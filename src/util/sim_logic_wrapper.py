# from snakesim.src.core.pathfinding import Pathfinding
# from snakesim.src.core.maze_gen import MazeGeneration
from ..core.pathfinding import Pathfinding
from ..core.maze_gen import MazeGeneration

class SimCore(Pathfinding, MazeGeneration):
    def __init__(self, pathfinding: Pathfinding, maze_generation: MazeGeneration):
        self._pathfinding = pathfinding
        self._maze_generation = maze_generation
