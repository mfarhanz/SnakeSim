import tkinter.font as tkFont
import tkinter as tk
from random import random, choice, choices
from multiprocessing import Process, Queue
from time import perf_counter

def moves(x, y):
    return [(x - 1, y - 1), (x - 1, y), (x - 1, y + 1), (x, y - 1),
                    (x, y + 1), (x + 1, y - 1), (x + 1, y), (x + 1, y + 1)]

def patterns():
    return [
        [[0, 0], [0, 0]], [[1, 0], [0, 0]], [[0, 1], [0, 0]], [[0, 0], [1, 0]], [[0, 0], [0, 1]],
        [[1, 1], [0, 0]], [[0, 0], [1, 1]], [[1, 0], [1, 0]], [[0, 1], [0, 1]],
        [[1, 1], [1, 0]], [[1, 0], [1, 1]], [[0, 1], [1, 1]], [[1, 1], [0, 1]]
    ]

def ret_move_lst(x, y, q):
    move_lst = [(i % ROWS, j % COLS) for (i, j) in moves(x, y)
                if not tiles[i % ROWS][j % COLS] and (i, j) != (x, y) and not
                any([tiles[(x - 1) % ROWS][y] == 1 and tiles[x][(y + 1) % COLS] == 1
                     and (i, j) == ((x - 1) % ROWS, (y + 1) % COLS),
                     tiles[x][(y + 1) % COLS] == 1 and tiles[(x + 1) % ROWS][y] == 1
                     and (i, j) == ((x + 1) % ROWS, (y + 1) % COLS),
                     tiles[(x + 1) % ROWS][y] == 1 and tiles[x][(y - 1) % COLS] == 1
                     and (i, j) == ((x + 1) % ROWS, (y - 1) % COLS),
                     tiles[x][(y - 1) % COLS] == 1 and tiles[(x - 1) % ROWS][y] == 1
                     and (i, j) == ((x - 1) % ROWS, (y - 1) % COLS)])]
    q.put(move_lst)

def ret_move_wt_lookup(x, y, q):
    move_wt_lookup = {((x - 1) % ROWS, (y - 1) % COLS): 0.2, ((x - 1) % ROWS, y): 0.8,
                      ((x - 1) % ROWS, (y + 1) % COLS): 0.2, (x, (y - 1) % COLS): 0.8,
                      (x, (y + 1) % COLS): 0.8, ((x + 1) % ROWS, (y - 1) % COLS): 0.2,
                      ((x + 1) % ROWS, y): 0.8, ((x + 1) % ROWS, (y + 1) % COLS): 0.2}
    q.put(move_wt_lookup)

def best_move(x, y, alg):
    match alg:
        case 'djikstra':
            pass
        case _:
            queue = Queue()
            start = perf_counter()
            # move_lst = [(i % ROWS, j % COLS) for (i, j) in moves(x, y)
            #             if not tiles[i % ROWS][j % COLS] and (i, j) != (x, y) and not
            #             any([tiles[(x - 1) % ROWS][y] == 1 and tiles[x][(y + 1) % COLS] == 1
            #                  and (i, j) == ((x - 1) % ROWS, (y + 1) % COLS),
            #             tiles[x][(y + 1) % COLS] == 1 and tiles[(x + 1) % ROWS][y] == 1
            #                  and (i, j) == ((x + 1) % ROWS, (y + 1) % COLS),
            #             tiles[(x + 1) % ROWS][y] == 1 and tiles[x][(y - 1) % COLS] == 1
            #                  and (i, j) == ((x + 1) % ROWS, (y - 1) % COLS),
            #             tiles[x][(y - 1) % COLS] == 1 and tiles[(x - 1) % ROWS][y] == 1
            #                  and (i, j) == ((x - 1) % ROWS, (y - 1) % COLS)])]
            # move_wt_lookup = {((x - 1) % ROWS, (y - 1) % COLS): 0.2, ((x - 1) % ROWS, y): 0.8,
            #                   ((x - 1) % ROWS, (y + 1) % COLS): 0.2, (x, (y - 1) % COLS): 0.8,
            #                   (x, (y + 1) % COLS): 0.8, ((x + 1) % ROWS, (y - 1) % COLS): 0.2,
            #                   ((x + 1) % ROWS, y): 0.8, ((x + 1) % ROWS, (y + 1) % COLS): 0.2}
            p1 = Process(target=ret_move_lst, args=(x, y, queue))
            p2 = Process(target=ret_move_wt_lookup, args=(x, y, queue))
            p1.start()
            p2.start()
            move_wt_lookup = queue.get()
            move_lst = queue.get()
            p1.join()
            p2.join()
            stop = perf_counter()
            print((stop - start) * 1000)
            print()
            # wt_lst = [move_wt_lookup[coord] for coord in move_lst]
            # return choices(population=move_lst, weights=wt_lst, k=1)[0]

