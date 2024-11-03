import collections
import math
import random
import heapq
from typing import List, Tuple
# from snakesim.src.util.common import Common
# from snakesim.src.util.matrix_helpers import MatrixHelpers
from ..util.common import Common
from ..util.matrix_helpers import MatrixHelpers

class Pathfinding:
    def random_step(self, start, matrix, wraparound=False, all_directional=False) -> List[Tuple[int, int]]:
        """
        Random walk algorithm implementation

        :param start: Current coordinate
        :param matrix: 2D matrix
        :param wraparound: Wrap from end-to-end when at edges or corners in matrix
        :param all_directional: Use neighbors from all 8-directions or standard 4-directions
        :return: Next move from current coordinate as a coordinate tuple
        """
        x, y = start
        rows, cols = len(matrix), len(matrix[0])
        move_lst = [(i, j) for (i, j) in Common.valid_moves(x, y, rows, cols, wraparound, all_directional)
                    if not matrix[i][j] and not MatrixHelpers.check_diagonal_crossing(x, y, i, j, matrix)]
        move_wt_lookup = {Common.diagonal_adjusted(x, y, (x - 1), (y - 1), rows, cols): 0.2,
                          Common.diagonal_adjusted(x, y, (x - 1), y, rows, cols): 0.8,
                          Common.diagonal_adjusted(x, y, (x - 1), (y + 1), rows, cols): 0.2,
                          Common.diagonal_adjusted(x, y, x, (y - 1), rows, cols): 0.8,
                          Common.diagonal_adjusted(x, y, x, (y + 1), rows, cols): 0.8,
                          Common.diagonal_adjusted(x, y, (x + 1), (y - 1), rows, cols): 0.2,
                          Common.diagonal_adjusted(x, y, (x + 1), y, rows, cols): 0.8,
                          Common.diagonal_adjusted(x, y, (x + 1), (y + 1), rows, cols): 0.2}
        wt_lst = [move_wt_lookup[coord] for coord in move_lst]
        return random.choices(population=move_lst, weights=wt_lst, k=1)[0]

    def depth_first_search(self, start, target, matrix, wraparound=False, all_directional=False, bidirectional=False):
        """
        Returns list of coordinates representing the best path to target in a matrix of shape (rows, cols)
        using the Depth First Search algorithm

        :param start: Start coordinate
        :param target: Target coordinate
        :param matrix: 2D matrix
        :param wraparound: Wrap symmetrically from end-to-end when at edges or corners in matrix
        :param all_directional: Use neighbors from all 8-directions or standard 4-directions
        :param bidirectional: Run algorithm bidirectionally (forward and backward pass) or not
        :return: List of coordinates representing the best path to target
        """
        def dfs_step(goal, stack, visited, nonvisited, backtrack):
            nonlocal found
            current = stack.pop()       # get from the end
            for x, y in Common.valid_moves(current[0], current[1], rows, cols, wraparound, all_directional):
                if not matrix[x][y] and (x, y) not in visited and not MatrixHelpers.check_diagonal_crossing(current[0], current[1], x, y, matrix):
                    visited.add(current)
                    stack.append((x, y))
                    backtrack[(x, y)] = current
                    visited_ordered.append((x, y))
                    if (x, y) == goal or (x, y) in nonvisited:
                        found = True
                        path.extend(MatrixHelpers.reconstruct_path((x, y), fwd_backtrack, bwd_backtrack))
                        return
    
        found = False
        rows, cols = len(matrix), len(matrix[0])
        target = tuple(target)
        visited_ordered = []
        fwd_visited, bwd_visited = set(), set()
        fwd_backtrack, bwd_backtrack = {}, {}
        fwd_stack, bwd_stack, path = [start], [target], []
        if bidirectional:
            while (fwd_stack or bwd_stack) and not found:
                dfs_step(target, fwd_stack, fwd_visited, bwd_visited, fwd_backtrack)
                if not found:
                    dfs_step(start, bwd_stack, bwd_visited, fwd_visited, bwd_backtrack)
        else:
            while fwd_stack and not found:
                dfs_step(target, fwd_stack, fwd_visited, bwd_visited, fwd_backtrack)
        return path, visited_ordered

    def breadth_first_search(self, start, target, matrix, wraparound=False, all_directional=False, bidirectional=False):
        """
        Returns list of coordinates representing the best path to target in a matrix of shape (rows, cols)
        using the Breadth First Search algorithm

        :param start: Start coordinate
        :param target: Target coordinate
        :param matrix: 2D matrix
        :param wraparound: Wrap symmetrically from end-to-end when at edges or corners in matrix
        :param all_directional: Use neighbors from all 8-directions or standard 4-directions
        :param bidirectional: Run algorithm bidirectionally (forward and backward pass) or not
        :return: List of coordinates representing the best path to target
        """
        def bfs_step(goal, q, visited, nonvisited, backtrack):
            nonlocal found
            current = q.pop(0)  # get from the start instead of end (this is literally the only difference from DFS)
            for x, y in Common.valid_moves(current[0], current[1], rows, cols, wraparound, all_directional):
                if not matrix[x][y] and (x, y) not in visited and not MatrixHelpers.check_diagonal_crossing(current[0], current[1], x, y, matrix):
                    visited.add((x, y))
                    q.append((x, y))
                    backtrack[(x, y)] = current
                    visited_ordered.append((x, y))
                    if (x, y) == goal or (x, y) in nonvisited:
                        found = True
                        path.extend(MatrixHelpers.reconstruct_path((x, y), fwd_backtrack, bwd_backtrack))
                        return
    
        found = False
        rows, cols = len(matrix), len(matrix[0])
        target = tuple(target)
        visited_ordered = []
        fwd_visited, bwd_visited = set(), set()
        fwd_queue, bwd_queue, path = [start], [target], []
        fwd_backtrack, bwd_backtrack = {}, {}
        fwd_visited.add(start)
        if bidirectional:
            bwd_visited.add(target)
            while (fwd_queue or bwd_queue) and not found:
                bfs_step(target, fwd_queue, fwd_visited, bwd_visited, fwd_backtrack)
                if not found:
                    bfs_step(start, bwd_queue, bwd_visited, fwd_visited, bwd_backtrack)
        else:
            while fwd_queue and not found:
                bfs_step(target, fwd_queue, fwd_visited, bwd_visited, fwd_backtrack)
        return path, visited_ordered

    def greedy_best_first_search(self, start, target, matrix, wraparound=False, all_directional=False, bidirectional=False, heuristic=0):
        """
        Returns list of coordinates representing the best path to target in a matrix of shape (rows, cols)
        using a Greedy Best First Search algorithm

        :param start: Start coordinate
        :param target: Target coordinate
        :param matrix: 2D matrix
        :param wraparound: Wrap symmetrically from end-to-end when at edges or corners in matrix
        :param all_directional: Use neighbors from all 8-directions or standard 4-directions
        :param bidirectional: Run algorithm bidirectionally (forward and backward pass) or not
        :param heuristic: Distance metric used
        :return: List of coordinates representing the best path to target
        """
        def greedy_best_first_step(goal, pq, visited, nonvisited, backtrack):
            nonlocal found
            _, current = heapq.heappop(pq)
            for x, y in Common.valid_moves(current[0], current[1], rows, cols, wraparound, all_directional):
                if not matrix[x][y] and (x, y) not in visited and not MatrixHelpers.check_diagonal_crossing(current[0], current[1], x, y, matrix):
                    visited.add((x, y))
                    backtrack[(x, y)] = current
                    visited_ordered.append((x, y))
                    cost = 1 if x - current[0] == 0 or y - current[1] == 0 else math.sqrt(2)
                    heapq.heappush(pq, (cost + Common.heuristic((x, y), goal, heuristic), (x, y)))
                    if (x, y) == goal or (x, y) in nonvisited:
                        found = True
                        path.extend(MatrixHelpers.reconstruct_path((x, y), fwd_backtrack, bwd_backtrack))
                        return
    
        found = False
        rows, cols = len(matrix), len(matrix[0])
        target = tuple(target)
        visited_ordered = []
        fwd_pq, bwd_pq, path = [], [], []
        fwd_visited, bwd_visited = set(), set()
        fwd_backtrack, bwd_backtrack = {}, {}
        fwd_visited.add(start)
        heapq.heappush(fwd_pq, (0, start))
        if bidirectional:
            bwd_visited.add(target)
            heapq.heappush(bwd_pq, (0, target))
            while (fwd_pq or bwd_pq) and not found:
                greedy_best_first_step(target, fwd_pq, fwd_visited, bwd_visited, fwd_backtrack)
                if not found:
                    greedy_best_first_step(start, bwd_pq, bwd_visited, fwd_visited, bwd_backtrack)
        else:
            while fwd_pq and not found:
                greedy_best_first_step(target, fwd_pq, fwd_visited, bwd_visited, fwd_backtrack)
        return path, visited_ordered

    def a_star(self, start, target, matrix, wraparound=False, all_directional=False, bidirectional=False, heuristic=0):
        """
        Returns list of coordinates representing the best path to target in a matrix of shape (rows, cols)
        using the A* pathfinding algorithm

        :param start: Start coordinate
        :param target: Target coordinate
        :param matrix: 2D matrix
        :param wraparound: Wrap symmetrically from end-to-end when at edges or corners in matrix
        :param all_directional: Use neighbors from all 8-directions or standard 4-directions
        :param bidirectional: Run algorithm bidirectionally (forward and backward pass) or not
        :param heuristic: Distance metric used
        :return: List of coordinates representing the best path to target
        """
        def a_star_step(goal, pq, visited, nonvisited, gscore, backtrack):
            nonlocal found
            _, current = heapq.heappop(pq)
            visited.add(current)
            for x, y in Common.valid_moves(current[0], current[1], rows, cols, wraparound, all_directional):
                if not matrix[x][y] and not MatrixHelpers.check_diagonal_crossing(current[0], current[1], x, y, matrix):
                    assumed = gscore[current] + (1 if x - current[0] == 0 or y - current[1] == 0 else math.sqrt(2))  # +1 for sides, +1.41 for diagonals
                    if assumed < gscore[(x, y)]:
                        gscore[(x, y)] = assumed
                        backtrack[(x, y)] = current
                        visited_ordered.append((x, y))
                        heapq.heappush(pq, (assumed + Common.heuristic((x, y), goal, heuristic), (x, y)))
                    if (x, y) == goal or (x, y) in nonvisited:
                        found = True
                        path.extend(MatrixHelpers.reconstruct_path((x, y), fwd_backtrack, bwd_backtrack))
                        return
    
        found = False
        rows, cols = len(matrix), len(matrix[0])
        target = tuple(target)
        fwd_gscore = {(i, j): float('inf') for i in range(rows) for j in range(cols)}
        bwd_gscore = {(i, j): float('inf') for i in range(rows) for j in range(cols)}
        visited_ordered = []
        fwd_pq, bwd_pq, path = [], [], []
        fwd_visited, bwd_visited = set(), set()
        fwd_backtrack, bwd_backtrack = {}, {}
        fwd_gscore[start] = 0
        heapq.heappush(fwd_pq, (Common.heuristic(start, target, heuristic), start))
        if bidirectional:
            bwd_gscore[target] = 0
            heapq.heappush(bwd_pq, (Common.heuristic(target, start, heuristic), target))
            while (fwd_pq or bwd_pq) and not found:
                a_star_step(target, fwd_pq, fwd_visited, bwd_visited, fwd_gscore, fwd_backtrack)
                if not found:
                    a_star_step(start, bwd_pq, bwd_visited, fwd_visited, bwd_gscore, bwd_backtrack)
        else:
            while fwd_pq and not found:
                a_star_step(target, fwd_pq, fwd_visited, bwd_visited, fwd_gscore, fwd_backtrack)
        return path, visited_ordered

    def dijkstra(self, start, target, matrix, wraparound=False, all_directional=False, bidirectional=False):
        """
        Returns list of coordinates representing the best path to target in a matrix of shape (rows, cols)
        using Dijkstra's pathfinding algorithm

        :param start: Start coordinate
        :param target: Target coordinate
        :param matrix: 2D matrix
        :param wraparound: Wrap symmetrically from end-to-end when at edges or corners in matrix
        :param all_directional: Use neighbors from all 8-directions or standard 4-directions
        :param bidirectional: Run algorithm bidirectionally (forward and backward pass) or not
        :return: List of coordinates representing the best path to target
        """
    
        def dijkstra_step(goal, pq, visited, nonvisited, gscore, backtrack):
            nonlocal found
            dist, current = heapq.heappop(pq)
            visited.add(current)
            for x, y in Common.valid_moves(current[0], current[1], rows, cols, wraparound, all_directional):
                if not matrix[x][y] and not MatrixHelpers.check_diagonal_crossing(current[0], current[1], x, y, matrix):
                    cost = dist + (1 if x - current[0] == 0 or y - current[1] == 0 else math.sqrt(2))
                    if cost < gscore[(x, y)]:
                        gscore[(x, y)] = cost
                        backtrack[(x, y)] = current
                        visited_ordered.append((x, y))
                        heapq.heappush(pq, (cost, (x, y)))
                    if (x, y) == goal or (x, y) in nonvisited:
                        found = True
                        path.extend(MatrixHelpers.reconstruct_path((x, y), fwd_backtrack, bwd_backtrack))
                        return
    
        found = False
        rows, cols = len(matrix), len(matrix[0])
        target = tuple(target)
        fwd_gscore = {(i, j): float('inf') for i in range(rows) for j in range(cols)}
        bwd_gscore = {(i, j): float('inf') for i in range(rows) for j in range(cols)}
        visited_ordered = []
        fwd_pq, bwd_pq, path = [], [], []
        fwd_visited, bwd_visited = set(), set()
        fwd_backtrack, bwd_backtrack = {}, {}
        fwd_gscore[start] = 0
        heapq.heappush(fwd_pq, (0, start))
        if bidirectional:
            bwd_gscore[target] = 0
            heapq.heappush(bwd_pq, (0, target))
            while (fwd_pq or bwd_pq) and not found:
                dijkstra_step(target, fwd_pq, fwd_visited, bwd_visited, fwd_gscore, fwd_backtrack)
                if not found:
                    dijkstra_step(start, bwd_pq, bwd_visited, fwd_visited, bwd_gscore, bwd_backtrack)
        else:
            while fwd_pq and not found:
                dijkstra_step(target, fwd_pq, fwd_visited, bwd_visited, fwd_gscore, fwd_backtrack)
        return path, visited_ordered

    # https://en.wikipedia.org/wiki/Fringe_search
    def fringe_search(self, start, target, matrix, wraparound=False, all_directional=False, bidirectional=False, heuristic=0):
        """
        Returns list of coordinates representing the best path to target in a matrix of shape (rows, cols)
        using the Fringe Search algorithm

        :param start: Start coordinate
        :param target: Target coordinate
        :param matrix: 2D matrix
        :param wraparound: Wrap symmetrically from end-to-end when at edges or corners in matrix
        :param all_directional: Use neighbors from all 8-directions or standard 4-directions
        :param bidirectional: Run algorithm bidirectionally (forward and backward pass) or not
        :param heuristic: Distance metric used
        :return: List of coordinates representing the best path to target
        """
    
        def fringe_step(goal, fringe, visited, nonvisited, cache, flimit):
            nonlocal found, meeting_point
            fmin = float('inf')
            for node in fringe:
                g, parent = cache[node]
                f = g + Common.heuristic(node, goal, heuristic)
                visited.add(node)
                if f > flimit:
                    fmin = min(f, fmin)
                    continue
                if node == goal or node in nonvisited:
                    found = True
                    meeting_point = node
                    return
                for x, y in Common.valid_moves(node[0], node[1], rows, cols, wraparound, all_directional)[::-1]:
                    if not matrix[x][y] and not MatrixHelpers.check_diagonal_crossing(node[0], node[1], x, y, matrix):
                        g_child = g + (1 if x - node[0] == 0 or y - node[1] == 0 else math.sqrt(2))
                        if (x, y) in cache:
                            if cache[(x, y)]:
                                g_cached, parent = cache[(x, y)]
                                if g_child >= g_cached:
                                    continue
                        if (x, y) in fringe:
                            fringe.remove((x, y))
                        fringe.append((x, y))
                        cache[(x, y)] = (g_child, node)
                        visited_ordered.append((x, y))
                fringe.remove(node)
            flimit = fmin
            return flimit
    
        found = False
        target = tuple(target)
        meeting_point = None
        rows, cols = len(matrix), len(matrix[0])
        fwd_fringe, bwd_fringe, path = [start], [target], []
        visited_ordered = []
        fwd_visited, bwd_visited = set(), set()
        fwd_cache, bwd_cache = {start: (0, None)}, {target: (0, None)}
        fwd_flimit, bwd_flimit = Common.heuristic(start, target, heuristic), Common.heuristic(target, start, heuristic)
        if bidirectional:
            while (fwd_fringe or bwd_fringe) and not found:
                fwd_flimit = fringe_step(target, fwd_fringe, fwd_visited, bwd_visited, fwd_cache, fwd_flimit)
                if not found:
                    bwd_flimit = fringe_step(start, bwd_fringe, bwd_visited, fwd_visited, bwd_cache, bwd_flimit)
        else:
            while fwd_fringe and not found:
                fwd_flimit = fringe_step(target, fwd_fringe, fwd_visited, bwd_visited, fwd_cache, fwd_flimit)
        if found:
            fwd_cache = {key: value[1] for key, value in fwd_cache.items()}
            bwd_cache = {key: value[1] for key, value in bwd_cache.items()}
            path.extend(MatrixHelpers.reconstruct_path(meeting_point, fwd_cache, bwd_cache))
        return path, visited_ordered

    def bellman_ford(self, start, target, matrix, wraparound=False, all_directional=False, bidirectional=False):
        """
        Returns list of coordinates representing the best path to target in a matrix of shape (rows, cols)
        using the Bellman-Ford algorithm

        Normally, this algorithm uses a third step to deal with 'negative cycles', or infinite loops while backtracking
        due to negative weights in a weighted matrix/graph; since there are no negative weights in the matrices used
        here, this step is not used.

        :param start: Start coordinate
        :param target: Target coordinate
        :param matrix: 2D matrix
        :param wraparound: Wrap symmetrically from end-to-end when at edges or corners in matrix
        :param all_directional: Use neighbors from all 8-directions or standard 4-directions
        :param bidirectional: Run algorithm bidirectionally (forward and backward pass) or not
        :return: List of coordinates representing the best path to target
        :return:
        """
    
        def check_cardinal(a, b):
            dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
            return (dx == 1 and dy == 0) or (dx == 0 and dy == 0)
    
        def relax_step(goal, queue, visited, nonvisited, dists, backtrack):
            nonlocal ctr, found
            ctr += 1  # Relaxation step
            u = queue.popleft()
            visited.add(u)
            for v in Common.valid_moves(u[0], u[1], rows, cols, wraparound, all_directional):
                if not matrix[v[0]][v[1]] and not MatrixHelpers.check_diagonal_crossing(u[0], u[1], v[0], v[1], matrix):
                    w = 1 if check_cardinal(v, u) else math.sqrt(2)
                    if dists[u] + w < dists[v]:
                        dists[v] = dists[u] + w
                        backtrack[v] = u
                        queue.append(v)
                        visited_ordered.append(v)
                    if v == goal or v in nonvisited:
                        found = True
                        path.extend(MatrixHelpers.reconstruct_path(v, fwd_backtrack, bwd_backtrack))
                        return
    
        found = False
        rows, cols = len(matrix), len(matrix[0])
        target = tuple(target)
        fwd_dists = {(i, j): float('inf') for i in range(rows) for j in range(cols)}
        bwd_dists = {(i, j): float('inf') for i in range(rows) for j in range(cols)}
        fwd_relax_queue, bwd_relax_queue = collections.deque([start]), collections.deque([target])
        fwd_backtrack, bwd_backtrack = {start: None}, {}
        visited_ordered = []
        fwd_visited, bwd_visited = set(), set()
        fwd_dists[start], bwd_dists[target] = 0, 0
        edges, path = [], []
        ctr = 0
        for x in range(rows):  # Get edges with weights
            for y in range(cols):
                for nx, ny in Common.valid_moves(x, y, rows, cols, wraparound, all_directional):
                    if not matrix[nx][ny] and not MatrixHelpers.check_diagonal_crossing(x, y, nx, ny, matrix):
                        edges.append((1 if check_cardinal((nx, ny), (x, y)) else math.sqrt(2), (x, y), (nx, ny)))
        if bidirectional:
            bwd_backtrack[target] = None
            while (fwd_relax_queue or bwd_relax_queue) and not found:
                relax_step(target, fwd_relax_queue, fwd_visited, bwd_visited, fwd_dists, fwd_backtrack)
                if not found:
                    relax_step(start, bwd_relax_queue, bwd_visited, fwd_visited, bwd_dists, bwd_backtrack)
        else:
            while fwd_relax_queue and not found:
                relax_step(target, fwd_relax_queue, fwd_visited, bwd_visited, fwd_dists, fwd_backtrack)
        return path, visited_ordered



    # https://en.wikipedia.org/wiki/Iterative_deepening_A*
    # since this is recursive, only good for small matrices
    # current implementation of the algorithm is very error prone, and goes into infinite loops often or when 4-directions are used
    def iterative_deepening_a_star(self, start, target, matrix, wraparound=False, all_directional=False, bidirectional=False, heuristic=0):
        """
        Returns list of coordinates representing the best path to target in a matrix of shape (rows, cols)
        using the Iterative Deepening A* path search algorithm (A* variant)
        
        :param start: Start coordinate
        :param target: Target coordinate
        :param matrix: 2D matrix
        :param wraparound: Wrap symmetrically from end-to-end when at edges or corners in matrix
        :param all_directional: Use neighbors from all 8-directions or standard 4-directions
        :return: List of coordinates representing the best path to target
        """
        def threshold_dfs(path, g, threshold):
            current = path[-1]
            f = g + Common.heuristic(current, target, heuristic)
            if f > threshold:
                return f
            if current == tuple(target):
                return True
            min_cost = float('inf')
            neighbors = Common.valid_moves(current[0], current[1], rows, cols, wraparound, all_directional)
            costs = [g + 1 + Common.heuristic(node, target, heuristic) for node in neighbors]
            ordered_neighbors = [neighbor for _, neighbor in sorted(zip(costs, neighbors))]
            for x, y in ordered_neighbors:
                if (x, y) not in path and not matrix[x][y]: # and not MatrixHelpers.check_diagonal_crossing(current[0], current[1], x, y, matrix):
                    path.append((x, y))
                    visited_ordered.append((x, y))
                    t = threshold_dfs(path, g + 1, threshold)
                    if t is True:
                        return True
                    if t < min_cost:
                        min_cost = t
                    path.pop()  # Keep pruning list till we have a path
            return min_cost
        
        rows, cols = len(matrix), len(matrix[0])
        bound = Common.heuristic(start, target, heuristic)
        path = [start]
        visited_ordered = []
        while True:
            next_thresh = threshold_dfs(path, 0, bound)
            if next_thresh is True or next_thresh == float('inf'):
                break
            bound = next_thresh
        return path[::-1], visited_ordered
