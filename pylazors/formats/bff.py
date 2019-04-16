from pylazors.board import Board
from pylazors.block import *
import os

bff_block_map = {'o': Block.BLANK,
                 'x': Block.FIXED_BLANK,
                 'A': Block.FIXED_REFLECT,
                 'B': Block.FIXED_OPAQUE,
                 'C': Block.FIXED_REFRACT}
block_bff_map = {v: k for k, v in bff_block_map.items()}


def read_bff(fname):
    """
    Load Lazors board data from a BFF file

    **Parameters**

        fname: *string*
            path to bff file to be read and parsed

    **Returns**

        board: *pylazors.Board object*

    """

    board_grid, available_blocks, laser_sources, target_points = [], [], [], []
    board_name = os.path.splitext(os.path.basename(fname))[0]

    with open(fname) as bff_file:
        grid_switch = False
        for line in bff_file:
            line = line.split('#', 1)[0].strip()
            if len(line) == 0:
                continue

            if line.strip() == 'GRID START':
                grid_switch = True
            elif line.strip() == 'GRID STOP':
                grid_switch = False
            elif grid_switch:
                board_grid.append([bff_block_map[x] for x in line.split()])
            elif line.split(' ')[0] in ['A', 'B', 'C']:
                block_type = unfix_block(bff_block_map[line.split(' ')[0]])
                block_count = int(line.split(' ')[1])
                available_blocks.append(tuple([block_type, block_count]))
            elif line.split(' ')[0] == 'L':
                x, y, vx, vy = list(map(int, line.split(' ')[1:]))
                laser_sources.append(tuple([x, y, vx, vy]))
            elif line.split(' ')[0] == 'P':
                x, y = list(map(int, line.split(' ')[1:]))
                target_points.append(tuple([x, y]))

    width, height = len(board_grid[0]), len(board_grid)
    board = Board(board_name, width, height)
    for x in range(width):
        for y in range(height):
            board.mod_block(x, y, board_grid[y][x])
    for block_type, block_count in available_blocks:
        board.add_available_blocks(block_type, block_count)
    for x, y, vx, vy in laser_sources:
        board.add_laser_source(x, y, vx, vy)
    for x, y in target_points:
        board.add_target(x, y)
    return board


def write_bff(board, fname):
    """ Save *board* (a pylazors.Board object) as a BFF file """

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
            f.write(' '.join([block_bff_map[b] for b in blocks[y]]) + '\n')
        f.write('GRID STOP\n\n')

        for block in set(available_blocks):
            f.write('%s %d\n' % (block_bff_map[fix_block(block)], available_blocks.count(block)))
        f.write('\n')
        for x, y, vx, vy in lasers:
            f.write('L %d %d %d %d\n' % (x, y, vx, vy))
        f.write('\n')
        for x, y in points:
            f.write('P %d %d\n' % (x, y))