def sim(loop=False):
    try:
        if msg_label.winfo_ismapped():
            msg_label.place_forget()
        col_width = int(c.winfo_width() / COLS)
        row_height = int(c.winfo_height() / ROWS)
        newpos = best_move(head[0], head[1], alg=ALGO)
        tiles[newpos[0]][newpos[1]] = c.create_rectangle(newpos[1] * col_width, newpos[0] * row_height,
                                                         (newpos[1] + 1) * col_width, (newpos[0] + 1) * row_height,
                                                         fill=col_scheme['h_fill'][THEME], tags=["snek"],
                                                         stipple='gray75', outline=col_scheme['canvas'][THEME])
        global snake
        last = snake.popitem()
        c.itemconfig(tiles[head[0]][head[1]], fill=col_scheme['b_fill'][THEME])
        c.delete(tiles[last[1][0]][last[1][1]])
        tiles[last[1][0]][last[1][1]] = 0
        snake = {**{tiles[newpos[0]][newpos[1]]: [newpos[0], newpos[1]]}, **snake}
        prev[:] = curr
        curr[:] = snake[list(snake)[-1]]
        head[:] = newpos
        stop()
        if loop:
            thread = root.after(DELAY, sim, loop)
            button3.configure(text="\u25A0", foreground="red", command=lambda: stop(thread))
            button1.configure(state="disabled")
            button4.configure(state="disabled")
    except IndexError:
        stop()
        msg_label.place(x=20, y=700 - msg_label.winfo_reqheight() * 2, in_=root)

def reset_snake():
    c.delete("snek")
    tiles[:] = [[0 if tiles[i][j] not in [0, 1] else tiles[i][j] for j in range(COLS)] for i in range(ROWS)]
    head[:] = [None, None]
    body_border[:] = []
    snake.clear()
    # global DELAY
    # DELAY = 160
    # delay_label.set(str(DELAY))
    if msg_label.winfo_ismapped():
        msg_label.place_forget()

def reset_map():
    c.delete("wall")
    tiles[:] = [[0 if tiles[i][j] == 1 else tiles[i][j] for j in range(COLS)] for i in range(ROWS)]

def stop(thd=None):
    if thd:
        root.after_cancel(thd)
    button3.configure(state="normal", text="\u25B6", foreground=col_scheme['wid_fg'][THEME], command=step)
    button1.configure(state="normal")
    button4.configure(state="normal")

def step():
    if any(map(any, tiles)):
        sim()

def run():
    if any(map(any, tiles)):
        sim(True)

def speed(cmd):
    global DELAY, delay_label
    if cmd == "up":
        DELAY = DELAY+20 if DELAY <= 1000 else DELAY
        if DELAY >= 1000:
            spinner1.configure(foreground="red")
            root.after(500, lambda: spinner1.configure(foreground=col_scheme['wid_fg'][THEME]))
    else:
        DELAY = DELAY-20 if DELAY > 20 else DELAY
        if DELAY <= 20:
            spinner1.configure(foreground="red")
            root.after(500, lambda: spinner1.configure(foreground=col_scheme['wid_fg'][THEME]))
    # delay_label.set(str(DELAY))

def create_block(x, y, y_width, x_height, dynamic=False):
    block = choices(population=[1, 2, 3, 4], weights=[0.9, 0.04, 0.007, 0.004], k=1)[0] if dynamic else WALL_W
    tiles[x][y] = c.create_rectangle(y * y_width, x * x_height, (y + block) * y_width,
                                     (x + block) * x_height, fill=col_scheme['w_fill'][THEME], tags=["wall"], width=0)
    for i, r2 in enumerate([r1[y:y + block] for r1 in tiles[x:x + block]], start=x):
        for j, c2 in enumerate(r2, start=y):
            tiles[i][j] = 1

def gen_maze():
    reset_map()
    reset_snake()
    col_width = int(c.winfo_width() / COLS)
    row_height = int(c.winfo_height() / ROWS)
    # tiles[:] = list(map(lambda x: [int(random() + 0.5) for _ in range(COLS)], range(ROWS)))
    # i = 0
    # while i < len(tiles):
    #     j = 0
    #     while j < len(tiles[0]):                          # maze generator v1
    #         if not tiles[i][j] or tiles[i][j] == 1:
    #             tiles[i][j] = int(random() + 0.5)
    #             if tiles[i][j]:
    #                 create_block(choice([(i-1) % ROWS, (i+1) % ROWS, i]),
    #                              choice([(j-1) % COLS, (j+1) % COLS, j]), col_width, row_height, True)
    #         j += choice([3, 1, 4, 2])
    #     i += choice([3, 1, 4, 2])
    for i in range(0, len(tiles), 2):
        for j in range(0, len(tiles[0]), 2):
            block = choice(patterns())
            for i2, x2 in enumerate(block):
                for j2, y2 in enumerate(x2):
                    if y2 and random() < 0.5:
                        create_block((i + i2) % ROWS, (j + j2) % COLS, col_width, row_height, True)

