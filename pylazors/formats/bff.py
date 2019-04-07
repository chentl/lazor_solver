from pylazors.board import Board
from pylazors.blocks import *
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
    ''' Read BFF file *fname*, return a pylazors.board.Board object. '''

    with open(fname, 'r') as f:
        bff_content = f.read()

    board_name = os.path.splitext(os.path.basename(fname))[0]

    grid_flag = False
    grid = []
    line_no = 0
    for line in bff_content.split('\n'):
        line_no += 1
        line = line.split('#', 1)[0]

        if len(line.strip()) == 0:
            continue

        if grid_flag:
            if line.rstrip() == 'GRID STOP':
                grid_flag = False
                grid_width = len(grid[0])
                grid_height = len(grid)
                board = Board(board_name, grid_width, grid_height)

                for y in range(grid_height):
                    if len(grid[y]) != grid_width:
                        raise IllegalSyntaxError
                    for x in range(grid_width):
                        try:
                            board.mod_block(x, y, bff_block_map[grid[y][x]])
                        except KeyError:
                            raise UnknownSymbolError

            else:
                grid.append(line.strip().split())
        elif line.rstrip() == 'GRID START':
            grid_flag = True
        else:
            items = line.strip().split()
            name, value = items[0], items[1:]
            if name == 'P':
                assert len(value) == 2
                board.add_point(int(value[0]), int(value[1]))
            elif name == 'L':
                assert len(value) == 4
                x, y, vx, vy = list(map(int, value))
                board.add_laser(x, y, vx, vy)
            elif name in bff_block_map:
                assert len(value) == 1
                board.add_available_blocks(unfix_block(bff_block_map[name]), int(value[0]))
            else:
                raise UnknownSymbolError(name)

    return board


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
