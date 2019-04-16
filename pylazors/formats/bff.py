from pylazors.board import Board
from pylazors.block import *
import os

bff_block_map = {'o': Block.BLANK,
                 'x': Block.FIXED_BLANK,
                 'A': Block.FIXED_REFLECT,
                 'B': Block.FIXED_OPAQUE,
                 'C': Block.FIXED_REFRACT}
block_dff_map = {v: k for k, v in bff_block_map.items()}


class UnknownSymbolError(Exception):
    pass


class IllegalSyntaxError(Exception):
    pass


def read_bff(fname):
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


def write_bff(board, fname):
    ''' Save *board* (a pylazors.board.Board object) as a BFF file '''

    board = board.copy(with_laser_segs=False)
    board.clean_board()
    blocks = board.get_blocks()
    available_blocks = board.get_available_blocks()
    lasers = board.get_lasers()
    points = board.get_points()

    if not fname.endswith('.bff'):
        fname += '.bff'

    with open(fname, 'w') as f:
        f.write('GRID START\n')
        for y in range(board.height):
            f.write(' '.join([block_dff_map[b] for b in blocks[y]]) + '\n')
        f.write('GRID STOP\n\n')

        for block in set(available_blocks):
            f.write('%s %d\n' % (block_dff_map[fix_block(block)], available_blocks.count(block)))
        f.write('\n')
        for x, y, vx, vy in lasers:
            f.write('L %d %d %d %d\n' % (x, y, vx, vy))
        f.write('\n')
        for x, y in points:
            f.write('P %d %d\n' % (x, y))
