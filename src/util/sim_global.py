"""
These classes define global variables that may or may not change state throughout the course of the application.
SimConfig: These variable hold initial values, and can be changed to your liking
SimState: These variables are internal application variables and must not be modified
SimData: These variables hold larger values and can be changed while maintaining the variable format
"""

from typing import List, Dict, Optional
from threading import Thread

class SimConfig:
	def __init__(self):
		self.MIN_WIDTH: int = 1220
		self.MIN_HEIGHT: int = 670
		self.ROWS: int = 30
		self.COLS: int = 60
		self.DELAY: int = 160
		self.WALL_WIDTH: int = 20
		self.COL_WIDTH: int = 20
		self.ROW_HEIGHT: int = 2
		self.MAZE_COEFF: int = 1
		self.ALGO: int = 0
		self.MAZE_ALGO: int = 2
		self.HEURISTIC: int = 0
		self.THEME: int = 0
		self.FONT_INDEX: int = 3
		self.FRAME_DELAY: int = 50
		self.MIN_CHASE_DELAY: int = 3
		self.WRAPAROUND: bool = True
		self.EIGHT_DIRECTIONAL: bool = True
		self.BIDIRECTIONAL: bool = False
		self.VISUALIZE: bool = False

class SimState:
	def __init__(self):
		self.SIM_CALLBACK: Optional[str] = None
		self.MOVING_CALLBACK: Optional[str] = None
		self.MESSAGE_CALLBACK: Optional[str] = None
		self.VISUALIZER_CALLBACK: Optional[str] = None
		self.FILTER_WORKER: Optional[Thread] = None
		self.FILTER_WORKER_STATUS: bool = True
		self.KEY_PRESSED: bool = False
		self.SNAKE_CHASING: bool = False
		self.SNAKE_GAME: bool = False
		self.MAZE_DYN: bool = False
		self.TARGET: List[Optional[int], Optional[int]] = [None, None]
		self.HEAD: List[Optional[int], Optional[int]] = [None, None]
		self.CURR: List[int, int] = [0, 0]
		self.PREV: List[int, int] = [0, 0]
		self.LAST_DIRECTION_IN_GAME: List[Optional[int], Optional[int]] = [None, None]
		self.CURRENT_DIRECTION_IN_GAME: List[int, int] = [0, 1]
		self.FRAMES: List = []
		self.FRAME_ID: List = []
		self.ROUTING: List = []
		self.TILES: List = []
		self.SNAKE: Dict = {}

