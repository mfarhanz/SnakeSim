import math
from typing import List, Tuple
import random

class Common:
	@staticmethod
	def valid_moves(x, y, rows, cols, prune=False, all_directional=False) -> List[Tuple[int, int]]:
		"""
		Returns set of valid moves that can be made from current location

		:param x: X coordinate of point
		:param y: Y coordinate of point
		:param rows: Number of rows in matrix
		:param cols: Number of columns in matrix
		:param prune: If this is true, returned moves will not include moves wrapped around edges
		:param all_directional: If this is true, considers 8-directional movement instead of 4-directional
		:return: List of valid coordinates for current point
		"""
		
		move_set = [(x - 1, y), (x, y - 1), (x, y + 1), (x + 1, y)]
		if all_directional:
			move_set.extend([(x - 1, y - 1), (x - 1, y + 1), (x + 1, y - 1), (x + 1, y + 1)])
		if not prune:
			move_set = [move for move in move_set if 0 <= move[0] < rows and 0 <= move[1] < cols]
			return move_set
		adjusted_set = [Common.diagonal_adjusted(x, y, x_new, y_new, rows, cols) for x_new, y_new in move_set]
		return adjusted_set
	
	@staticmethod
	def check_path_blocked(path: List[Tuple[int, int]], matrix: List[List[int]]) -> bool:
		"""
		Returns True if the current path defined by an algorithm is blocked by a wall

		:param path: Set of coordinates in the matrix
		:param matrix: 2D matrix
		:return: Returns True if the path is blocked, else False
		"""
		for point in path:
			if matrix[point[0]][point[1]]:
				return True
		return False
	
	@staticmethod
	def break_up_edges(matrix, startx, starty, endx, endy, rows, cols):
		"""
		Creates gaps at the borders of the matrix (in-place) at random points

		:param matrix: 2D matrix
		:param startx: Start X coordinate
		:param starty: Start Y coordinate
		:param endx: Last X coordinate
		:param endy: Last Y coordinate
		:param rows: Number of rows in parent matrix
		:param cols: Number of columns in parent matrix
		:return:
		"""
		for im, i in enumerate(range(startx, endx)):
			for jm, j in enumerate(range(starty, endy)):
				if im == 0 or jm == 0 or im == rows - 1 or jm == cols - 1:  # this helps make entry points at the edges of map
					if (im == 0 and matrix[im + 1][jm] == 0 and random.random() < 0.4) or \
						(im == rows - 1 and matrix[im - 1][jm] == 0 and random.random() < 0.4) or \
						(jm == 0 and matrix[im][jm + 1] == 0 and random.random() < 0.4) or \
						(jm == cols - 1 and matrix[im][jm - 1] == 0 and random.random() < 0.4):
						matrix[im][jm] = 0
	
	@staticmethod
	def check_closed_path(matrix: List[List[int]], start_x, start_y) -> Tuple[bool, List[Tuple[int, int]]]:
		"""
		Checks if the given coordinate is in a closed space in the matrix using flood fill

		:param matrix:
		:param start_x:
		:param start_y:
		:return: Tuple of the boolean result, in addition to the set of vertices visited during flood fill
		"""
		if matrix[start_x][start_y] != 0:
			return False, []
		rows, cols = len(matrix), len(matrix[0])
		visited = set()  # To track visited positions
		stack = [(start_x, start_y)]  # Stack for the iterative approach
		directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
		while stack:        # non-recursive implementation
			x, y = stack.pop()
			if (x, y) in visited:
				continue
			visited.add((x, y))
			# Check if we are at the boundary of the map
			if x == 0 or x == rows - 1 or y == 0 or y == cols - 1:
				return False, list(visited)
			# Explore all 4 directions
			for dx, dy in directions:
				new_x, new_y = x + dx, y + dy
				if 0 <= new_x < rows and 0 <= new_y < cols and matrix[new_x][new_y] == 0:
					stack.append((new_x, new_y))
		return True, list(visited)
	
	@staticmethod
	def diagonal_adjusted(x1, y1, x2, y2, rows, cols) -> Tuple[int, int]:
		"""
		Returns adjust coordinates when moving out of the edge of the map at a diagonal
		
		:param x1: Initial X coordinate
		:param y1: Initial Y coordinate
		:param x2: Assumed X coordinate
		:param y2: Assumed Y coordinate
		:param rows: Number of rows in matrix
		:param cols: Number of columns in matrix
		:return:
		"""
		if x2 - x1 == 1 and y2 - y1 == 1:  # SE
			if x1 == rows - 1:
				if y1 > cols / 2:
					y2 += rows
				else:
					x2 = cols // 2 - y1 - 1
					y2 = 0
			elif y1 == cols - 1:
				y2 = cols - x1 - 1
				x2 = 0
		elif x2 - x1 == -1 and y2 - y1 == -1:  # NW
			if x1 == 0:
				if y1 < cols / 2:
					y2 += rows
				else:
					# x = rows - (y1 - cols//2 + 1)
					x2 = cols - y1 - 1
					y2 = cols - 1
			elif y1 == 0:
				y2 = rows - x1 - 1
				x2 = rows - 1
		elif x2 - x1 == 1 and y2 - y1 == -1:  # SW
			if x1 == rows - 1:
				if y1 < cols / 2:
					y2 += rows
				else:
					x2 = rows - (cols - y1)
					y2 = cols - 1
			elif y1 == 0:
				y2 = x1
				x2 = 0
		elif x2 - x1 == -1 and y2 - y1 == 1:  # NE
			if x1 == 0:
				if y1 > cols / 2:
					y2 -= rows
				else:
					x2 = y2 - 1
					y2 = 0
			elif y1 == cols - 1:
				y2 = cols - (rows - x1)
				x2 = rows - 1
		return x2 % rows, y2 % cols
	
	@staticmethod
	def flood_fill(matrix, x, y, visited):
		if x < 0 or x >= len(matrix[0]) or y < 0 or y >= len(matrix) or matrix[y][x] != 0:
			return []
		stack = [(x, y)]
		points = []
		while stack:
			cx, cy = stack.pop()  # Get the current coordinates
			# Skip if this cell is out of bounds or already visited or not a `0`
			if cx < 0 or cx >= len(matrix[0]) or cy < 0 or cy >= len(matrix) or visited[cy][cx] or matrix[cy][cx] != 0:
				continue
			visited[cy][cx] = True  # Mark the cell as visited
			points.append((cx, cy))  # Add the current cell to the list of points
			stack.append((cx + 1, cy))  # Add neighbors to stack
			stack.append((cx - 1, cy))
			stack.append((cx, cy + 1))
			stack.append((cx, cy - 1))
		return points
	
	@staticmethod
	def get_closed_spaces(maze, out):
		"""
		Returns a list of points that are contained within closed spaces in the map
		:param maze: 2D matrix
		:param out: Reference list to return output in (inplace)
		:return:
		"""
		for i in range(len(maze)):
			for j in range(len(maze[0])):
				if (i, j) not in out and maze[i][j] == 0:
					tpl = Common.check_closed_path(maze, i, j)
					if tpl[0]:
						out.extend(tpl[1])
	
	@staticmethod
	def make_map_connected(matrix: List[List[int]], startx, starty, endx, endy, rows, cols):
		"""
		Makes the map represented by the 2d matrix well-connected in-place, with less frequent dead ends and more branches

		:param matrix: 2d matrix
		:param startx: initial X coordinate
		:param starty: initial Y coordinate
		:param endx: last X coordinate to stop at
		:param endy: last Y coordinate to stop at
		:param rows: Number of rows in parent matrix
		:param cols: Number of rows in parent matrix
		"""
		for im, i in enumerate(range(startx, endx)):
			for jm, j in enumerate(range(starty, endy)):
				if im == 0 or jm == 0 or im == rows - 2 or jm == cols - 2:  # this helps make entry points at the edges of map
					if (im == 0 and matrix[im + 1][jm] == 0 and random.random() < 0.4) or \
						(im == rows - 2 and matrix[im - 1][jm] == 0 and random.random() < 0.4) or \
						(jm == 0 and matrix[im][jm + 1] == 0 and random.random() < 0.4) or \
						(jm == cols - 2 and matrix[im][jm - 1] == 0 and random.random() < 0.4):
						matrix[im][jm] = 0
				if matrix[im][jm] == 0:
					count_of_ones = 0  # this is to not create dead ends, make the map well-connected
					neighbors = []
					directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
					for di, dj in directions:
						ni, nj = (im + di) % rows, (jm + dj) % cols
						if 1 <= ni < rows - 2 and 1 <= nj < cols - 2:
							if matrix[ni][nj] == 1:
								count_of_ones += 1
								neighbors.append((ni, nj))  # Store the neighbor's position
					# If there are exactly 3 ones surrounding the 0
					if count_of_ones == 3:
						# Randomly select one neighbor to set to 0
						selected_neighbor = random.choice(neighbors)
						matrix[selected_neighbor[0]][selected_neighbor[1]] = 0
	
	@staticmethod
	def make_map_open(matrix):
		rows, cols = len(matrix), len(matrix[0])
		visited = [[False] * cols for _ in range(rows)]
		# Find all closed spaces (you can modify the starting point as needed)
		for y in range(rows):
			for x in range(cols):
				if matrix[y][x] == 0 and not visited[y][x]:
					closed_space = Common.flood_fill(matrix, x, y, visited)
					# Check if we have a closed space
					if closed_space:
						# Choose an exit point (e.g., the first point found in the closed space)
						exit_point = None
						for (ex, ey) in closed_space:
							# Check the neighbors to find a `1` to turn into a `0`
							if (ex + 1 < cols and matrix[ey][ex + 1] == 1) or \
								(ex - 1 >= 0 and matrix[ey][ex - 1] == 1) or \
								(ey + 1 < rows and matrix[ey + 1][ex] == 1) or \
								(ey - 1 >= 0 and matrix[ey - 1][ex] == 1):
								exit_point = (ex, ey)
								break
						# If an exit point was found, make it open
						if exit_point:
							exit_x, exit_y = exit_point
							# Change one of the bordering `1`s to `0`
							if exit_x + 1 < cols and matrix[exit_y][exit_x + 1] == 1:
								matrix[exit_y][exit_x + 1] = 0
							elif exit_x - 1 >= 0 and matrix[exit_y][exit_x - 1] == 1:
								matrix[exit_y][exit_x - 1] = 0
							elif exit_y + 1 < rows and matrix[exit_y + 1][exit_x] == 1:
								matrix[exit_y + 1][exit_x] = 0
							elif exit_y - 1 >= 0 and matrix[exit_y - 1][exit_x] == 1:
								matrix[exit_y - 1][exit_x] = 0
	
	@staticmethod
	def heuristic(a, b, opt=0):
		return (
			max((abs(a[0] - b[0]), abs(a[1] - b[1]))),  # Chebyshev distance (0)
			abs(a[0] - b[0]) + abs(a[1] - b[1]),  # Manhattan distance (1)
			math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2),  # Euclidean distance (2)
			(math.sqrt(2) - 1) * (abs(a[0] - b[0])) + (abs(a[1] - b[1])) if (abs(a[0] - b[0])) < abs(a[1] - b[1]) else
			(math.sqrt(2) - 1) * (abs(a[1] - b[1])) + abs(a[0] - b[0]),  # Octile distance (3)
			sum(el1 != el2 for el1, el2 in zip(a, b))  # Hamming distance (4)
		)[opt]

	@staticmethod
	def interpolate_color(c1, c2, factor):
		"""Interpolate between two colors."""
		new_color = (
			int(c1[0] + (c2[0] - c1[0]) * factor),
			int(c1[1] + (c2[1] - c1[1]) * factor),
			int(c1[2] + (c2[2] - c1[2]) * factor),
		)
		# Convert to hex format
		return f'#{new_color[0] // 256:02x}{new_color[1] // 256:02x}{new_color[2] // 256:02x}'

class AppException:
	class TargetBlocked(Exception):
		pass
	
	class RanIntoObject(Exception):
		pass
	
	class TargetCaught(Exception):
		pass
	
	class VisualizerPending(Exception):
		pass