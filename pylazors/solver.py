
from itertools import combinations, product
from operator import itemgetter
from math import factorial
import numpy as np
import random
import time
import os
from pylazors.formats.png import write_png
from pylazors.formats.bff import read_bff, bff_block_map
from pylazors.board import Board
from pylazors.block import Block, unfix_block

'''
Lazor Project

**Description**


**Functions**

        lazor_load_bff:
            load bff file to be read and manipulated by other functions

        lazor_solve:
            function to solve a loaded board by iterating through possible combinations

        get_possible_combs_perm:
            obtain all possible combinations for moveable blocks in available positions

        get_available_positions:
            obtain all available positions for block placement

        get_data_grid:
            convert letter_grid (loaded by lazor_load_bff) to data_grid

        lazor_on:
            function to switch lazers on and trace thier positions

        pos_chk:
            positions checker to confirm point is in grid

**bff file info**
        Grid: contains blocks with values as the following, and it must start
        and end with two lines of flags GRID START and GRID STOP
          x = no block allowed [0]
          o = blocks allowed [0]
          A = fixed reflect block [2]
          B = fixed opaque block [4]
          C = fixed refract block [6]
            example:
                GRID START
                o   o   o   o   o
                o   o   o   o   o
                o   o   o   o   x
                o   o   o   o   o
                o   o   o   o   o
                GRID STOP
        Blocks:
          A = reflect block [2]
          B = opaque block [4]
          C = refract block [6]

        Lazers: x, y, vx, vy [8]
          L 2 7 1 -1

        Target Points: x, y [9]
          P 0 1

**Examples of data representation in run**

        letter_grid = [['o' 'o' 'A' 'o' 'o']
                       ['o' 'o' 'o' 'A' 'o']
                       ['A' 'o' 'A' 'o' 'x']
                       ['o' 'o' 'o' 'A' 'o']
                       ['o' 'o' 'A' 'o' 'o']]

        blocks = ['A', 'A', 'A', 'A', 'A', 'A']

        lazers = [['2', '1', '1', '1'], ['9', '4', '-1', '1']]

        points = [['6', '3'], ['6', '5'], ['6', '7'], ['2', '9'], ['9', '6']]

        available_positions = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (0, 1),
                               (1, 1), (2, 1), (3, 1), (4, 1), (0, 2), (1, 2),
                               (2, 2), (3, 2), (0, 3), (1, 3), (2, 3), (3, 3),
                               (4, 3), (0, 4), (1, 4), (2, 4), (3, 4), (4, 4)]

        data_grid = [[ 0.  0.  0.  0.  2.  2.  2.  0.  0.  0.  0.]
                     [ 0.  0.  8.  0.  2.  2.  2.  0.  0.  0.  0.]
                     [ 0.  0.  0.  8.  2.  2.  2.  2.  2.  0.  0.]
                     [ 0.  0.  0.  0.  8.  0. -1.  2.  2.  0.  0.]
                     [ 2.  2.  2.  8.  2.  2.  2.  2.  2.  8.  0.]
                     [ 2.  2.  2.  0.  2.  2. -1.  0.  8.  0.  0.]
                     [ 2.  2.  2.  8.  2.  2.  2.  2.  2. -1.  0.]
                     [ 0.  0.  0.  0.  8.  0. -1.  2.  2.  0.  8.]
                     [ 0.  0.  0.  8.  2.  2.  2.  2.  2.  0.  0.]
                     [ 0.  0. -1.  0.  2.  2.  2.  0.  0.  0.  0.]
                     [ 0.  8.  0.  0.  2.  2.  2.  0.  0.  0.  0.]]

        possible_combs = [[('A', (0, 0)), ('A', (1, 0)), ('A', (2, 0)), ('A', (3, 0)), ('A', (4, 0)), ('A', (0, 1))],
                          [('A', (0, 0)), ('A', (1, 0)), ('A', (2, 0)), ('A', (3, 0)), ('A', (4, 0)), ('A', (1, 1))],
                          [('A', (0, 0)), ('A', (1, 0)), ('A', (2, 0)), ('A', (3, 0)), ('A', (4, 0)), ('A', (2, 1))],
                          ....
                          [('A', (4, 3)), ('A', (0, 4)), ('A', (1, 4)), ('A', (2, 4)), ('A', (3, 4)), ('A', (4, 4))]]

'''


def lazor_load_bff(inp):
    '''
    Load lazor data from a bff file

    **Parameters**

        inp: *string*
            path to bff file to be read and parsed

    **Returns**

        valid: *np.array*, *list*, *list*, *list*, *list*
            a numpy array of the grid in letters, and lists of movealbe blocks,
            lazer positions and directions, and target points positions, and
            the number of each block [A, B, C]
    '''
    letter_grid, blocks, lazers, points, A, B, C = [], [], [], [], 0, 0, 0

    with open(inp) as lazor_file:
        grid_switch = False
        for line in lazor_file:
            if line.strip() == "GRID START":
                grid_switch = True
            elif line.strip() == "GRID STOP":
                grid_switch = False
            elif grid_switch:
                letter_grid.append(line.strip().split())
            elif (line.strip()).split(" ")[0] == "A":
                A = int((line.strip()).split(" ")[1])
                for a in range(A):
                    blocks.append('A')
            elif (line.strip()).split(" ")[0] == "B":
                B = int((line.strip()).split(" ")[1])
                for b in range(B):
                    blocks.append('B')
            elif (line.strip()).split(" ")[0] == "C":
                C = int((line.strip()).split(" ")[1])
                for c in range(C):
                    blocks.append('C')
            elif (line.strip()).split(" ")[0] == "L":
                lazers.append((line.strip()).split(" ")[1:])
            elif (line.strip()).split(" ")[0] == "P":
                points.append((line.strip()).split(" ")[1:])
    letter_grid = np.array(letter_grid)

    return letter_grid, blocks, lazers, points, [A, B, C]


