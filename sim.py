import src.snake_sim
import src.util.sim_global
import src.util.sim_logic_wrapper

if __name__ == '__main__':
	configuration = src.util.sim_global.SimConfig()
	hardcoded = src.util.sim_global.SimData()
	state_variable_reference = src.util.sim_global.SimState()
	finders = src.core.pathfinding.Pathfinding()
	generators = src.core.maze_gen.MazeGeneration()
	core_logic = src.util.sim_logic_wrapper.SimCore(finders, generators)
	src.snake_sim.SnakeSim(configuration, state_variable_reference, hardcoded, core_logic)
