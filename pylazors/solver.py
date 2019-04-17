"""
This file contains board solving functions

User should only use solve_board() in this file. It will automatically choose the best
solving algorithm and use it to solve given board.
"""

from itertools import combinations, product
from math import factorial
import numpy as np
import random
import time
from pylazors.block import *
from pylazors.formats.bff import bff_block_map, block_bff_map
from pylazors._solver import _solve_large_board, _trace_lasers


def _solve_board(board, solve_limit=1E5):
    """
    lazor (game) solver

    **Parameters**

        board: *pylazors.Board object*

        solve_limit: *optional, integer*
            the maximum number of combinations allowed. if exceeded, the function
            returns None. if 0 -> no limit.

    **Returns**

        solution_board: *pylazors.Board object*
            board for the solved maze
    """

    # Translate pylazors.Board to data
    letter_grid = np.array([[block_bff_map[block] for block in row] for row in board.get_blocks()])
    blocks = [block_bff_map[fix_block(block)] for block in board.get_available_blocks()]
    lazers = [list(map(str, l)) for l in board.get_laser_sources()]
    points = [list(map(str, p)) for p in board.get_targets()]
    block_counts = list(map(lambda b: board.get_available_blocks().count(b), [Block.REFLECT, Block.OPAQUE, Block.REFRACT]))

    # load data and count number of available positions
    # letter_grid, blocks, lazers, points, block_counts = data
    available_positions = get_available_positions(letter_grid)

    # calculate the number of moveable blocks and available positions [debug]
    n_blocks, n_pos = len(blocks), len(available_positions)
    # calculate the number of unique combinations or possible combinations
    unique_combinations = factorial(n_pos) / (factorial(n_pos - n_blocks) * factorial(block_counts[0]) * factorial(block_counts[1]) * factorial(block_counts[2]))

    if unique_combinations > solve_limit and solve_limit != 0:
        print("[solve_board] skipped: too many combinations! (%i)" % unique_combinations)
        return None

    unique_blocks = 0

    for bc in block_counts:
        if bc > 0:
            unique_blocks += 1

    # if the number of block types is 1, use combinations, otherwise use the modified functions
    if unique_blocks == 1:
        t0 = time.time()
        possible_combs = [zip(blocks, x) for x in combinations(available_positions, len(blocks))]
        print("[solve_board] %i combinations generated in %.3f s" % (len(possible_combs), time.time() - t0))
    elif unique_blocks > 1:
        t0 = time.time()
        possible_combs = get_possible_combs_perm(blocks, available_positions)
        print("[solve_board] %i permutations generated in %.3f s" % (len(possible_combs), time.time() - t0))

    iter_num = 1
    # Iterate a random combination each time and turn lazor on
    for comb_number in range(len(possible_combs)):
        comb_ind = random.randint(0, len(possible_combs) - 1)
        comb = possible_combs.pop(comb_ind)

        i_grid = []
        i_grid = letter_grid.copy()

        for blk in comb:
            i_grid[blk[1][1]][blk[1][0]] = blk[0]

        data_grid = get_data_grid(i_grid, points)
        data_grid_w_lazer_on = lazor_on(data_grid, lazers)

        # stop if solution is found [if no 9 is in data_grid]
        if not any([point == 9 for row in data_grid_w_lazer_on for point in row]):
            print("[solve_board] Solution found in %i iterations" % (iter_num))
            solution_board = board.copy()
            for x in range(board.width):
                for y in range(board.height):
                    if board.get_block(x, y) != bff_block_map[i_grid[y][x]]:
                        solution_board.mod_block(x, y, unfix_block(bff_block_map[i_grid[y][x]]))
            laser_segments = _trace_lasers(solution_board.get_blocks(), solution_board.get_laser_sources())
            solution_board.load_laser_segments(laser_segments)
            return solution_board

        iter_num += 1

    print("[solve_board] No solution found!")


def get_possible_combs_perm(blocks, available_positions):
    '''
    unique combinations generator. This function still generates similar
    combinations

    **Parameters**

        blocks: *list*
            list of moveable blocks letters

        available_positions: *list*
            list of (x, y) coordinates of available positions

    **Returns**

        possible_combs: *list*{*list*{*string*, *tulpe*}}
            list of all possible combinations of letters in available positions
    '''
    num_avail_blocks = len(blocks)

    i_perm = []
    for i in range(num_avail_blocks):
        i_comb = [blocks[i], available_positions]
        i_perm.append(product(* i_comb))

    j_perm = product(* i_perm)
    j_perm = {frozenset(j) for j in j_perm}
    j_perm = [list(i) for i in j_perm]

    possible_combs = j_perm

    # below is used to eliminate identical combination with diffirent sorting
    # by sorting them. However, it is time consuming compared to iterating through
    # the solver
    #
    # t0 = time.time()
    # for comb in j_perm:
    #     if len(comb) == num_avail_blocks:
    #         comb = sorted(comb, key=itemgetter(0, 1))
    #         if comb not in possible_combs:
    #             possible_combs.append(comb)
    # print("   k_perm time: %.5f seconds" % (time.time() - t0))

    return possible_combs