def lazor_solve(data, solve_limit=1E5):
    '''
    lazor (game) solver

    **Parameters**

        data: *list* {*np.array*, *list*, *list*, *list*}
            numpy array of letter_grid, lists of movealbe blocks letters,
            lazer positions and directions, and target points positions

        solve_limit: *optional, integer*
            the maximum number of combinations allowed. if exceeded, the function
            returns None. if 0 -> no limit.

    **Returns**

        valid: *np.array*
            data array for the solved maze
    '''

    # load data and count number of available positions
    letter_grid, blocks, lazers, points, block_counts = data
    available_positions = get_available_positions(letter_grid)

    # calculate the number of moveable blocks and available positions [debug]
    n_blocks, n_pos = len(blocks), len(available_positions)
    # calculate the number of unique combinations or possible combinations
    unique_combinations = factorial(n_pos) / (factorial(n_pos - n_blocks) * factorial(block_counts[0]) * factorial(block_counts[1]) * factorial(block_counts[2]))

    if (unique_combinations > solve_limit and solve_limit != 0):
        print("skipped: too many combinations! (%i)" % unique_combinations)
        return None

    unique_blocks = 0

    for bc in block_counts:
        if bc > 0:
            unique_blocks += 1

    # if the number of block types is 1, use combinations, otherwise use the modified functions
    if unique_blocks == 1:
        t0 = time.time()
        possible_combs = [zip(blocks, x) for x in combinations(available_positions, len(blocks))]
        print("%i combinations generated in %.3f s" % (len(possible_combs), time.time() - t0))
    elif unique_blocks > 1:
        t0 = time.time()
        possible_combs = get_possible_combs_perm(blocks, available_positions)
        print("%i permutations generated in %.3f s" % (len(possible_combs), time.time() - t0))

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
            print("Solution found in %i iterations" % (iter_num))
            return i_grid
        iter_num += 1

    print("No solution found!")


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
    '''
    From a letter grid, this function extracts avilable positions for a
    moveable block to be placed at.

    **Parameters**

        letter_grid: *np.array*
            letter grid generated by lazor_load function

    **Returns**

        available_positions: *list, tuples, (x, y)*
            a list of all avaiable positions in (x, y) coordinates
    '''
    available_positions = []
    for j in range(len(letter_grid)):
        for i in range(len(letter_grid[0])):
            if letter_grid[j][i] == 'o':
                available_positions.append((i, j))
    return available_positions


def get_data_grid(letter_grid, points):
    '''
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

    '''
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
    '''
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
    '''
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
    '''
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
    '''
    # x_dim, y_dim = 2 * len(grid[0]) + 1, 2 * len(grid) + 1
    x_dim, y_dim = len(data_grid[0, :]), len(data_grid[:, 0])
    # print(x_dim, y_dim)
    return x >= 0 and x < x_dim and y >= 0 and y < y_dim


def solution_to_png(solution, bff_fname, png_fname):
    '''
    Export solution as a PNG Image.

    This code is in a early verion. It just read the original BFF
    file into a <Board> object, replace blocks by *solution*. Run
    trace_lasers to get laser paths, and call write_png.

    #TODO: Instead of tracing laser again, just extract laser info
    from lazor_solve()
    '''

    board = read_bff(bff_fname)
    width, height = board.width, board.height

    # Because in solution 'A', 'B', and 'C' may represent fixed or
    # unfixed blocks, use original board from BFF file to find out
    # which block is unfixed.
    original_blocks = board.get_blocks()
    solution_blocks = [[bff_block_map[b] for b in row] for row in solution]
    for x in range(width):
        for y in range(height):
            if original_blocks[y][x] != solution_blocks[y][x]:
                board.mod_block(x, y, unfix_block(solution_blocks[y][x]))

    # Run laser-tracing on solution board
    laser_segs = trace_lasers(board.get_blocks(), board.get_lasers())
    board.load_laser_segments(laser_segs)

    # Write to PNG
    write_png(board, png_fname)


# Test and optimization utilities unit
if __name__ == "__main__":
    if not os.path.exists('solutions'):
        os.makedirs('solutions')

    files = os.listdir(os.path.join('boards', 'all'))
    for file in files:
        if not file.endswith('.bff'):
            continue

        print("--------------- Solving: %s -----------------" % file)
        fptr = os.path.join('boards', 'all', file)
        data = lazor_load_bff(fptr)
        t0 = time.time()
        solution = lazor_solve(data, solve_limit=1E6)
        print(solution)
        print(' Solver Performance: %.5f seconds' % (time.time() - t0))

        png_fname = os.path.join('solutions', file.split('.')[0])
        if solution is not None:
            solution_to_png(solution, fptr, png_fname)
