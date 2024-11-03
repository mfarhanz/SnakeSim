import os
import queue
import math
import random
import multiprocessing
import tkinter as tk
import tkinter.font as tk_font

from .util.sim_global import *
from .util.sim_logic_wrapper import *
from .util.sim_wrappers import SimWrappers
from .util.common import Common, AppException, Tuple
from .widget.tooltip import ToolTip
from .widget.custom_button import CustomButton

class SnakeSim:
    def __init__(self, config: SimConfig, state: SimState, presets: SimData, core: SimCore):
        self.root = None
        self.canvas = None
        self.widgets = None
        self.message_queue = None
        self.visualizer_thread = None
        self.config = config
        self.state = state
        self.data = presets
        self.core = core
        self.init_buffers()
        self.setup()
    
    def init_buffers(self):
        self.state.TARGET = [random.randrange(self.config.ROWS), random.randrange(self.config.COLS)]
        self.state.TILES = [[0 for _ in range(self.config.COLS)] for _ in range(self.config.ROWS)]
    
    def setup(self):
        self.root = tk.Tk(className="SnakeSim")
        self.root.title("SnakeSim")
        self.root.state('zoomed')
        self.root.minsize(self.config.MIN_WIDTH, self.config.MIN_HEIGHT)
        self.canvas = tk.Canvas(self.root, width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight(),
                                borderwidth=0, highlightthickness=0, cursor="tcross",
                                background=self.data.COLOR_SCHEME['canvas'][self.config.THEME])
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<1>", lambda event: event.widget.focus_set())
        self.canvas.bind("<Configure>", lambda _: self._on_canvas_resize())
        self.canvas.bind("<B1-Motion>", self._mouse_event_handler)
        self.canvas.bind("<B3-Motion>", self._mouse_event_handler)
        self.canvas.bind("<B2-Motion>", self._mouse_event_handler)
        
        self.update_cell_size()

        self.state.FRAMES = []
        scanline_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'filter', 'scanline_h')
        for filename in os.listdir(scanline_dir):
            if filename.endswith('.png'):
                image_path = os.path.join(scanline_dir, filename)
                image = tk.PhotoImage(file=image_path)
                self.state.FRAMES.append(image)
        for frame in self.state.FRAMES:
            frame_id = self.canvas.create_image(0, 0, image=frame, anchor=tk.NW, tags="filter")
            self.state.FRAME_ID.append(frame_id)
        # Create buttons
        buttons = [
            CustomButton(text=self.data.WIDGET_ICONS["reset-snake"], name="reset-snake", command=self.reset_snake),
            CustomButton(text=self.data.WIDGET_ICONS["reset-map"], name="reset-map", command=self.reset_map),
            CustomButton(text=self.data.WIDGET_ICONS["step"], name="step", command=self._step),
            CustomButton(text=self.data.WIDGET_ICONS["run"], name="run", command=self._run),
            CustomButton(text=self.data.WIDGET_ICONS["theme"], name="theme", command=self.set_theme),
            CustomButton(text=self.data.WIDGET_ICONS["dynamic-wall"], name="dynamic-wall", command=self._toggle_dynamic_wall),
            CustomButton(text=self.data.WIDGET_ICONS['wraparound'], name="wraparound", command=self.toggle_wraparound),
            CustomButton(text=self.data.WIDGET_ICONS['cardinal_movement'], name="cardinal_movement", command=self.toggle_directional_movement),
            CustomButton(text=self.data.WIDGET_ICONS['bidirectional'], name="bidirectional", command=self.toggle_bidirectional_pathfinding),
            CustomButton(text=self.data.WIDGET_ICONS["gen-maze"], name="gen-maze", command=self._gen_maze),
            CustomButton(text=self.data.WIDGET_ICONS["crt-mode"], name="crt-mode", command=self.toggle_crt_mode),
            CustomButton(text=self.data.WIDGET_ICONS["play-snake"], name="play-snake", command=self._toggle_snake_game),
            CustomButton(text=self.data.WIDGET_ICONS["snake-chase"], name="snake-chase", command=self._toggle_snake_chase),
            CustomButton(text=self.data.WIDGET_ICONS["find-holes"], name="find-holes", command=self._display_holes_in_map),
            CustomButton(text=self.data.WIDGET_ICONS["make-connected"], name="make-connected", command=lambda: self._update_map(1)),
            CustomButton(text=self.data.WIDGET_ICONS["make-open"], name="make-open", command=lambda: self._update_map(2)),
            CustomButton(text=self.data.WIDGET_ICONS["visualizer"], name="visualizer", command=self._toggle_visualizer),
            CustomButton(text=self.data.WIDGET_ICONS['help'], name="help", cursor="question_arrow", command=self._show_help),
            CustomButton(text=self.data.WIDGET_ICONS['about'], name="about", command=self._show_about)
        ]
        for button in buttons:
            button.pack()  # Adjust layout as necessary
        # Create scales/spinners
        delay_label = tk.StringVar(value=self.data.WIDGET_ICONS['delay'])
        slider1 = tk.Scale(label=self.data.WIDGET_ICONS['set-wall'], name="set-wall", orient=tk.HORIZONTAL, cursor="sb_h_double_arrow", command=self._set_wall_width)
        slider2 = tk.Scale(label=self.data.WIDGET_ICONS['maze-size'], name="maze-size", orient=tk.HORIZONTAL, cursor="sb_h_double_arrow", command=self._set_maze_size)
        spinner1 = tk.Spinbox(name="delay", command=(self.root.register(lambda cmd: self._set_speed(cmd, spinner1)), '%d'), textvariable=delay_label)
        slider2.set(1)
        # Create dropdowns
        algo_label = tk.StringVar()
        algo_label.set('Random Walk')
        algo_label.trace("w", lambda *_: self._on_label_change(algo_label, 1))
        metric_label = tk.StringVar()
        metric_label.set('Chebyshev')
        metric_label.trace("w", lambda *_: self._on_label_change(metric_label, 2))
        maze_label = tk.StringVar()
        maze_label.set('Simple Random')
        maze_label.trace("w", lambda *_: self._on_label_change(maze_label, 3))
        dropdown1 = tk.OptionMenu(self.root, algo_label, 'Random Walk')
        dropdown_menu = tk.Menu(dropdown1, name="pathfinding")
        for option in self.data.PATHFINDING_ALGOS:
            dropdown_menu.add_radiobutton(label=option, variable=algo_label, value=option,
                                          font=tk_font.Font(family=tk_font.families()[self.config.FONT_INDEX], size=13))
        dropdown1.bind("<FocusIn>", lambda event: event.widget.master.focus_set())
        dropdown1.configure(menu=dropdown_menu)
        dropdown2 = tk.OptionMenu(self.root, metric_label, 'Chebyshev')
        dropdown_menu2 = tk.Menu(dropdown2, name="heuristic")
        for option in self.data.DISTANCE_METRICS:
            dropdown_menu2.add_radiobutton(label=option, variable=metric_label, value=option,
                                          font=tk_font.Font(family=tk_font.families()[self.config.FONT_INDEX], size=13))
        dropdown2.bind("<FocusIn>", lambda event: event.widget.master.focus_set())
        dropdown2.configure(menu=dropdown_menu2)
        dropdown3 = tk.OptionMenu(self.root, maze_label, 'Simple Random')
        dropdown_menu3 = tk.Menu(dropdown3, name="maze-choice")
        for option in self.data.MAZE_GENERATION_ALGOS:
            dropdown_menu3.add_radiobutton(label=option, variable=maze_label, value=option,
                                           font=tk_font.Font(family=tk_font.families()[self.config.FONT_INDEX], size=13))
        dropdown3.bind("<FocusIn>", lambda event: event.widget.master.focus_set())
        dropdown3.configure(menu=dropdown_menu3)
        # Create textboxes
        help_text = tk.Text(self.root, cursor="arrow")
        help_text.insert(tk.END, self.data.HELP_INFO)
        help_text.bind("<Button-1>", self._highlight_button_in_help)
        # Create panels from frames and labels
        about_panel = tk.Frame(self.canvas, cursor="arrow")
        about_title = tk.Label(about_panel, name="title", text=f"\U0001F40D SnakeSim")
        about_title.pack(pady=5)
        about_version = tk.Label(about_panel, name="version", text="v1.1")
        about_version.pack()
        about_powered = tk.Label(about_panel, name="python-powered", text="Python Powered")
        about_powered.pack()
        about_dev = tk.Label(about_panel,  name="developer", text="developed by deethree\n(github.com/mfarhanz)")
        about_dev.pack(pady=5)
        # Cache all widgets
        self.widgets = {
            "buttons": [*buttons],
            "sliders": [slider1, slider2],
            "spinners": [spinner1],
            "dropdowns": [(dropdown_menu, dropdown1), (dropdown_menu2, dropdown2), (dropdown_menu3, dropdown3)],
            "textbox": [help_text],
            "panels": [(about_panel, (about_title, about_powered, about_version, about_dev))],
            "tooltips": []
        }
        # Create tooltips
        for group_name, widget_group in list(self.widgets.items())[:-1]:
            for widget in widget_group:
                check = group_name in ['dropdowns', 'panels']
                args = (self.config.THEME, self.config.FONT_INDEX, self.data.COLOR_SCHEME['wid_bg'][self.config.THEME],
                        self.data.COLOR_SCHEME['wid_fg'][self.config.THEME])
                if check:
                    if widget[0].winfo_name() in self.data.TOOLTIPS:
                        self.widgets["tooltips"].append(ToolTip(self.root, widget[1], self.data.TOOLTIPS[widget[0].winfo_name()], *args))
                else:
                    if widget.winfo_name() in self.data.TOOLTIPS:
                        self.widgets["tooltips"].append(ToolTip(self.root, widget, self.data.TOOLTIPS[widget.winfo_name()], *args))
        # Configure all
        self.config_widgets()
        self.set_theme()
        # Assign positions (ugly, i know)
        self.canvas.create_window(10, 10, anchor="nw", window=buttons[0], tags="reset-snake")
        self.canvas.create_window(buttons[0].winfo_reqwidth() + 20, 10, anchor="nw", window=buttons[1], tags="reset-map")
        self.canvas.create_window(buttons[0].winfo_reqwidth() * 2 + 30, 10, anchor="nw", window=buttons[2], tags="step")
        self.canvas.create_window(buttons[0].winfo_reqwidth() * 3 + 40, 10, anchor="nw", window=buttons[3], tags="run")
        self.canvas.create_window(buttons[0].winfo_reqwidth() * 4 + 50, 17, anchor="nw", window=spinner1, tags="delay")
        self.canvas.create_window(buttons[0].winfo_reqwidth() * 6 + 50, 7, anchor="nw", window=slider1, tags="set-wall")
        self.canvas.create_window(buttons[0].winfo_reqwidth() * 8 + 70, 7, anchor="nw", window=slider2, tags="maze-size")
        self.canvas.create_window(buttons[0].winfo_reqwidth() * 10 + 90, 22, anchor="nw", window=dropdown3, tags="maze-choice")
        self.canvas.create_window(buttons[0].winfo_reqwidth() * 14 + 110, 22, anchor="nw", window=dropdown1, tags="pathfinding")
        self.canvas.create_window(buttons[0].winfo_reqwidth() * 18 + 130, 22, anchor="nw", window=dropdown2, tags="heuristic")
        # these buttons are dynamically positioned on the right side
        # whenever canvas is resized, so don't need to be placed exactly
        for button in self.widgets["buttons"][4:]:
            self.canvas.create_window(0, 0, anchor="nw", window=button, tags=button.winfo_name())
        self._start_animation()
        self.message_queue = queue.Queue()
        self._pulse_button(button_id='help', pulse=True)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def config_widgets(self):
        """
        Configures widgets used in app.

        :return:
        """
        for group_name, widgets in self.widgets.items():
            for widget in widgets:
                if group_name == "buttons":
                    widget.configure(borderwidth=2, width=2, activeforeground="cyan", relief="flat",
                                     overrelief="raised",
                                     font=tk_font.Font(family=tk_font.families()[self.config.FONT_INDEX], size=18, weight='bold'))
                elif group_name == "spinners":
                    widget.configure(borderwidth=0, width=3, justify="center",
                                     font=tk_font.Font(family=tk_font.families()[self.config.FONT_INDEX], size=20, weight='bold'))
                elif group_name == "sliders":
                    widget.configure(from_=1, to=6, orient="horizontal", showvalue=False, length=100,
                                     highlightthickness=0,
                                     font=tk_font.Font(family=tk_font.families()[self.config.FONT_INDEX], size=16, weight='bold'))
                elif group_name == "dropdowns":
                    widget[1].configure(borderwidth=1, width=14, highlightthickness=0, indicatoron=False,
                                        relief="groove",
                                        font=tk_font.Font(family=tk_font.families()[self.config.FONT_INDEX], size=13, weight='bold'))
                    widget[0].configure(borderwidth=0, relief='flat', tearoff=0, activeborderwidth=0)
                elif group_name == "textbox":
                    widget.configure(borderwidth=5, padx=15, pady=15, wrap="word", relief="groove", width=50,
                                     font=tk_font.Font(family=tk_font.families()[self.config.FONT_INDEX], size=16, weight='bold'))
                elif group_name == "panels":
                    title_font = tk_font.Font(family=tk_font.families()[self.config.FONT_INDEX], size=24, weight='bold')
                    body_font = tk_font.Font(family=tk_font.families()[self.config.FONT_INDEX], size=12)
                    widget[0].configure(borderwidth=3, padx=15, pady=15, relief="groove")
                    widget[1][0].configure(font=title_font)
                    for label in widget[1][1:]:
                        label.configure(font=body_font)

    def set_theme(self):
        """
        Update and alternate between simulator themes.

        :return:
        """
        self.config.THEME = -~self.config.THEME % len(self.data.COLOR_SCHEME['canvas'])
        self.canvas.configure(background=self.data.COLOR_SCHEME['canvas'][self.config.THEME])
        for group_name, widgets in self.widgets.items():
            for widget in widgets:
                if group_name == "buttons":
                    widget.configure(activebackground=self.data.COLOR_SCHEME['btn_act_bg'][self.config.THEME],
                                     background=self.data.COLOR_SCHEME['wid_bg'][self.config.THEME],
                                     foreground=self.data.COLOR_SCHEME['w_fill'][
                                         self.config.THEME] if widget.winfo_name() == "reset-map"
                                     else self.data.COLOR_SCHEME['h_fill'][self.config.THEME] if widget.winfo_name() in [
                                         "play-snake", "snake-chase", "dynamic-wall", "bidirectional", "visualizer", "help", "about"]
                                     else self.data.COLOR_SCHEME['wid_fg'][self.config.THEME])
                elif group_name == "spinners":
                    widget.configure(background=self.data.COLOR_SCHEME['wid_bg'][self.config.THEME],
                                     foreground=self.data.COLOR_SCHEME['wid_fg'][self.config.THEME],
                                     buttonbackground=self.data.COLOR_SCHEME['wid_bg'][self.config.THEME])
                elif group_name == "sliders":
                    widget.configure(activebackground=self.data.COLOR_SCHEME['wid_fg'][self.config.THEME],
                                     background=self.data.COLOR_SCHEME['wid_bg'][self.config.THEME],
                                     foreground=self.data.COLOR_SCHEME['wid_fg'][self.config.THEME],
                                     troughcolor=self.data.COLOR_SCHEME['wid_bg'][self.config.THEME])
                elif group_name == "tooltips":
                    widget.tooltip_bg = self.data.COLOR_SCHEME['wid_bg'][self.config.THEME]
                    widget.tooltip_fg = self.data.COLOR_SCHEME['wid_fg'][self.config.THEME]
                elif group_name == "textbox":
                    widget.configure(background=self.data.COLOR_SCHEME['wid_bg'][self.config.THEME],
                                     foreground=self.data.COLOR_SCHEME['wid_fg'][self.config.THEME])
                elif group_name == "panels":
                    widget[0].configure(background=self.data.COLOR_SCHEME['wid_bg'][self.config.THEME])
                    for label in widget[1]:
                        label.configure(background=self.data.COLOR_SCHEME['wid_bg'][self.config.THEME],
                                            foreground=self.data.COLOR_SCHEME['wid_fg'][self.config.THEME])
                elif group_name == "dropdowns":
                    widget[1].configure(background=self.data.COLOR_SCHEME['wid_bg'][self.config.THEME],
                                        foreground=self.data.COLOR_SCHEME['wid_fg'][self.config.THEME],
                                        activeforeground=self.data.COLOR_SCHEME['b_fill'][self.config.THEME],
                                        activebackground=self.data.COLOR_SCHEME['btn_act_bg'][self.config.THEME])
                    widget[0].configure(background=self.data.COLOR_SCHEME['wid_bg'][self.config.THEME],
                                        activebackground=self.data.COLOR_SCHEME['btn_act_bg'][self.config.THEME])
                    for index in range(widget[0].index("end") + 1):
                        widget[0].entryconfigure(index, background=self.data.COLOR_SCHEME['wid_bg'][self.config.THEME],
                                                 foreground=self.data.COLOR_SCHEME['h_fill'][self.config.THEME],
                                                 activebackground=self.data.COLOR_SCHEME['btn_act_bg'][
                                                     self.config.THEME],
                                                 activeforeground=self.data.COLOR_SCHEME['wid_fg'][self.config.THEME],
                                                 selectcolor=self.data.COLOR_SCHEME['h_fill'][self.config.THEME])
    
    def _start_animation(self):
        self.state.FILTER_WORKER = Thread(target=self._filter_playback, args=(0,), daemon=True)
        self.state.FILTER_WORKER.start()

    def _on_canvas_resize(self):
        self.update_cell_size()
        bottom_padding = 10
        for button in self.widgets["buttons"][4:]:
            self.canvas.coords(button.winfo_name(), self.canvas.winfo_width() - self.widgets['buttons'][4].winfo_reqwidth() - 10, bottom_padding)
            bottom_padding += 50
        if not self._get_button('reset-map').pulse:
            self._pulse_button(button_id='reset-map', pulse=True)
        if not self._get_button('reset-snake').pulse:
            self._pulse_button(button_id='reset-snake', pulse=True)

    def _on_move_key_release(self, _):
        self.state.KEY_PRESSED = False
        self.root.bind('<KeyPress-w>', lambda _: self._move_callback_wrapper(2, (True, False)[self.state.SNAKE_GAME]))
        self.root.bind('<KeyPress-a>', lambda _: self._move_callback_wrapper(-1, (True, False)[self.state.SNAKE_GAME]))
        self.root.bind('<KeyPress-s>', lambda _: self._move_callback_wrapper(-2, (True, False)[self.state.SNAKE_GAME]))
        self.root.bind('<KeyPress-d>', lambda _: self._move_callback_wrapper(1, (True, False)[self.state.SNAKE_GAME]))

    def _on_label_change(self, var, var_id):
        """
        Update selected algorithm/heuristic to selected dropdown option's id.
        
        :param var: String label variable
        :param var_id: Label id
        :return:
        """
        if var_id == 1:     # pathfinding label
            pathfinding = var.get().lower()
            self.config.ALGO =  0 if pathfinding == 'random walk' else \
                                1 if pathfinding == 'depth first' else \
                                2 if pathfinding == 'breadth first' else \
                                3 if pathfinding == 'dijkstra' else \
                                4 if pathfinding == 'a*' else \
                                5 if pathfinding == 'greedy best first' else \
                                6 if pathfinding == 'fringe' else \
                                7 if pathfinding == 'bellman-ford' else \
                                8 if pathfinding == 'iterative deepening a*' else 9
        elif var_id == 2:   # distance metric label
            metric = var.get().lower()
            self.config.HEURISTIC = 0 if metric == 'chebyshev' else \
                                    1 if metric == 'manhattan' else \
                                    2 if metric == 'euclidean' else \
                                    3 if metric == 'octile' else 4  # (hamming)
        elif var_id == 3:   # maze label
            maze = var.get().lower()
            self.config.MAZE_ALGO = 0 if maze == 'simple random' else \
                                    1 if maze == 'diagonal random' else \
                                    2 if maze == 'dungeon rooms' else \
                                    3 if maze == 'dfs maze' else \
                                    4 if maze == 'recursive division' else \
                                    5 if maze == 'cell opening' else 6
                                    # 6 if maze == 'iterative prims' else 7     # TBD later

    def _on_close(self):
        """
        Cleanup before exiting application.
        """
        self.state.FILTER_WORKER_STATUS = False
        self.state.FILTER_WORKER.join()
        self.root.destroy()
    
    @staticmethod
    def _call_and_save(func, *args, **kwargs):
        q = kwargs.pop('queue')
        result = func(*args, **kwargs)
        q.put(result)

    @SimWrappers.show_loading
    def _call_with_notification(self, func, *args, callback=None, callback_args=None):
        func(*args)

    def _call_with_timeout(self, func, *args, **kwargs):
        timeout = 5         # time limit of 5 seconds for given function
        q = multiprocessing.Queue()
        kwargs['queue'] = q
        process = multiprocessing.Process(target=self._call_and_save, args=(func, *args), kwargs=kwargs)
        process.start()
        process.join(timeout)
        if process.is_alive():
            self.show_message("Operation timed out :(")
            process.terminate()
            process.join()
            return None
        res = q.get()
        return res
    
    def _await_for_timer(self, timer_call, *args, **kwargs):
        if kwargs:
            all_args = (*args, kwargs)
        else:
            all_args = args
        if timer_call() is not None:
            self.root.after(50, self._await_for_timer, timer_call, *all_args)
        else:
            args = all_args[:-1]
            kwargs = all_args[-1]
            if 'func' in kwargs:
                func = kwargs.pop('func')
                func(*args, **kwargs)
    
    def _move_callback_wrapper(self, direction, repeat=False):
        self.state.KEY_PRESSED = True
        if direction == -1:
            self.root.unbind('<KeyPress-a>')
        elif direction == 1:
            self.root.unbind('<KeyPress-d>')
        elif direction == 2:
            self.root.unbind('<KeyPress-w>')
        else:
            self.root.unbind('<KeyPress-s>')
        self._move_in_game(direction, repeat)

    # not sure if wrapper needed...
    @SimWrappers.call_safe
    def _mouse_event_handler(self, event):
        """
        Draw or erase on canvas on user interaction.

        :param event: Current mouse event
        :return:
        """
        canvas_x = self.canvas.winfo_rootx()
        canvas_y = self.canvas.winfo_rooty()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_x <= event.x_root <= canvas_x + canvas_width and canvas_y <= event.y_root <= canvas_y + canvas_height:
            col = event.x // self.config.COL_WIDTH
            row = event.y // self.config.ROW_HEIGHT
            if not self.state.TILES[row][col]:
                # if event.state == 0x0100:  # LMB hit
                if 200 < event.state < 300:  # LMB hit
                    if self.state.HEAD.count(None) == len(self.state.HEAD):
                        self.state.TILES[row][col] = self.canvas.create_rectangle(col * self.config.COL_WIDTH, row * self.config.ROW_HEIGHT,
                                                                                  (col + 1) * self.config.COL_WIDTH, (row + 1) * self.config.ROW_HEIGHT,
                                                                                  fill=self.data.COLOR_SCHEME['h_fill'][self.config.THEME],
                                                                                  tags=["snek"], stipple='gray75')
                        self.state.SNAKE[self.state.TILES[row][col]] = [row, col]
                        self.state.PREV[:] = self.state.CURR
                        self.state.CURR[:] = row, col
                        self.state.HEAD[:] = row, col
                    elif (row, col) in Common.valid_moves(self.state.CURR[0], self.state.CURR[1], self.config.ROWS, self.config.COLS):
                        if any(self.state.TILES[coord[0]][coord[1]] != 0 for coord in Common.valid_moves(row, col, self.config.ROWS, self.config.COLS)
                               if 0 <= coord[0] < self.config.ROWS and 0 <= coord[1] < self.config.COLS):
                            self.state.TILES[row][col] = self.canvas.create_rectangle(col * self.config.COL_WIDTH, row * self.config.ROW_HEIGHT,
                                                                                      (col + 1) * self.config.COL_WIDTH, (row + 1) * self.config.ROW_HEIGHT,
                                                                                      fill=self.data.COLOR_SCHEME['b_fill'][self.config.THEME],
                                                                                      tags="snek", stipple='gray75')
                            self.state.SNAKE[self.state.TILES[row][col]] = [row, col]
                            self.state.PREV[:] = self.state.CURR
                            self.state.CURR[:] = row, col
                # elif event.state == 0x0400:  # RMB hit
                elif 1000 < event.state < 1100:  # RMB hit
                    self._create_block(row, col, self.config.COL_WIDTH, self.config.ROW_HEIGHT, self.state.MAZE_DYN)
            # if event.state == 0x0200:   # Middle button hit
            if 500 < event.state < 600:   # Middle button hit
                if [row, col] not in self.state.SNAKE.values():
                    self.canvas.delete(self.state.TILES[row][col])
                    self.state.TILES[row][col] = 0

    def _handle_game_exception(self, message_key):
        """
        Notify user of runtime exception by display corresponding error message for exception.
        
        :param message_key:
        :return:
        """
        self._stop('sim')
        self.show_message(random.choice(self.data.MESSAGES[message_key]))
        self._pulse_button(button_id='reset-snake', pulse=True)
    
    def _filter_playback(self, n):
        """
        Displays frames of the filter (CRT effect) once.

        :param n: current frame
        :return:
        """
        if not self.state.FRAMES:
            return
        if self.state.FILTER_WORKER_STATUS:
            if n < len(self.state.FRAMES):
                self.canvas.itemconfigure(self.state.FRAME_ID[(n-1) % len(self.state.FRAMES)], state=tk.HIDDEN)
                self.canvas.itemconfigure(self.state.FRAME_ID[n], state=tk.NORMAL)
                self.canvas.tag_raise(self.state.FRAME_ID[n])
                n = n + 1 if n != len(self.state.FRAMES) - 1 else 0
                # self.widgets['buttons'][2].configure(command=lambda: self.step(thd))      # why did i put this here?
                self.root.after(self.config.FRAME_DELAY, self._filter_playback, n)

    def _toggle_movement_bindings(self, toggle, continuous=False):
        if toggle:
            self.root.bind('<KeyPress-w>', lambda _: self._move_callback_wrapper(2, continuous))
            self.root.bind('<KeyRelease-w>', self._on_move_key_release)
            self.root.bind('<KeyPress-a>', lambda _: self._move_callback_wrapper(-1, continuous))
            self.root.bind('<KeyRelease-a>', self._on_move_key_release)
            self.root.bind('<KeyPress-s>', lambda _: self._move_callback_wrapper(-2, continuous))
            self.root.bind('<KeyRelease-s>', self._on_move_key_release)
            self.root.bind('<KeyPress-d>', lambda _: self._move_callback_wrapper(1, continuous))
            self.root.bind('<KeyRelease-d>', self._on_move_key_release)
        else:
            self.root.unbind('<KeyPress-w>')
            self.root.unbind('<KeyRelease-w>')
            self.root.unbind('<KeyPress-a>')
            self.root.unbind('<KeyRelease-a>')
            self.root.unbind('<KeyPress-s>')
            self.root.unbind('<KeyRelease-s>')
            self.root.unbind('<KeyPress-d>')
            self.root.unbind('<KeyRelease-d>')

    @SimWrappers.call_safe
    def toggle_crt_mode(self):
        """
        Toggles CRT effect (scanlines).

        :return:
        """
        self.state.FILTER_WORKER_STATUS = not self.state.FILTER_WORKER_STATUS
        button = self._get_button('crt-mode')
        if not self.state.FILTER_WORKER_STATUS:
            button.configure(foreground=self.data.COLOR_SCHEME['h_fill'][self.config.THEME], relief="flat")
            self.state.FILTER_WORKER.join()
            items = self.canvas.find_withtag("filter")
            for item in items:
                self.canvas.itemconfigure(item, state=tk.HIDDEN)
        else:
            button.configure(foreground=self.data.COLOR_SCHEME['wid_fg'][self.config.THEME], relief="sunken")
            self.state.FILTER_WORKER = Thread(target=self._filter_playback, args=(0,), daemon=True)
            self.state.FILTER_WORKER.start()

    @SimWrappers.call_safe
    def _toggle_snake_chase(self):
        """
        Enable/disable playing the Snake Chase game.
        
        :return:
        """
        self.state.SNAKE_CHASING = not self.state.SNAKE_CHASING
        self._stop("sim", thd=self.state.SIM_CALLBACK)
        if self.state.SNAKE_GAME:
            self.state.SNAKE_GAME = not self.state.SNAKE_GAME
            self._get_button('play-snake').configure(foreground=self.data.COLOR_SCHEME['h_fill'][self.config.THEME], relief="flat")
        else:
            self.widgets["dropdowns"][0][1].configure(state="normal")
        if self.state.SNAKE_CHASING:
            self._get_button('snake-chase').configure(foreground=self.data.COLOR_SCHEME['wid_fg'][self.config.THEME], relief="sunken")
            self.show_message(random.choice(self.data.MESSAGES["chase_game"]))
            self._get_button('play-snake').configure(state="disabled")
            self._get_button('snake-chase').configure(state="disabled")
            self.root.after(3000, lambda: self._game_count_down(4))
        else:
            self._toggle_movement_bindings(False)
            self._get_button('snake-chase').configure(foreground=self.data.COLOR_SCHEME['h_fill'][self.config.THEME], relief="flat")

    @SimWrappers.call_safe
    def _toggle_snake_game(self):
        """
        Enable/disable playing the classic Snake game.
        
        :return:
        """
        self.state.SNAKE_GAME = not self.state.SNAKE_GAME
        self._stop("sim", thd=self.state.SIM_CALLBACK)
        if self.state.SNAKE_CHASING:
            self.state.SNAKE_CHASING = not self.state.SNAKE_CHASING
            self._get_button('snake-chase').configure(foreground=self.data.COLOR_SCHEME['h_fill'][self.config.THEME], relief="flat")
        else:
            self.widgets["dropdowns"][0][1].configure(state="normal")
        if self.state.SNAKE_GAME:
            self._get_button('play-snake').configure(foreground=self.data.COLOR_SCHEME['wid_fg'][self.config.THEME], relief="sunken")
            self.show_message(random.choice(self.data.MESSAGES["snake_game"]))
            self._get_button('play-snake').configure(state="disabled")
            self._get_button('snake-chase').configure(state="disabled")
            self.root.after(3000, lambda: self._game_count_down(4))
        else:
            self._toggle_movement_bindings(False)
            self._get_button('play-snake').configure(foreground=self.data.COLOR_SCHEME['h_fill'][self.config.THEME], relief="flat")

    def _toggle_dynamic_wall(self):
        """
        Toggles drawing walls of random width instead of a set width.

        :return:
        """
        self.state.MAZE_DYN = not self.state.MAZE_DYN
        fg_color = self.data.COLOR_SCHEME['wid_fg' if self.state.MAZE_DYN else 'h_fill'][self.config.THEME]
        self._get_button('dynamic-wall').configure(foreground=fg_color, relief="sunken" if self.state.MAZE_DYN else "flat")
        self.widgets["sliders"][0].config(state=("normal", "disabled")[self.state.MAZE_DYN],
                                          foreground=(self.data.COLOR_SCHEME['wid_fg'][self.config.THEME], '#6D6D6B')[self.state.MAZE_DYN])

    def toggle_wraparound(self):
        """
        Enable/disable mirrored wrapping around map border.
        
        :return:
        """
        self.config.WRAPAROUND = not self.config.WRAPAROUND
        fg_color = self.data.COLOR_SCHEME['wid_fg' if self.config.WRAPAROUND else 'h_fill'][self.config.THEME]
        self._get_button('wraparound').configure(foreground=fg_color, relief="sunken" if self.config.WRAPAROUND else "flat")

    def toggle_directional_movement(self):
        """
        Toggle between 4-directional or 8-directional movement for the snake.
        
        :return:
        """
        self.config.EIGHT_DIRECTIONAL = not self.config.EIGHT_DIRECTIONAL
        fg_color = self.data.COLOR_SCHEME['wid_fg' if self.config.EIGHT_DIRECTIONAL else 'h_fill'][self.config.THEME]
        self._get_button('cardinal_movement').configure(foreground=fg_color, relief="sunken" if self.config.EIGHT_DIRECTIONAL else "flat")
    
    def toggle_bidirectional_pathfinding(self):
        """
        Enable/disable bidirectional pathfinding.
        
        :return:
        """
        self.config.BIDIRECTIONAL = not self.config.BIDIRECTIONAL
        fg_color = self.data.COLOR_SCHEME['wid_fg' if self.config.BIDIRECTIONAL else 'h_fill'][self.config.THEME]
        self._get_button('bidirectional').configure(foreground=fg_color, relief="sunken" if self.config.BIDIRECTIONAL else "flat")
    
    def _toggle_visualizer(self):
        """
        Enable/disable visualizing.
        
        :return:
        """
        self._stop_visualizer_callback()
        self.config.VISUALIZE = not self.config.VISUALIZE
        fg_color = self.data.COLOR_SCHEME['wid_fg' if self.config.VISUALIZE else 'h_fill'][self.config.THEME]
        self._get_button('visualizer').configure(foreground=fg_color, relief="sunken" if self.config.VISUALIZE else "flat")
    
    def _stop_visualizer_callback(self):
        """
        Stops the visualizer callback timer.
        
        :return:
        """
        if self.state.VISUALIZER_CALLBACK:
            self.root.after_cancel(self.state.VISUALIZER_CALLBACK)
        self.canvas.delete('highlight')
        self.state.VISUALIZER_CALLBACK = None
        self._disable_active_visualizer_button()
    
    @SimWrappers.call_safe
    def _game_count_down(self, x):
        """
        Show a countdown before starting a sim/game run.
        
        :param x:
        :return:
        """
        if x == 0:
            self._get_button('play-snake').configure(state="normal")
            self._get_button('snake-chase').configure(state="normal")
            self.widgets["dropdowns"][0][1].configure(state="disabled")
            if self.state.SNAKE_GAME or self.state.SNAKE_CHASING:
                self._toggle_movement_bindings(False)
                if self.state.SNAKE_GAME:
                    self._toggle_movement_bindings(True)
                elif self.state.SNAKE_CHASING:
                    self._toggle_movement_bindings(True, True)
                self._run()
                return
        self.show_message(f"{x}")
        self.root.after(600, lambda: self._game_count_down(x - 1))

    @SimWrappers.call_safe
    def _move_in_game(self, direction, repeat):
        """
        Callback that manages the current direction/movement of the snake/target.
        
        :param direction:
        :param repeat:
        :return:
        """
        def change_direction():
            if self.state.LAST_DIRECTION_IN_GAME[0] is None or self.state.LAST_DIRECTION_IN_GAME[1] is None:
                self.state.LAST_DIRECTION_IN_GAME[:] = self.state.CURRENT_DIRECTION_IN_GAME
            if direction == -1:
                self.state.CURRENT_DIRECTION_IN_GAME[:] = [0, -1]
            elif direction == 1:
                self.state.CURRENT_DIRECTION_IN_GAME[:] = [0, 1]
            elif direction == 2:
                self.state.CURRENT_DIRECTION_IN_GAME[:] = [-1, 0]
            else:
                self.state.CURRENT_DIRECTION_IN_GAME[:] = [1, 0]
    
        if repeat:
            if self.state.KEY_PRESSED:
                if self.state.HEAD != self.state.TARGET:
                    change_direction()
                    adjusted = Common.diagonal_adjusted(self.state.TARGET[0], self.state.TARGET[1], self.state.TARGET[0] + self.state.CURRENT_DIRECTION_IN_GAME[0],
                                                        self.state.TARGET[1] + self.state.CURRENT_DIRECTION_IN_GAME[1], self.config.ROWS, self.config.COLS)
                    next_move = [adjusted[0], adjusted[1]]
                    if self.state.TILES[next_move[0]][next_move[1]] == 0:
                        self.state.TARGET[:] = next_move
                        self.canvas.delete("target")
                        self.canvas.create_rectangle(self.state.TARGET[1] * self.config.COL_WIDTH, self.state.TARGET[0] * self.config.ROW_HEIGHT,
                                                     (self.state.TARGET[1] + 1) * self.config.COL_WIDTH, (self.state.TARGET[0] + 1) * self.config.ROW_HEIGHT,
                                                     fill='orange', tags="target")
                if self.state.MOVING_CALLBACK:
                    self.root.after_cancel(self.state.MOVING_CALLBACK)
                self.state.MOVING_CALLBACK = self.root.after(self.config.DELAY - self.config.MIN_CHASE_DELAY if self.config.DELAY <= 80 else 70, self._move_in_game, direction, repeat)
        else:
            change_direction()
    
    def _show_about(self):
        """
        Display/hide the About window.
        :return:
        """
        button = self._get_button('about')
        if self.widgets["panels"][0][0].winfo_viewable():
            self.canvas.delete("about_window")
            button.configure(foreground=self.data.COLOR_SCHEME['h_fill'][self.config.THEME], relief="flat")
        else:
            x, y = self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2
            self.canvas.create_window(x, y, window=self.widgets["panels"][0][0], tags="about_window")
            button.configure(foreground=self.data.COLOR_SCHEME['wid_fg'][self.config.THEME], relief="sunken")
    
    def _show_help(self):
        """
        Display/hide the Help window.
        
        :return:
        """
        button = self._get_button('help')
        if button.pulse:
            button.pulse = False
        if self.widgets["textbox"][0].winfo_viewable():
            self.canvas.delete("help_window")
            for btn in self.widgets["buttons"]:
                self._pulse_button(button=btn, pulse=False)
            button.configure(foreground=self.data.COLOR_SCHEME['h_fill'][self.config.THEME], relief="flat")
        else:
            x, y = self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2
            self.canvas.create_window(x, y, window=self.widgets["textbox"][0], tags="help_window")
            button.configure(foreground=self.data.COLOR_SCHEME['wid_fg'][self.config.THEME], relief="sunken")

    @SimWrappers.call_safe
    def show_message(self, message):
        """
        Display a message at the bottom of the canvas.
        
        :param message:
        :return:
        """
        def get_next_message():
            if not self.message_queue.empty():
                mssg = self.message_queue.get()  # Get the next message
                self.canvas.delete("message")  # Clear previous message
                font = tk_font.Font(family=tk_font.families()[self.config.FONT_INDEX], size=18, weight='bold')
                self.canvas.create_text(font.measure(mssg) / 1.8, self.root.winfo_height() - 40, text=mssg, font=font,
                                        fill=self.data.COLOR_SCHEME['wid_fg'][self.config.THEME], tags="message")
                if self.message_queue.qsize() == 0:
                    self.state.MESSAGE_CALLBACK = self.root.after(3000, lambda: self.canvas.delete("message"))
                else:
                    self.state.MESSAGE_CALLBACK = self.root.after(500, get_next_message)

        self.message_queue.put(message)
        if self.state.MESSAGE_CALLBACK:
            self.root.after_cancel(self.state.MESSAGE_CALLBACK)
            self.state.MESSAGE_CALLBACK = None
        get_next_message()
    
    def _get_button(self, name):
        return next((btn for btn in self.widgets["buttons"] if btn.winfo_name() == name), None)
    
    def _pulse_button(self, button_id: str = None, button=None, pulse=False):
        """
        Start/stop pulsing a button.
        
        :param button_id:
        :param button:
        :param pulse:
        :return:
        """
        
        if button_id is not None:
            current_button = self._get_button(button_id)
            if pulse:
                if not current_button.pulse:
                    current_button.pulse = True
                # if not self.widgets["buttons"][button_id].pulse:
                #     self.widgets["buttons"][button_id].pulse = True
            else:
                if current_button.pulse:
                    current_button.pulse = False
                # if self.widgets["buttons"][button_id].pulse:
                #     self.widgets["buttons"][button_id].pulse = False
        elif button is not None:
            if pulse:
                if not button.pulse:
                    button.pulse = True
            else:
                if button.pulse:
                    button.pulse = False

    def _highlight_button_in_help(self, event):
        """
        Highlight button on clicking the corresponding button icon in the help window.
        
        :param event:
        :return:
        """
        # Get the index of the line where the click occurred
        index = self.widgets["textbox"][0].index("@{},{}".format(event.x, event.y))
        line_number = index.split('.')[0]  # Get the line number in help textbox
        line = self.widgets["textbox"][0].get(f"{line_number}.0", f"{line_number}.end").strip()  # Get the entire line
        for btn in self.widgets["buttons"]:
            self._pulse_button(button=btn, pulse=False)
        key = next((icon for icon in self.data.WIDGET_ICONS.values() if icon in line), None)
        if key:
            button = next((btn for btn in self.widgets["buttons"] if btn.cget('text') == key), None)
            if button:
                self._pulse_button(button=button, pulse=True)
    
    def _disable_active_visualizer_button(self):
        visualizing_button = next((button for button in self.widgets["buttons"] if button.pulse), None)
        if visualizing_button:
            self._pulse_button(button=visualizing_button, pulse=False)

    @SimWrappers.call_safe
    def _visualize_sections(self, sections, color, col_width, row_height):
        """
        Highlight the points in the given group/map sections with the corresponding group color on canvas,
        with a delay inbetween successive points.
        
        :param sections:
        :param color:
        :param col_width:
        :param row_height:
        :return:
        """
        def start_highlighting(next_point):
            nonlocal index
            try:
                point = next(next_point)
                if point not in [tuple(self.state.HEAD), tuple(self.state.TARGET)]:
                    self.canvas.create_rectangle(point[1] * col_width, point[0] * row_height, (point[1] + 1) * col_width,
                                                 (point[0] + 1) * row_height, tags=["highlight"], width=0,
                                                 fill=color if not multiple else color[index])
                self.state.VISUALIZER_CALLBACK = self.root.after(1, start_highlighting, next_point)
            except StopIteration:
                if multiple and index < len(sections)-1:
                    index += 1
                    self.state.VISUALIZER_CALLBACK = self.root.after(1, start_highlighting, iter(sections[index]))
                else:
                    self._disable_active_visualizer_button()
                    self.state.VISUALIZER_CALLBACK = None
                    return

        self.canvas.delete("highlight")
        index, self.state.VISUALIZER_CALLBACK = 0, 1   # this is  actually needed, it prevents root.after from finishing immediately elsewhere
        multiple = isinstance(sections[0][0], list) or isinstance(sections[0][0], tuple)
        next_point = iter(sections[index]) if multiple else iter(sections)
        self.visualizer_thread = Thread(target=lambda: start_highlighting(next_point), daemon=True)
        self.visualizer_thread.start()

    @SimWrappers.call_safe
    def _visualise_maze_in_place(self, coords, col_width, row_height, matrix=None):
        """
        Draw a point or a set of points from a given matrix or the global tile matrix on the canvas with a delay
        inbetween successive points.
        
        :param coords:
        :param col_width:
        :param row_height:
        :param matrix:
        :return:
        """
        def update_point(next_point=None):
            nonlocal index
            if not next_point:
                x, y = coords
                if self.state.TILES[x][y]:
                    self.canvas.delete(self.state.TILES[x][y])
                self.state.TILES[x][y] = self.canvas.create_rectangle(y * col_width, x * row_height, (y + 1) * col_width, (x + 1) * row_height,
                                                                      fill=self.data.COLOR_SCHEME['w_fill'][self.config.THEME], tags=["wall"], width=0)
            else:
                try:
                    x, y = next(next_point)
                    if index == 0:
                        self.state.TILES[x][y] = self.canvas.create_rectangle(y * col_width, x * row_height, (y + 1) * col_width, (x + 1) * row_height,
                                                                              fill=self.data.COLOR_SCHEME['w_fill'][self.config.THEME], tags=["wall"], width=0)
                    else:
                        self.canvas.delete(self.state.TILES[x][y])
                        if matrix[x][y]:
                            self.state.TILES[x][y] = self.canvas.create_rectangle(y * col_width, x * row_height, (y + 1) * col_width, (x + 1) * row_height,
                                                                                  fill=self.data.COLOR_SCHEME['w_fill'][self.config.THEME], tags=["wall"], width=0)
                        else:
                            self.state.TILES[x][y] = 0
                    self.state.VISUALIZER_CALLBACK = self.root.after(1, update_point, next_point)
                except StopIteration:
                    if multiple and index < len(coords) - 1:
                        index += 1
                        self.state.VISUALIZER_CALLBACK = self.root.after(1, update_point, iter(coords[index]))
                    else:
                        self.root.after_cancel(self.state.VISUALIZER_CALLBACK)
                        self._disable_active_visualizer_button()
                        self.state.VISUALIZER_CALLBACK = None

        if isinstance(coords[0], int):
            update_point()
        elif matrix:
            index = 0
            multiple = isinstance(coords[0][0], list) or isinstance(coords[0][0], tuple)
            point_generator = iter(coords[index]) if multiple else iter(coords)
            update_point(iter(point_generator))

    @SimWrappers.call_safe
    def _display_holes_in_map(self):
        """
        Highlight all closed spaces/holes on the map.
        
        :return:
        """
        if self.state.VISUALIZER_CALLBACK:
            self._stop_visualizer_callback()
            return
        points = []
        self._pulse_button(button_id='find-holes', pulse=True)
        self._call_with_notification(Common.get_closed_spaces, self.state.TILES, points, callback=self._visualize_sections,
                                     callback_args=(points, self.data.COLOR_SCHEME['highlight_space'][self.config.THEME],
                                                    self.config.COL_WIDTH, self.config.ROW_HEIGHT))

    def _set_maze_gen_algo(self, x):
        self.config.MAZE_ALGO = int(x)

    def _set_wall_width(self, x):
        """
        Updates wall width.

        :param x: Width
        :return:
        """
        self.config.WALL_WIDTH = int(x)
    
    def _set_maze_size(self, x):
        """
        Updates maze dimensions.

        :param x: Scaling factor
        :return:
        """
        self.config.ROWS, self.config.COLS = 30 * int(x), 60 * int(x)
        self.update_cell_size()
        self.reset_map()
        self.reset_snake()
        self.update_target()
        
    def _set_speed(self, cmd, spinner):
        """
        Adjust the snake's speed (delay between moving again).

        :param cmd:
        :param spinner: Reference to parent widget
        :return:
        """
        if cmd == "up":
            self.config.DELAY = self.config.DELAY + 20 if self.config.DELAY <= 1000 else self.config.DELAY
            if self.config.DELAY >= 1000:
                self.widgets['spinners'][0].configure(foreground="red")
                self.root.after(500, lambda: self.widgets['spinners'][0].configure(foreground=self.data.COLOR_SCHEME['wid_fg'][self.config.THEME]))
        else:
            self.config.DELAY = self.config.DELAY - 20 if self.config.DELAY > 20 else self.config.DELAY
            if self.config.DELAY <= 20:
                self.widgets['spinners'][0].configure(foreground="red")
                self.root.after(500, lambda: self.widgets['spinners'][0].configure(foreground=self.data.COLOR_SCHEME['wid_fg'][self.config.THEME]))
        spinner.config(value=str(self.config.DELAY))

    def update_cell_size(self):
        self.config.COL_WIDTH, self.config.ROW_HEIGHT = math.ceil(self.canvas.winfo_width() / self.config.COLS), math.ceil(self.canvas.winfo_height() / self.config.ROWS)

    @SimWrappers.call_safe
    def reset_snake(self):
        """
        Clears all tiles representing the snake from canvas.

        :return:
        """
        self.canvas.delete("snek", "target", "message")
        self.state.TILES[:] = [[0 if self.state.TILES[i][j] in self.state.SNAKE.keys() else self.state.TILES[i][j]
                                for j in range(self.config.COLS)] for i in range(self.config.ROWS)]
        self.state.ROUTING[:] = []
        self.state.HEAD[:] = [None, None]
        self.state.SNAKE.clear()
        self._pulse_button(button_id='reset-snake', pulse=False)

    @SimWrappers.call_safe
    def reset_map(self):
        """
        Clears all tiles representing walls from the map.

        :return:
        """
        self.canvas.delete("wall", "highlight")
        snake_tile_ids = [self.state.TILES[i][j] for i, j in self.state.SNAKE.values()]
        self.state.TILES[:] = [[0 for _ in range(self.config.COLS)] for _ in range(self.config.ROWS)]
        for sid in snake_tile_ids:
            tile = self.state.SNAKE[sid]
            self.state.TILES[tile[0]][tile[1]] = sid
        self._pulse_button(button_id='reset-map', pulse=False)

    @SimWrappers.call_safe
    def redraw_map(self):
        """
        Redraw the global tile matrix as a map on canvas.
        
        WARNING: this does not clear existing tiles
        
        :return:
        """
        for i in range(self.config.ROWS):  # draw map
            for j in range(self.config.COLS):
                if self.state.TILES[i][j] == 1:
                    self.state.TILES[i][j] = self.canvas.create_rectangle(j * self.config.COL_WIDTH,
                                                                          i * self.config.ROW_HEIGHT,
                                                                          (j + 1) * self.config.COL_WIDTH,
                                                                          (i + 1) * self.config.ROW_HEIGHT,
                                                                          fill=self.data.COLOR_SCHEME['w_fill'][
                                                                              self.config.THEME], tags=["wall"], width=0)
        print(len(self.canvas.find_all()))

    @SimWrappers.call_safe
    def _update_map(self, method):
        """
        Applies a specific modification to the current matrix/map and redraws the canvas.
        
        :param method:
        :return:
        """
        self.reset_snake()
        maze = [[1 if val else 0 for val in row] for row in self.state.TILES]
        if method == 1:
            Common.make_map_connected(maze, 0, 0, self.config.ROWS - 1, self.config.COLS - 1,
                                     self.config.ROWS, self.config.COLS)
        elif method == 2:
            Common.make_map_open(maze)
        self.canvas.delete("wall")
        for i in range(0, self.config.ROWS):
            for j in range(0, self.config.COLS):
                self.state.TILES[i][j] = maze[i][j]
        self.redraw_map()
    
    def update_target(self):
        """
        Randomly modifies the location of the target.
        
        :return:
        """
        self.state.TARGET[:] = [random.randrange(self.config.ROWS), random.randrange(self.config.COLS)]
        while True:
            if self.state.TILES[self.state.TARGET[0]][self.state.TARGET[1]] == 0:
                if not Common.check_closed_path(self.state.TILES, self.state.TARGET[0], self.state.TARGET[1])[0]:
                    break
            self.state.TARGET[:] = [random.randrange(self.config.ROWS), random.randrange(self.config.COLS)]

    def _step(self, thd=None):
        """
        Run one step of the simulation.

        :param thd:
        :return:
        """
        if any(map(any, self.state.TILES)):
            self._sim()
        self._stop('filter', thd=thd)

    def _run(self):
        """
        Enable simulation autoplay.

        :return:
        """
        if any(map(any, self.state.TILES)):
            self._sim(True)

    def _stop(self, tag=None, thd=None):
        """
        Stops the simulation.

        :param tag:
        :param thd:
        :return:
        """
        if thd:
            self.root.after_cancel(thd)
        if tag == 'sim':
            self._get_button('step').configure(state="normal", text=self.data.WIDGET_ICONS["step"], foreground=self.data.COLOR_SCHEME['wid_fg'][self.config.THEME], command=self._step)
            self._get_button('reset-snake').configure(state="normal")
            self._get_button('run').configure(state="normal")

    @SimWrappers.call_safe
    def _create_block(self, x, y, y_width, x_height, dynamic=False):
        """
        Draws a block of tiles of the specified size on canvas.
    
        :param x: X coordinate
        :param y: Y coordinate
        :param y_width: Width of block
        :param x_height: Height of block
        :param dynamic: Toggle block randomizer
        :return:
        """
        block = random.choices(population=[1, 2, 3, 4], weights=[0.9, 0.04, 0.007, 0.004], k=1)[0] if dynamic else self.config.WALL_WIDTH
        self.state.TILES[x][y] = self.canvas.create_rectangle(y * y_width, x * x_height, (y + block) * y_width, (x + block) * x_height,
                                                              fill=self.data.COLOR_SCHEME['w_fill'][self.config.THEME], tags=["wall"], width=0)
        for i, r2 in enumerate([r1[y:y + block] for r1 in self.state.TILES[x:x + block]], start=x):
            for j, c2 in enumerate(r2, start=y):
                self.state.TILES[i][j] = self.state.TILES[x][y]

    def best_path(self, x, y, alg):
        """
        Get the shortest or best path (along with the visited vertices) from the current coordinates to
        TARGET based on the given algorithm.
        
        :param x: Base X coordinate
        :param y: Base Y coordinate
        :param alg: ID of pathfinding algorithm
        :return: Best move as a coordinate tuple
        """
        if alg == 0 or not alg:
            return self.core.random_step((x, y), self.state.TILES, self.config.WRAPAROUND, self.config.EIGHT_DIRECTIONAL)
        else:
            args = ((x, y), self.state.TARGET, self.state.TILES, self.config.WRAPAROUND, self.config.EIGHT_DIRECTIONAL, self.config.BIDIRECTIONAL)
            if alg == 1:
                path_and_visited = self.core.depth_first_search(*args)
            elif alg == 2:
                path_and_visited = self.core.breadth_first_search(*args)
            elif alg == 3:
                path_and_visited = self.core.dijkstra(*args)
            elif alg == 4:
                path_and_visited = self.core.a_star(*args, self.config.HEURISTIC)
            elif alg == 5:
                path_and_visited = self.core.greedy_best_first_search(*args, self.config.HEURISTIC)
            elif alg == 6:
                path_and_visited = self.core.fringe_search(*args, self.config.HEURISTIC)
            elif alg == 7:
                path_and_visited = self.core.bellman_ford(*args)
            elif alg == 8:
                path_and_visited = self._call_with_timeout(self.core.iterative_deepening_a_star, *args, self.config.HEURISTIC)
            del path_and_visited[0][-1]
            return path_and_visited

    def _sim(self, loop=False):
        """
        Simulates an iteration of the current pathfinding algorithm once with the snake.
        
        :param loop: If this is true, the method is called again, basically getting
                    the next simulation state
        :return:
        """
        try:
            if not self.state.SNAKE_CHASING and not self.canvas.coords("target"):
                self.update_target()
                self.canvas.create_rectangle(self.state.TARGET[1] * self.config.COL_WIDTH, self.state.TARGET[0] * self.config.ROW_HEIGHT, (self.state.TARGET[1] + 1) * self.config.COL_WIDTH,
                                             (self.state.TARGET[0] + 1) * self.config.ROW_HEIGHT, fill='orange', tags="target")
            newpos: Tuple[int, int]
            if not self.state.SNAKE_GAME:
                try:
                    # when snake is chasing, currently this doesn't re-evaluate the best path immediately when the
                    # target's position has changed, maybe something to-do in the future; moreover this gives the snake
                    # AI a more natural feeling, compared to knowing the target's location at all times (idk)
                    # Regardless, this may be implemented later, maybe a toggle to ramp up difficulty
                    if not self.state.ROUTING or Common.check_path_blocked(self.state.ROUTING, self.state.TILES):
                        path_and_visited = self.best_path(self.state.HEAD[0], self.state.HEAD[1], alg=self.config.ALGO)
                        if not isinstance(path_and_visited[0], int):
                            self.state.ROUTING[:] = path_and_visited[0]
                            if self.config.VISUALIZE:
                                self._visualize_sections([list(path_and_visited[1]), path_and_visited[0]],
                                                         [self.data.COLOR_SCHEME['highlight_visited'][self.config.THEME],
                                                          self.data.COLOR_SCHEME['highlight_path'][self.config.THEME]],
                                                         self.config.COL_WIDTH, self.config.ROW_HEIGHT)
                                raise AppException.VisualizerPending
                        else:
                            self.state.ROUTING[:] = path_and_visited
                    if isinstance(self.state.ROUTING[-1], tuple):
                        newpos = self.state.ROUTING[-1]
                        del self.state.ROUTING[-1]
                    else:
                        newpos = tuple(self.state.ROUTING)
                        self.state.ROUTING.clear()
                except IndexError:
                    raise AppException.TargetBlocked
            else:
                if self.state.TILES[(self.state.HEAD[0]+self.state.CURRENT_DIRECTION_IN_GAME[0]) % self.config.ROWS][(self.state.HEAD[1]+self.state.CURRENT_DIRECTION_IN_GAME[1]) % self.config.COLS] != 0:
                    newpos = Common.diagonal_adjusted(self.state.HEAD[0], self.state.HEAD[1], self.state.HEAD[0] + self.state.LAST_DIRECTION_IN_GAME[0],
                                                      self.state.HEAD[1] + self.state.LAST_DIRECTION_IN_GAME[1], self.config.ROWS, self.config.COLS)
                else:
                    newpos = Common.diagonal_adjusted(self.state.HEAD[0], self.state.HEAD[1], self.state.HEAD[0] + self.state.CURRENT_DIRECTION_IN_GAME[0],
                                                      self.state.HEAD[1] + self.state.CURRENT_DIRECTION_IN_GAME[1], self.config.ROWS, self.config.COLS)
                    self.state.LAST_DIRECTION_IN_GAME[:] = self.state.CURRENT_DIRECTION_IN_GAME
            if self.state.TILES[newpos[0]][newpos[1]] != 0:
                raise AppException.RanIntoObject
            self.state.TILES[newpos[0]][newpos[1]] = self.canvas.create_rectangle(newpos[1] * self.config.COL_WIDTH, newpos[0] * self.config.ROW_HEIGHT,
                                                                                  (newpos[1] + 1) * self.config.COL_WIDTH, (newpos[0] + 1) * self.config.ROW_HEIGHT,
                                                                                  fill=self.data.COLOR_SCHEME['h_fill'][self.config.THEME], tags=["snek"],
                                                                                  stipple='gray75', outline=self.data.COLOR_SCHEME['canvas'][self.config.THEME])
            last = self.state.SNAKE.popitem()
            self.canvas.itemconfig(self.state.TILES[self.state.HEAD[0]][self.state.HEAD[1]], fill=self.data.COLOR_SCHEME['b_fill'][self.config.THEME])
            self.canvas.delete(self.state.TILES[last[1][0]][last[1][1]])
            self.state.TILES[last[1][0]][last[1][1]] = 0
            self.state.SNAKE = {**{self.state.TILES[newpos[0]][newpos[1]]: [newpos[0], newpos[1]]}, **self.state.SNAKE}
            self.state.PREV[:] = self.state.CURR
            self.state.CURR[:] = self.state.SNAKE[list(self.state.SNAKE)[-1]]
            self.state.HEAD[:] = newpos
            if self.state.HEAD == self.state.TARGET:
                self.canvas.delete("target")
                if self.state.SNAKE_CHASING:
                    raise AppException.TargetCaught
                elif self.state.SNAKE_GAME:
                    new_tail = self.core.random_step((self.state.CURR[0], self.state.CURR[1]), self.state.TILES)
                    self.state.SNAKE[self.state.TILES[new_tail[0]][new_tail[1]]] = [new_tail[0], new_tail[1]]
                    self.state.PREV[:] = self.state.CURR
                    self.state.CURR[:] = new_tail[0], new_tail[1]
            if loop:
                self.state.SIM_CALLBACK = self.root.after(self.config.DELAY, self._sim, loop)
                self._get_button('step').configure(text="\u25A0", foreground="red", command=lambda: self._stop('sim', self.state.SIM_CALLBACK))
                self._get_button('reset-snake').configure(state="disabled")
                self._get_button('run').configure(state="disabled")
        except AppException.RanIntoObject:
            self._handle_game_exception("collision")
        except AppException.TargetBlocked:
            self._handle_game_exception("path_blocked")
        except AppException.TargetCaught:
            self._handle_game_exception("game_over")
        except AppException.VisualizerPending:
            self._await_for_timer(lambda: self.state.VISUALIZER_CALLBACK, func=self._run)
        except TypeError:
            self._stop('sim', self.state.SIM_CALLBACK)

    # @SimWrappers.call_safe
    def _gen_maze(self):
        """
        Draw maze/map from matrix created with the current maze generation algorithm onto canvas.
        
        :return:
        """
        self.reset_map()
        self.reset_snake()
        startx, starty = 0, 0
        if self.config.MAZE_ALGO == 0:
            maze, original_points, converted_points = self.core.simple_maze_generation(self.config.ROWS, self.config.COLS)
        elif self.config.MAZE_ALGO == 1:
            maze, original_points, converted_points = self.core.diagonal_maze_generation(self.config.ROWS, self.config.COLS)
        elif self.config.MAZE_ALGO == 2:
            maze, original_points, converted_points = self.core.dungeon_rooms_maze_generation(self.config.ROWS, self.config.COLS)
        elif self.config.MAZE_ALGO == 3:
            maze, original_points, converted_points = self.core.dfs_maze_generation(self.config.ROWS, self.config.COLS)
            startx, starty = 1, 1
        elif self.config.MAZE_ALGO == 4:
            maze, original_points, converted_points = self.core.recursive_division_maze_generation(self.config.ROWS, self.config.COLS)
        elif self.config.MAZE_ALGO == 5:
            maze, original_points, converted_points = self.core.cell_opening_maze_generation(self.config.ROWS, self.config.COLS)
        elif self.config.MAZE_ALGO == 6:
            maze, original_points, converted_points = self.core.iterative_prims_maze_generation(self.config.ROWS, self.config.COLS)
        if self.config.VISUALIZE:
            if self.state.VISUALIZER_CALLBACK:
                self._stop_visualizer_callback()
            self._pulse_button('gen-maze', pulse=True)
            if original_points:
                self._visualise_maze_in_place([original_points, converted_points], self.config.COL_WIDTH, self.config.ROW_HEIGHT, matrix=maze)
            else:
                self._visualise_maze_in_place(converted_points, self.config.COL_WIDTH, self.config.ROW_HEIGHT, matrix=maze)
        else:
            for im, i in enumerate(range(startx, self.config.ROWS)):
                for jm, j in enumerate(range(starty, self.config.COLS)):
                    self.state.TILES[i][j] = maze[im][jm]
            self.redraw_map()

# def run_app():
#     configuration = SimConfig()
#     hardcoded = SimData()
#     state_variable_reference = SimState()
#     core_logic = SimCore(Pathfinding(), MazeGeneration())
#     SnakeSim(configuration, state_variable_reference, hardcoded, core_logic)
#
# if __name__ == '__main__':
#     run_app()
    