def get_available_positions(letter_grid):
    """
    From a letter grid, this function extracts avilable positions for a
    moveable block to be placed at.

    **Parameters**

        letter_grid: *np.array*
            letter grid generated by lazor_load function

    **Returns**

        available_positions: *list, tuples, (x, y)*
            a list of all avaiable positions in (x, y) coordinates
    """

    available_positions = []
    for j in range(len(letter_grid)):
        for i in range(len(letter_grid[0])):
            if letter_grid[j][i] == 'o':
                available_positions.append((i, j))
    return available_positions


def get_data_grid(letter_grid, points):
    """
    Convert letter grid into data grid and include target points.

    **Parameters**

        letter_grid: *np.array*
            letter grid generated by lazor_load function

        points: *list*
            list of target points obtained by lazor_load function

    **Returns**

        data_grid: *np.array*
            converted data grid

    **Example**
        inputs:
            letter_grid = [['o' 'o' 'A' 'o' 'o']
                           ['o' 'o' 'o' 'A' 'o']
                           ['A' 'o' 'A' 'o' 'x']
                           ['o' 'o' 'o' 'A' 'o']
                           ['o' 'o' 'A' 'o' 'o']]

            points = [['6', '3'], ['6', '5'], ['6', '7'], ['2', '9'], ['9', '6']]

        returns:

            data_grid = [[ 0.  0.  0.  0.  2.  2.  2.  0.  0.  0.  0.]
                         [ 0.  0.  0.  0.  2.  2.  2.  0.  0.  0.  0.]
                         [ 0.  0.  0.  0.  2.  2.  2.  2.  2.  0.  0.]
                         [ 0.  0.  0.  0.  0.  0.  9.  2.  2.  0.  0.]
                         [ 2.  2.  2.  0.  2.  2.  2.  2.  2.  0.  0.]
                         [ 2.  2.  2.  0.  2.  2.  9.  0.  0.  0.  0.]
                         [ 2.  2.  2.  0.  2.  2.  2.  2.  2.  9.  0.]
                         [ 0.  0.  0.  0.  0.  0.  9.  2.  2.  0.  0.]
                         [ 0.  0.  0.  0.  2.  2.  2.  2.  2.  0.  0.]
                         [ 0.  0.  9.  0.  2.  2.  2.  0.  0.  0.  0.]
                         [ 0.  0.  0.  0.  2.  2.  2.  0.  0.  0.  0.]]

    """
    x_dim, y_dim = 2 * len(letter_grid) + 1, 2 * len(letter_grid[0]) + 1
    data_grid = np.zeros(shape=(x_dim, y_dim))
    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
        (-1, -1),
        (-1, 1),
        (1, -1),
        (1, 1)]

    for j in range(len(letter_grid)):
        for i in range(len(letter_grid[0])):
            x, y = 2 * i + 1, 2 * j + 1
            block = letter_grid[j][i]
            neighbors = [(x + direction[0], y + direction[1]) for direction in directions]
            if block == "A":
                data_grid[y, x] = 2
                for neighbor in neighbors:
                    val = data_grid[neighbor[1], neighbor[0]]
                    if val != 4:
                        data_grid[neighbor[1], neighbor[0]] = 2
            if block == "B":
                data_grid[y, x] = 4
                for neighbor in neighbors:
                    data_grid[neighbor[1], neighbor[0]] = 4
            if block == "C":
                data_grid[y, x] = 6
                for neighbor in neighbors:
                    val = data_grid[neighbor[1], neighbor[0]]
                    if (val != 4 or val != 2):
                        data_grid[neighbor[1], neighbor[0]] = 6

    for point in points:
            data_grid[int(point[1]), int(point[0])] = 9

    return data_grid


