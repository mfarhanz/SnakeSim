import random
from typing import List, Tuple
# from snakesim.src.util.common import Common
# from snakesim.src.util.matrix_helpers import MatrixHelpers
from ..util.common import Common
from ..util.matrix_helpers import MatrixHelpers

class MazeGeneration:
	def dungeon_rooms_maze_generation(self, height, width):
		"""
		Returns a map/maze generated by a randomised dungeon-rooms algorithm
		
		:param height: breadth of 2D map
		:param width: length of 2D map
		"""
		maze = list(map(lambda x: [int(random.random() + 0.5) for _ in range(width)], range(height)))
		maze_original_points = [(i, j) for i in range(height) for j in range(width) if maze[i][j] == 1]
		maze_converted_points = []
		scaling_factor = max(height // 30, width // 60)
		num_of_points = range(random.randrange(20 + scaling_factor * 5, 40 + scaling_factor * 5))
		points = [(random.randrange(0, height), random.randrange(0, width)) for _ in num_of_points]
		for p in points:
			hole_size = random.choice([1, 2, 3] + list(range(4, 4 + scaling_factor - 1)))
			for i in range(p[0] - hole_size, p[0] + hole_size):
				for j in range(p[1] - hole_size, p[1] + hole_size):
					maze[i % height][j % width] = 0
					maze_converted_points.append((i % height, j % width))
		return maze, maze_original_points, maze_converted_points
	
	def dfs_maze_generation(self, rows, cols):
		"""
		Applies depth first search (in-place) to 2D matrix to generate maze/map
		
		:param rows: Number of rows of 2D matrix representing maze
		:param cols: Number of columns of 2D matrix representing maze
		"""
		# Directions for moving (right, down, left, up)
		directions = [(2, 0), (0, 2), (-2, 0), (0, -2)]  # (dx, dy)
		odd_rows = rows - 1 if rows % 2 == 0 else rows
		odd_cols = cols - 1 if cols % 2 == 0 else cols
		x, y = random.randrange(1, odd_cols, 2), random.randrange(1, odd_rows, 2)
		maze = [[1] * odd_cols for _ in range(odd_rows)]
		maze_original_points = [(i, j) for i in range(odd_rows) for j in range(odd_cols) if maze[i][j] == 1]
		maze_converted_points = [(y, x)]
		stack = [(y, x)]
		maze[y][x] = 0
		while stack:
			y, x = stack[-1]
			maze[y][x] = 0  # Mark the current cell as part of the maze (0)
			maze_converted_points.append((y, x))
			random.shuffle(directions)  # Randomize directions
			found = False
			for dx, dy in directions:
				nx, ny = x + dx, y + dy  # New coordinates
				if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and maze[ny][nx] == 1:
					# Carve a path between the current cell and the new cell
					maze[y + dy // 2][x + dx // 2] = 0  # Remove the wall between
					maze[ny][nx] = 0  # Mark the new cell as part of the maze
					stack.append((ny, nx))  # Add new cell to the stack
					maze_converted_points.extend([(y + dy // 2, x + dx // 2), (ny, nx)])
					found = True
					break
			if not found:
				stack.pop()
		return maze, maze_original_points, maze_converted_points
		# Recursive version (works only for smaller matrices)
		# maze[y][x] = 0  # Mark the current cell as part of the maze (0)
		# # Directions for moving (right, down, left, up)
		# directions = [(2, 0), (0, 2), (-2, 0), (0, -2)]  # (dx, dy)
		# random.shuffle(directions)  # Randomize directions
		# for dx, dy in directions:
		# 	nx, ny = x + dx, y + dy  # New coordinates
		# 	if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and maze[ny][nx] == 1:
		# 		# Carve a path between the current cell and the new cell
		# 		maze[y + dy // 2][x + dx // 2] = 0  # Remove the wall between
		# 		self.dfs_maze_generation(maze, nx, ny, rows, cols)
		
	def simple_maze_generation(self, height, width):
		"""
		Returns map generated using randomization
		
		:param height: breadth of 2D map
		:param width: length of 2D map
		"""
		maze = [[0] * width for _ in range(height)]
		maze_original_points = []
		maze_converted_points = []
		for i in range(0, len(maze), 2):
			for j in range(0, len(maze[0]), 2):
				block = random.choice(MatrixHelpers.block_patterns())
				for i2, x2 in enumerate(block):
					for j2, y2 in enumerate(x2):
						if y2 and random.random() < 0.4:  # mess with percent to change maze generation
							block = random.choices(population=[1, 2, 3, 4], weights=[0.9, 0.04, 0.007, 0.004], k=1)[0]
							x, y, = (i + i2) % height, (j + j2) % width
							for ri, r2 in enumerate([r1[y:y + block] for r1 in maze[x:x + block]], start=x):
								for rj, c2 in enumerate(r2, start=y):
									maze[ri][rj] = 1
									maze_converted_points.append((ri, rj))
		return maze, maze_original_points, maze_converted_points
	
	def diagonal_maze_generation(self, height, width):
		"""
		Returns maze generated using a simple checkerboard-randomized pattern
		
		:param height: breadth of 2D map
		:param width: length of 2D map
		"""
		maze = [[0] * width for _ in range(height)]
		maze_original_points = []
		maze_converted_points = []
		for i in range(len(maze)):
			for j in range(len(maze[i])):
				if i % 2 == 0:
					maze[i][j] = 1
					maze_original_points.append((i, j))
				if i % 2 == 1 and j % 2 == 0:
					maze[i][j] = 1
					maze_original_points.append((i, j))
		for i in range(1, len(maze), 2):
			for j in range(1, len(maze[i]), 2):
				if maze[i][j] == 0:
					try:
						walls = [tpl for tpl in Common.valid_moves(i, j, height, width, False, True) if maze[tpl[0]][tpl[1]] == 1]
						wall = random.choice(walls)
						walls.remove(wall)
						wall2 = random.choice(walls)
						maze[wall[0]][wall[1]] = 0
						maze[wall2[0]][wall2[1]] = 0
						maze_converted_points.extend([(wall[0], wall[1]), (wall2[0], wall2[1])])
					except IndexError:
						continue
		return maze, maze_original_points, maze_converted_points
	
	# TBD later
	def iterative_prims_maze_generation(self, height, width):
		maze = [[1] * width for _ in range(height)]
		directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
		x, y = random.randrange(0, height), random.randrange(0, width)
		maze_original_points = [(i, j) for i in range(height) for j in range(width) if maze[i][j] == 1]
		maze_converted_points = [(x, y)]
		frontier = [(x, y)]
		while frontier:
			frontier_cell = random.choice(frontier)
			frontier_neighbors = []
			for dx, dy in directions:
				nx, ny = frontier_cell[0] + dx, frontier_cell[1] + dy
				if 0 <= nx < height and 0 <= ny < width and not maze[nx][ny]:
					frontier_neighbors.append((nx, ny))
			frontier_neighbors.append(frontier_cell)
			adjacent = random.choice(frontier_neighbors)
			maze[adjacent[0]][adjacent[1]] = 0
			maze[frontier_cell[0]][frontier_cell[1]] = 0
			frontier_neighbors.remove(adjacent)
			if frontier_cell in frontier_neighbors:
				frontier_neighbors.remove(frontier_cell)
			frontier.remove(frontier_cell)
			frontier.extend(frontier_neighbors)
			# for r in maze:
			# 	print(' '.join(map(str, r)))
		return maze, maze_original_points, maze_converted_points
	
	def cell_opening_maze_generation(self, height, width):
		maze = [[0 if i % 2 == 0 and j % 2 == 0 else 1 for i in range(width)] for j in range(height)]
		maze_original_points = [(i, j) for i in range(height) for j in range(width) if maze[i][j] == 1]
		maze_converted_points = []
		cells = []
		for i in range(width):
			for j in range(height):
				if maze[j][i] == 0:
					cells.append((i, j))
		directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
		for i, cell in enumerate(cells):
			side = random.choice(directions)
			gap = (cell[1]+side[0], cell[0]+side[1])
			if 0 <= gap[0] < height and 0 <= gap[1] < width:
				maze[gap[0]][gap[1]] = 0
				maze_converted_points.append((gap[0], gap[1]))
		return maze, maze_original_points, maze_converted_points

	def recursive_division_maze_generation(self, height, width):
			"""
			Returns map/maze generated using a recursive division algorithm
			
			:param height: breadth of 2D map
			:param width: length of 2D map
			"""
			def check_connectivity(x, y, h, w):
				if maze[x][(y + 1) % w] == 1 and maze[x][(y - 1) % w] == 1 and \
					maze[(x + 1) % h][y] == 0 and maze[(x - 1) % h][y] == 0:
					return True
				elif maze[(x + 1) % h][y] == 1 and maze[(x - 1) % h][y] == 1 and \
					maze[x][(y + 1) % w] == 0 and maze[x][(y - 1) % w] == 0:
					return True
				else:
					return False
			
			def recursive_divide(matrix, startx, starty):
				if len(matrix) == 1:
					return
				if len(matrix[0]) == 1:
					return
				h, w = len(matrix), len(matrix[0])
				if startx + 1 == startx + h - 1 or starty + 1 == starty + w - 1:
					return
				point = (random.randrange(startx + 1, startx + h - 1), random.randrange(starty + 1, starty + w - 1))
				for j in range(startx, startx + h):
					maze[j][point[1]] = 1
					maze_converted_points.append((j, point[1]))
				for i in range(starty, starty + w):
					maze[point[0]][i] = 1
					maze_converted_points.append((point[0], i))
				wall_top_half = [(x, point[1]) for x in range(startx, point[0])]
				wall_bottom_half = [(x, point[1]) for x in range(point[0], h)]
				wall_left_half = [(point[0], y) for y in range(starty, point[1])]
				wall_right_half = [(point[0], y) for y in range(point[1], w)]
				valid_walls = [wall for wall in [wall_right_half, wall_top_half, wall_left_half, wall_bottom_half] if wall]
				if len(valid_walls) >= 1:
					for wall in random.sample(valid_walls, k=len(valid_walls) - 1 if len(valid_walls) > 1 else 1):
						gap = random.choice(wall)
						while True:
							if len(wall) < 2 or check_connectivity(gap[0], gap[1], h, w):
								break
							else:
								wall.remove(gap)
							gap = random.choice(wall)
						maze[gap[0]][gap[1]] = 0
						maze_converted_points.append((gap[0], gap[1]))
				q1 = MatrixHelpers.get_selection(maze, startx, starty, point[0], point[1])
				q2 = MatrixHelpers.get_selection(maze, startx, point[1] + 1, point[0], starty + w)
				q3 = MatrixHelpers.get_selection(maze, point[0] + 1, starty, startx + h, point[1])
				q4 = MatrixHelpers.get_selection(maze, point[0] + 1, point[1] + 1, startx + h, starty + w)
				recursive_divide(q1, startx, starty)
				recursive_divide(q2, startx, point[1] + 1)
				recursive_divide(q3, point[0] + 1, starty)
				recursive_divide(q4, point[0] + 1, point[1] + 1)
			
			maze = [[0 for _ in range(width)] for _ in range(height)]
			maze_original_points = []
			maze_converted_points = []
			recursive_divide(maze, 0, 0)
			return maze, maze_original_points, maze_converted_points