class SimData:
	def __init__(self):
		self.MESSAGES = {
			"snake_game": [
				'Time to set a new record!',
				'It\'s Snake, but for Pros!',
				'Eat food, not walls!',
				'Food good, wall bad!',
				'Time to show off your gamer skills!',
				'It\'s eating time.',
				'Do you have what it takes?',
				'Just like the old times.',
				'Classic Snake!'
			],
			"chase_game": [
				"You've been marked. Run.",
				"Time to run!",
				"Hide and seek...but I'm seeking.",
				"RUN",
				"Somebody is very hungry...",
				"Cat and mouse!",
				"Danger is lurking...",
				"Go ahead...I'll give you a headstart.",
				"Don't get caught!",
				"Avoid the Snake!"
			],
			"collision": [
				"Ouch!",
				"Collision!",
				"That's gonna leave a mark!",
				"SPLAT",
				"Simulation over",
				"Ow...",
				"Snake isn't doing well...",
				"Looks like Snake is drunk!",
				"Snake passed out",
				"That looked like it hurt...",
				"Oh well...next time!"
			],
			"path_blocked": [
				"Cannot find path!",
				"Path blocked!",
				"Snake is lost!",
				"Trapped!",
				"Uh oh!",
				"Simulation over"
			],
			"game_over": [
				"Game Over!",
				"Dead!",
				"Better luck next time!",
				"Try again, champ!",
				"Well played!",
				"End of the road!",
				"Got you!",
				"Yikes...",
				"Too easy!",
				"Maybe next time lil bro",
				"Too slow!"
			]
		}
		
		# Color schemes
		self.COLOR_SCHEME = {
			'canvas': [
				'#FFFFFF', '#000000', '#000000', '#003612', '#2A3132', '#191970', '#00868B', '#458B74', '#8B1A1A'
			],
			'wid_fg': [
				'#000000', '#836FFF', '#00CD00', '#84F055', '#90AFC5', '#4169E1', '#79CDCD', '#4EEE94', '#FFDEAD'
			],
			'wid_bg': [
				'#FFFFFF', '#000000', '#000000', '#003612', '#2A3132', '#191970', '#00868B', '#458B74', '#8B1A1A'
			],
			'btn_act_bg': [
				'#FFFFFF', '#000000', '#000000', '#003612', '#2A3132', '#191970', '#00868B', '#458B74', '#8B1A1A'
			],
			'h_fill': [
				'#333333', '#473C8B', '#008B00', '#03FCAD', '#53868B', '#27408B', '#20B2AA', '#32CD32', '#F0E68C'
			],
			'b_fill': [
				'#000000', '#836FFF', '#00CD00', '#53D59A', '#90AFC5', '#4169E1', '#79CDCD', '#4EEE94', '#FFDEAD'
			],
			'w_fill': [
				'#000000', '#551A8B', '#8B4726', '#13882F', '#763726', '#551A8B', '#76EEC6', '#20B2AA', '#CD3700'
			],
			'highlight_space': [
				'#FFD700', '#FFFACD', '#A8E600', '#FFBF00', '#00FFFF', '#FF7F50', '#86ADAD', '#FF1493', '#FF0000'
			],
			'highlight_visited': [
				'#A2A2A3', '#AE62F5', '#FABC9B', '#A4F5CA', '#778991', '#7C9AFC', '#6A7AB0', '#80BF8E', '#BF7575'
			],
			'highlight_path': [
				'#1BF55A', '#0ABF8C', '#0ABF8C', '#03AD03', '#11F5AC', '#06C487', '#53F5C1', '#03FC4E', '#37C204'
			]
		}
		
		self.TOOLTIPS = {
			'reset-snake': "Reset snake",
			'reset-map': "Reset map",
			'step': "Run once",
			'run': "Run (Autoplay)",
			'theme': "Change theme",
			'dynamic-wall': "Toggle dynamic wall",
			'wraparound': "Toggle wrapping\naround edges",
			'cardinal_movement': "Toggle directional\nmovement",
			'bidirectional': "Toggle bidirectional\npathfinding",
			'gen-maze': "Generate map",
			'crt-mode': "Toggle scanlines",
			'play-snake': "Toggle Snake game",
			'snake-chase': "Toggle Snake Chase",
			'delay': "Adjust snake speed",
			'set-wall': "Adjust wall width",
			'maze-choice': "Select map generation algorithm",
			'maze-size': "Set maze size",
			'pathfinding': "Select pathfinding algorithm",
			'heuristic': "Select distance metric",
			'find-holes': "View closed spaces",
			'make-connected': "Break closed edges",
			'make-open': "Open closed spaces",
			'visualizer': "Toggle visualizer",
		}
		
		self.WIDGET_ICONS = {
			'reset-snake': "\u21BA",
			'reset-map': "\u2B6F",
			'step': "\u25B6",
			'run': "\u22B2\u22B2",
			'theme': "\U0001F58C",
			'dynamic-wall': "\U0001F3B2",
			'wraparound': "\U0001FA9E",
			'cardinal_movement': "\U0001F9ED",
			'bidirectional': "\u21CC",
			'gen-maze': "\U0001F3C1",
			'crt-mode': "\U0001F4FA",
			'play-snake': "\U0001F3AE",
			'snake-chase': "\U0001F3C3",
			'delay': "\u22D9",
			'set-wall': "\u258C\u2194",
			'maze-size': "\u26F6",
			'find-holes': "\u2B55",
			'make-connected': "\U0001F517",
			'make-open': "\U0001FA93",
			'visualizer': "\U0001F441",
			'help': "\u2754",
			'about': "\u24D8"
		}
		
		# currently supporting only these; more can be added in pathfinding.py
		self.PATHFINDING_ALGOS = [
			'Random Walk', 'Depth First', 'Breadth First', 'Greedy Best First', 'A*', 'Dijkstra', 'Fringe', 'Bellman-Ford', 'Iterative Deepening A*'
		]
		
		self.MAZE_GENERATION_ALGOS = [
			'Simple Random', 'Diagonal Random', 'Dungeon Rooms', 'DFS Maze', 'Recursive Division', 'Cell Opening'
		]
		
		self.DISTANCE_METRICS = [
			'Chebyshev', 'Manhattan', 'Euclidean', 'Octile', 'Hamming'
		]
		
		self.HELP_INFO = f"{self.WIDGET_ICONS['reset-snake']} - Resets/Removes the snake from canvas\n\n" \
		                 f"{self.WIDGET_ICONS['reset-map']} - Resets/Removes walls from the canvas, including visualized areas\n\n" \
		                 f"{self.WIDGET_ICONS['step']} - Moves the snake once using the selected pathfinding algorithm\n\n" \
		                 f"{self.WIDGET_ICONS['run']} - Autoplay simulation with selected pathfinding algorithm\n\n" \
		                 f"This can also be used to start or stop a sim run or game\n\n" \
		                 f"{self.WIDGET_ICONS['delay']} - Adjust the snake's speed\n\n" \
		                 f"{self.WIDGET_ICONS['set-wall']} - Adjust the wall width when drawing\n\n" \
		                 f"{self.WIDGET_ICONS['maze-size']} - Adjust the maze size (warning: resets the entire canvas)\n\n" \
		                 f"{self.WIDGET_ICONS['theme']} - Toggle app theme\n\n" \
		                 f"{self.WIDGET_ICONS['dynamic-wall']} - Toggle making walls having randomized width while drawing\n\n" \
		                 f"{self.WIDGET_ICONS['wraparound']} - Toggle wrapping symmetrically from end-to-end when at edges\n\n" \
		                 f"{self.WIDGET_ICONS['cardinal_movement']} - Toggle 4-directional or 8-directional movement\n\n" \
		                 f"{self.WIDGET_ICONS['bidirectional']} - Toggle making pathfinding bidirectional\n\n" \
		                 f"{self.WIDGET_ICONS['gen-maze']} - Generate maze with a new seed\n\n" \
		                 f"{self.WIDGET_ICONS['find-holes']} - Finds all holes or closed spaces in the map and highlights them\n\n" \
		                 f"{self.WIDGET_ICONS['make-connected']} - Breaks up points in closed spaces to enforce connectivity\n\n" \
		                 f"{self.WIDGET_ICONS['make-open']} - Tears up calculated sections of the map to enforce connectivity\n\n" \
		                 f"{self.WIDGET_ICONS['visualizer']} - Toggle visualizing pathfinding/maze-generation algorithms;" \
		                 f"if this is toggled off, it will clear all visualized/highlighted areas\n\n" \
		                 f"{self.WIDGET_ICONS['crt-mode']} - Toggle the scanline filter for a CRT effect (reduces app performance)\n\n" \
		                 f"{self.WIDGET_ICONS['play-snake']} - Toggle playing the game of Snake\n\n" \
		                 f"{self.WIDGET_ICONS['snake-chase']} - Toggle playing as the target instead of the snake in Snake\n\n" \
		                 f"\n\n" \
		                 f"\u2B50 Draw the snake using RMB, draw walls using the LMB\n\n" \
		                 f"\u2B50 The snake can only be drawn from its last drawn end, or the head\n\n" \
		                 f"\u2B50 Use the reset buttons to reset the snake or map state at any point\n\n" \
		                 f"\u2B50 Use the visualizer button to toggle visualizing when generating mazes or running the pathfinding simulator," \
		                 f"or to clear any highlighting or visualizations from the canvas\n\n" \
		                 f"\u2B50 If at any time the app/snake/maze generation/visualization gets stuck, simply use the reset buttons, " \
		                 f"or the visualizer buttons to reset to the original state\n\n" \
		                 f"\u2B50 Buttons may sometimes pulse as a hint or while they are performing a task\n\n" \
		                 f"\u2B50 Certain buttons (on the right side) affect the way pathfinding works and can be toggled on or off at any point\n\n" \
		                 f"\u2B50 Changing the maze generation algorithm will not change the current maze, it must be regenerated\n\n" \
		                 f"\u2B50 Increasing the maze size will reduce the speed of visualization and may thus incur some performance loss\n\n" \
		                 f"\u2B50 It is advisable to use the filter effect only when working with small mazes, otherwise it will cause significant lag;" \
		                 f"in general, the app performs better when the filter is not on (it has been included purely for aesthetic reasons)\n\n" \
		                 f"\u2B50 The snake/snake chase games use WASD for movement/changing direction\n\n" \
		                 f"\u2B50 The IDA* algorithm is currently a recursive implementation, and so only works for small mazes (recursion depth limit)" \

