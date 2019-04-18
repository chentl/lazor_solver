from pylazors.board import Board
from pylazors.block import *
import os


bff_block_map = {'o': Block.BLANK,
                 'x': Block.FIXED_BLANK,
                 'A': Block.FIXED_REFLECT,
                 'B': Block.FIXED_OPAQUE,
                 'C': Block.FIXED_REFRACT}
block_bff_map = {v: k for k, v in bff_block_map.items()}


class BFFReaderError(Exception):
    def __init__(self, file_name, line_no=None, message=''):
        msg = 'Error in %s' % file_name
        if line_no:
            msg += ' at line %d' % line_no
        if message:
            msg += ': %s' % message
        super().__init__(msg)


def read_bff(fname):
    """
    Load Lazors board data from a BFF file

    **Parameters**

        fname: *string*
            path to bff file to be read and parsed

            See docs/sample.bff for format detail of .BFF files.

    **Returns**

        board: *pylazors.Board object*

    """

    board_grid, available_blocks, laser_sources, target_points = [], [], [], []
    board_name = os.path.splitext(os.path.basename(fname))[0]

    try:
        with open(fname) as f:
            bff_file = f.read()
    except FileNotFoundError:
        raise BFFReaderError(fname, message='File not found.')

    grid_switch = False
    grid_width = None
    for line_no, line in enumerate(bff_file.splitlines(), start=1):
        line = line.split('#', 1)[0].strip()
        if len(line) == 0:
            continue

        if line.strip() == 'GRID START':
            if grid_switch:
                raise BFFReaderError(fname, line_no, 'Too many GRID START')
            if board_grid:
                raise BFFReaderError(fname, line_no, 'Only one grid can be defined in a BFF file')
            grid_switch = True
        elif line.strip() == 'GRID STOP':
            if not grid_switch or not board_grid:
                raise BFFReaderError(fname, line_no, 'GRID STOP before a grid has been defined')
            grid_switch = False

        elif grid_switch:
            try:
                row = [bff_block_map[x] for x in line.split()]
            except KeyError:
                raise BFFReaderError(fname, line_no, 'Unknown block symbol')
            if grid_width:
                if grid_width != len(row):
                    raise BFFReaderError(fname, line_no, 'Grid width mismatches.')
            else:
                grid_width = len(row)
            board_grid.append(row)
        elif line.split(' ')[0] in ['A', 'B', 'C']:
            try:
                block_type = unfix_block(bff_block_map[line.split(' ')[0]])
                block_count = int(line.split(' ')[1])
            except (KeyError, ValueError, IndexError):
                raise BFFReaderError(fname, line_no, 'Error syntax for available block')
            available_blocks.append(tuple([block_type, block_count]))
        elif line.split(' ')[0] == 'L':
            try:
                x, y, vx, vy = list(map(int, line.split(' ')[1:]))
            except (KeyError, ValueError, IndexError) as e:
                raise BFFReaderError(fname, line_no, str(e))
            laser_sources.append(tuple([x, y, vx, vy]))
        elif line.split(' ')[0] == 'P':
            try:
                x, y = list(map(int, line.split(' ')[1:]))
            except (KeyError, ValueError, IndexError) as e:
                raise BFFReaderError(fname, line_no, str(e))
            target_points.append(tuple([x, y]))
        else:
            raise BFFReaderError(fname, line_no, 'Unknown syntax: ' + line)

    if not board_grid:
        raise BFFReaderError(fname, message='Missing grid information')
    if not available_blocks:
        raise BFFReaderError(fname, message='Missing available block information')
    if not laser_sources:
        raise BFFReaderError(fname, message='Missing laser source information')
    if not target_points:
        raise BFFReaderError(fname, message='Missing target point information')

    width, height = len(board_grid[0]), len(board_grid)
    board = Board(board_name, width, height)
    for x in range(width):
        for y in range(height):
            board.mod_block(x, y, board_grid[y][x])
    for block_type, block_count in available_blocks:
        board.add_available_blocks(block_type, block_count)
    if len(board.get_available_blocks()) > board.get_movable_blocks_num():
        raise BFFReaderError(fname, message='Too many available blocks')
    for x, y, vx, vy in laser_sources:
        try:
            board.add_laser_source(x, y, vx, vy)
        except AssertionError as e:
            raise BFFReaderError(fname, message='Error laser formats: ' + str(e))
    for x, y in target_points:
        try:
            board.add_target(x, y)
        except AssertionError as e:
            raise BFFReaderError(fname, message='Error point formats: ' + str(e))
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
