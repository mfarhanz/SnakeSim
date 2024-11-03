from typing import List, Tuple
# from snakesim.src.util.common import Common
from src.util.common import Common

class MatrixHelpers:
	@staticmethod
	def block_patterns() -> List[List[List[int]]]:
		"""
		Valid 2x2 block types for representing objects on map; here 0 represents an empty area, 1 represents a filled area

		:return: Set of blocks represented as 2D lists in a list
		"""
		return [
			[[0, 0], [0, 0]], [[1, 0], [0, 0]], [[0, 1], [0, 0]], [[0, 0], [1, 0]], [[0, 0], [0, 1]],
			[[1, 1], [0, 0]], [[0, 0], [1, 1]], [[1, 0], [1, 0]], [[0, 1], [0, 1]],
			[[1, 1], [1, 0]], [[1, 0], [1, 1]], [[0, 1], [1, 1]], [[1, 1], [0, 1]]
		]
	
	@staticmethod
	def get_selection(matrix: List[List[int]], startx, starty, endx, endy) -> List[List[int]]:
		"""
		Gets a 2D selection from the matrix at the specified coordinates

		:param matrix: 2D matrix
		:param startx: Starting X coordinate
		:param starty: Starting Y coordinate
		:param endx: Ending X coordinate
		:param endy: Ending Y coordinate
		:return: Matrix selection specified by the coordinates
		"""
		subset = []
		for qi in range(startx, endx):
			row = []
			for qj in range(starty, endy):
				try:
					row.append(matrix[qi][qj])
				except IndexError:
					continue
			subset.append(row)
		return subset
	
	@staticmethod
	def reconstruct_path(point, forward, backward=None):
		def get_path_section(root, backtrack):
			current = root
			while current is not None:
				path.append(current)
				current = backtrack.get(current)
		
		path = []
		get_path_section(point, forward)
		path.reverse()
		if backward:
			get_path_section(backward.get(point), backward)
		path.reverse()
		return path
	
	@staticmethod
	def check_diagonal_crossing(x, y, i, j, matrix: List[List[int]]) -> bool:
		"""
		Checks if crossing illegally over walls via diagonal moves from current location on map

		:param x: Current X coordinate
		:param y: Current Y coordinate
		:param i: Move index (row number)
		:param j: Move index (column number)
		:param matrix: 2D matrix
		:return: True if moving diagonally from (x,y) to (i,j) is illegal, else False
		"""
		rows, cols = len(matrix), len(matrix[0])
		ret = any([
			all([i - x == 1, j - y == 1, matrix[(x + 1) % rows][y] != 0, matrix[x][(y + 1) % cols] != 0]),
			all([i - x == -1, j - y == -1, matrix[(x - 1) % rows][y] != 0, matrix[x][(y - 1) % cols] != 0]),
			all([i - x == 1, j - y == -1, matrix[(x + 1) % rows][y] != 0, matrix[x][(y - 1) % cols] != 0]),
			all([i - x == -1, j - y == 1, matrix[(x - 1) % rows][y] != 0, matrix[x][(y + 1) % cols] != 0])
		])
		return ret