def lazor_on(data_grid, lazers, MAXITER=100):
    """
    lazor solver algorithm. The algorithm works by taking the data grid and iterate
        through each laser pointer. For each laser:
                - Determine if the incident position is on the side or top of block.
                  This is done to set the reflection of the laser (its direction)
                - Determine the neighbor block position and its type. To escape laser
                  trapping.
                - Based on the incident and other positions and their type, take action
                  as described below.

    **Parameters**

        x: *int*
            An x coordinate to check if it resides within the maze.
        y: *int*
            A y coordinate to check if it resides within the maze.
        nBlocks: *int*
            How many blocks wide the maze is.  Should be equivalent to
            the length of the maze (ie. len(maze)).

    **Returns**

        valid: *bool*
            Whether the coordiantes are valid (True) or not (False).
    """

    laz_grid = data_grid.copy()
    lazs = list(lazers)

    for lazer in lazs:
        pos = [int(lazer[0]), int(lazer[1])]
        lazer_vector = [int(lazer[2]), int(lazer[3])]
        i = 0
        while i < MAXITER:
            # determine if on side or t/b
            # in each case, get the values of neighbors' center of blocks
            # proceed according to the values (i.e. 2, 4, 6)
            # where (2)     reflects to one direction
            #       (4)     blocks the lazer
            #       (6)     passes throght in its direction and relects in another
            #                   (additional lazer must be generated???)

            # loc = 0 (side of block), loc = 1 (top or bottom of block)
            if not pos_chk(pos[0], pos[1], data_grid):
                # break the while loop (turn off lazer) once exceeding the bound.
                break
            pos_val = data_grid[pos[1], pos[0]]
            if pos_val == 9:
                laz_grid[pos[1], pos[0]] = -1
            elif pos_val == 0:
                laz_grid[pos[1], pos[0]] = 8

            if (pos[0] % 2) == 0:
                # Side (check ONLY right or left neighbor based on direction)
                reflection = 0
                incident_pos = [pos[0] + lazer_vector[0], pos[1]]
                other_pos = [pos[0] - lazer_vector[0], pos[1]]

            elif (pos[1] % 2) == 0:
                # Top or Bottom
                reflection = 1
                incident_pos = [pos[0], pos[1] + lazer_vector[1]]
                other_pos = [pos[0], pos[1] - lazer_vector[1]]

            if not pos_chk(incident_pos[0], incident_pos[1], data_grid):
                # break the while loop (turn off lazer) once exceeding the bound.
                break
            incident_pos_val = data_grid[incident_pos[1], incident_pos[0]]

            # check the position of other block if valid, and get its value or set 0
            if pos_chk(other_pos[0], other_pos[1], data_grid):
                other_pos_val = data_grid[other_pos[1], other_pos[0]]
            else:
                other_pos_val = 0

            # if passable block, pass light to next position in direction
            if incident_pos_val == 0:
                pos = [pos[0] + lazer_vector[0], pos[1] + lazer_vector[1]]
            # if reflection block, reflect lazer
            elif incident_pos_val == 2:
                # if lazer is trapped between two reflection blocks, stop lazer
                if (other_pos_val == 2 or other_pos_val == 4):
                    break
                lazer_vector[reflection] = -1 * lazer_vector[reflection]
                pos = [pos[0] + lazer_vector[0], pos[1] + lazer_vector[1]]
            # if opaque block, stop lazer
            elif incident_pos_val == 4:
                break
            # if refreact block, refract lazer
            elif incident_pos_val == 6:
                # if other block is reflection block, only pass through
                if (other_pos_val == 2 or other_pos_val == 4):
                    pos = [pos[0] + lazer_vector[0], pos[1] + lazer_vector[1]]
                # otherwise, passthrough lazer, and add additional reflection lazer
                else:
                    lazer_vector_temp = list(lazer_vector)
                    lazer_vector_temp[reflection] = -1 * lazer_vector_temp[reflection]
                    lz_ref = [pos[0], pos[1], lazer_vector_temp[0], lazer_vector_temp[1]]
                    if lz_ref not in lazs:
                        lazs.append(lz_ref)
                    pos = [pos[0] + lazer_vector[0], pos[1] + lazer_vector[1]]
            # print(laz_grid)
            i += 1

    return laz_grid


def pos_chk(x, y, data_grid):
    """
    Validate if the coordinates specified (x and y) are within the maze.

    **Parameters**

        x: *int*
            An x coordinate to check if it resides within the maze.
        y: *int*
            A y coordinate to check if it resides within the maze.
        nBlocks: *int*
            How many blocks wide the maze is.  Should be equivalent to
            the length of the maze (ie. len(maze)).

    **Returns**

        valid: *bool*
            Whether the coordiantes are valid (True) or not (False).
    """

    # x_dim, y_dim = 2 * len(grid[0]) + 1, 2 * len(grid) + 1
    x_dim, y_dim = len(data_grid[0, :]), len(data_grid[:, 0])
    # print(x_dim, y_dim)
    return x >= 0 and x < x_dim and y >= 0 and y < y_dim


def solve_board(board, **kwargs):
    """
    Solve a given Lazors board.

    This function will check the size of the given board, choose the best
    solving algorithm and use it to solve given board.

    **Parameters**

        board: *pylazors.Board object*

    **Returns**

        solution_board: *pylazors.Board object*
            board for the solved maze
    """

    if board.width * board.height < 15:
        solution = _solve_board(board, **kwargs)
        if solution is None:
            # fallback to _solve_large_board() when _solve_board() skips
            # solving due to too many combinations.
            return _solve_large_board(board)
        else:
            return solution
    else:
        return _solve_large_board(board)