def set_wall(x):
    global WALL_W
    WALL_W = int(x)

def dynamic_wall_toggle():
    global MAZE_DYN
    MAZE_DYN = not MAZE_DYN
    slider1.config(state=("normal", "disabled")[MAZE_DYN],
                   foreground=(col_scheme['wid_fg'][THEME], '#6D6D6B')[MAZE_DYN])

def gamma(x):
    pass

def set_theme():
    global THEME
    # theme = (0, 1)[1 ^ theme]
    THEME = -~THEME % len(col_scheme['canvas'])
    c.configure(background=col_scheme['canvas'][THEME])
    spinner1.configure(background=col_scheme['wid_bg'][THEME], foreground=col_scheme['wid_fg'][THEME],
                       buttonbackground=col_scheme['wid_bg'][THEME])
    msg_label.configure(background=col_scheme['wid_bg'][THEME], foreground=col_scheme['wid_fg'][THEME], )
    for slider in [slider1, slider2]:
        slider.configure(activebackground=col_scheme['wid_fg'][THEME], background=col_scheme['wid_bg'][THEME],
                         foreground=col_scheme['wid_fg'][THEME], troughcolor=col_scheme['wid_bg'][THEME])
    for button in [button1, button2, button3, button4, button5, button6, button7]:
        button.configure(activebackground=col_scheme['btn_act_bg'][THEME], background=col_scheme['wid_bg'][THEME],
                         foreground=col_scheme['w_fill'][THEME] if button.winfo_name() == "reset-map"
                         else col_scheme['wid_fg'][THEME])

def config(widgets):
    for widget in widgets:
        match widget.winfo_name():
            case "reset-snake" | "reset-map" | "step" | "run" | "theme" | "dynamic_wall" | "gen-maze":
                widget.configure(borderwidth=2, width=2, activeforeground="cyan", relief="flat", overrelief="raised",
                                 font=tkFont.Font(family=tkFont.families()[3], size=18, weight='bold'))
            case "message":
                widget.configure(font=tkFont.Font(family=tkFont.families()[3], size=18, weight='bold'))
            case "delay":
                widget.configure(borderwidth=0, textvariable=delay_label, width=2, justify="center",
                                 font=tkFont.Font(family=tkFont.families()[3], size=20, weight='bold'))
            case "set-wall" | "func2":
                widget.configure(from_=1, to=4, orient="horizontal", showvalue=False, length=100, highlightthickness=0,
                                 font=tkFont.Font(family=tkFont.families()[3], size=13, weight='bold'))

def callback(event):
    canvas_x = c.winfo_rootx()
    canvas_y = c.winfo_rooty()
    canvas_width = c.winfo_width()
    canvas_height = c.winfo_height()
    if canvas_x <= event.x_root <= canvas_x + canvas_width and canvas_y <= event.y_root <= canvas_y + canvas_height:
        col_width = int(c.winfo_width() / COLS)
        row_height = int(c.winfo_height() / ROWS)
        col = event.x // col_width
        row = event.y // row_height
        if not tiles[row][col]:
            if event.state == 0x0100:           # LMB hit
                if head.count(None) == len(head):         # not any(map(any, tiles)) (before)
                    tiles[row][col] = c.create_rectangle(col * col_width, row * row_height, (col+1) * col_width,
                                                         (row+1) * row_height, fill=col_scheme['h_fill'][THEME],
                                                         tags=["snek"], stipple='gray75')
                    snake[tiles[row][col]] = [row, col]
                    prev[:] = curr
                    curr[:] = row, col
                    head[:] = row, col
                elif (row, col) in moves(curr[0], curr[1]):
                    if any(tiles[coord[0]][coord[1]] != 0 for coord in moves(row, col)
                           if 0 <= coord[0] < ROWS and 0 <= coord[1] < COLS):
                        tiles[row][col] = c.create_rectangle(col * col_width, row * row_height,
                                                             (col + 1) * col_width, (row + 1) * row_height,
                                                             fill=col_scheme['b_fill'][THEME], tags="snek",
                                                             stipple='gray75')
                        snake[tiles[row][col]] = [row, col]
                        prev[:] = curr
                        curr[:] = row, col
            elif event.state == 0x0400:         # RMB hit
                create_block(row, col, col_width, row_height, MAZE_DYN)
        # if tiles[row][col] == 1 and event.state == 0x0200:    # delete wall not working yet
        #     # c.itemconfig(tiles[row][col], fill=col_scheme['canvas'][theme])
        #     c.delete(tiles[row][col])
        #     tiles[row][col] = 0
        elif [row, col] == prev:
            c.delete(tiles[row][col])
            tiles[row][col] = 0

if __name__ == '__main__':
    ROWS = 30  # uppercase vars can be modified in program
    COLS = 60
    DELAY = 160
    WALL_W = 1
    MAZE_COEFF = 1
    MAZE_DYN = False
    ALGO = ''
    THEME = 0
    head = [None, None]
    curr = [0, 0]
    prev = [0, 0]
    snake = {}
    body_border = []
    tiles = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    # fonts = [0, 1, 2, 3, 4, 7, 40, 330, 340]
    col_scheme = {
        'canvas': ('white', 'black', 'black', '#2A3132', 'midnight blue', 'turquoise4', 'aquamarine4', 'firebrick4'),
        'wid_fg': (
        'black', 'SlateBlue1', 'green3', '#90AFC5', 'royal blue', 'DarkSlateGray3', 'SeaGreen2', 'navajo white'),
        'wid_bg': ('white', 'black', 'black', '#2A3132', 'midnight blue', 'turquoise4', 'aquamarine4', 'firebrick4'),
        'btn_act_bg': (
        'white', 'black', 'black', '#2A3132', 'midnight blue', 'turquoise4', 'aquamarine4', 'firebrick4'),
        'h_fill': (
        'gray20', 'SlateBlue4', 'green4', 'CadetBlue4', 'RoyalBlue4', 'DarkSlateGray4', 'lime green', 'khaki'),
        'b_fill': (
        'SlateGray4', 'SlateBlue1', 'green3', '#90AFC5', 'royal blue', 'DarkSlateGray3', 'SeaGreen2', 'navajo white'),
        'w_fill': (
        'LightSteelBlue4', 'purple4', 'sienna4', '#763726', 'purple4', 'aquamarine2', 'light sea green', 'OrangeRed3')
    }

    root = tk.Tk(className=" SnakeSim")
    root.resizable(False, False)
    root.geometry('%dx%d+%d+%d' % (1200, 700, root.winfo_screenmmwidth()/4, root.winfo_screenmmheight()/4))
    c = tk.Canvas(root, width=1200, height=700, borderwidth=0, highlightthickness=0, background=col_scheme['canvas'][THEME])
    c.bind("<1>", lambda event: event.widget.focus_set())
    button1 = tk.Button(text="\u2B6F", name="reset-snake", command=reset_snake)
    button2 = tk.Button(text="\u2B6F", name="reset-map", command=reset_map)
    button3 = tk.Button(text="\u25B6", name="step", command=step)     # u23F5 (before)
    button4 = tk.Button(text="\u22B2\u22B2", name="run", command=run)       # u23E9 (before)
    button5 = tk.Button(text='\U0001F58C', name="theme", command=set_theme)     # U0001F3A8 (before)
    button6 = tk.Button(text='\U0001F500', name="dynamic_wall", command=dynamic_wall_toggle)
    button7 = tk.Button(text='\U0001F3C1', name="gen-maze", command=gen_maze)
    slider1 = tk.Scale(name="set-wall", orient=tk.HORIZONTAL, label="\u258C\u2194", command=set_wall)
    slider2 = tk.Scale(name="func2", orient=tk.HORIZONTAL, label="\u03B3", command=gamma)
    spinner1 = tk.Spinbox(name="delay", command=(root.register(speed), '%d'))
    msg_label = tk.Label(text="Collision!", name="message")
    delay_label = tk.StringVar(value='\u22D9')  # 23F1 (before)
    config([button1, button2, button3, button4, button5, button6, button7, msg_label, spinner1, slider1, slider2])
    c.create_window(10, 10, anchor="nw", window=button1)
    c.create_window(button1.winfo_reqwidth()+20, 10, anchor="nw", window=button2)
    c.create_window(button1.winfo_reqwidth()*2+30, 10, anchor="nw", window=button3)
    c.create_window(button1.winfo_reqwidth()*3+40, 10, anchor="nw", window=button4)
    c.create_window(button1.winfo_reqwidth()*4+60, 17, anchor="nw", window=spinner1)
    c.create_window(button1.winfo_reqwidth()*6+60, 7, anchor="nw", window=slider1)
    c.create_window(button1.winfo_reqwidth()*8+80, 7, anchor="nw", window=slider2)
    c.create_window(c.winfo_reqwidth()-button5.winfo_reqwidth()-10, 10, anchor="nw", window=button5)
    c.create_window(c.winfo_reqwidth()-button5.winfo_reqwidth()-10, 70, anchor="nw", window=button6)
    c.create_window(c.winfo_reqwidth()-button5.winfo_reqwidth()-10, 130, anchor="nw", window=button7)
    c.bind("<B1-Motion>", callback)
    c.bind("<B3-Motion>", callback)
    c.bind("<Button-2>", callback)
    c.pack()
    set_theme()
    root.mainloop()
