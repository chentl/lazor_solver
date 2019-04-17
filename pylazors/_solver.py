"""
This file contains board solver optimized for large board.

The _solve_large_board() function in this file should have same input and output formats
as the _solve_board() function in solver.py. Also both functions should yield same
results when given the same input. The only differences between them is that the one
in this file will be more efficient when solving large boards.

docs/optimization.md contains some notes about this file.
"""

from pylazors.block import Block
from itertools import combinations
import pickle


def _target_neighbor_block_positions(x, y):
    """ Return locations of two neighbor blocks of target point at (x, y) """

    bx, by = x // 2, y // 2
    return ((bx, by), (bx - 1, by)) if y % 2 else ((bx, by), (bx, by - 1))


def _laser_next_block_position(x, y, vx, vy):
    """ Return location of the next block on path of laser (x, y, vx, vy) """

    # This is a one-line equivalent of some codes in trace_lasers()
    bx, by = x // 2, y // 2
    return (bx - (0 if vx > 0 else 1), by) if y % 2 else (bx, by - (0 if vy > 0 else 1))


def _trace_lasers(blocks, laser_sources):
    """ Trace lasers on board and return all laser paths.
        **Parameters**

        blocks: *list, list*
            A list of lists holding all blocks on board. Format should be
            same as the the return of pylazors.board.Board.get_blocks()
            [[<Block>, <Block>, ...], ...]
        laser_sources: *list, tuple*
            A list of tuples holding all laser sources. Format should be
            same as the the return of pylazors.board.Board.get_lasers().
            [(x, y, vx, vy), ...]

    **Returns**

        laser_segments: *list, tuple*
            A list of tuples holding all segments on laser path.
            [(x0, y0, x1, y1), ...]
    """

    lasers, laser_history = list(laser_sources), set(laser_sources)
    laser_segments = []
    width, height = len(blocks[0]), len(blocks)

    while len(lasers):
        x, y, vx, vy = lasers.pop()
        vertical_wall = True if y % 2 else False
        if vertical_wall:
            bx, by = x // 2 - (0 if vx > 0 else 1), y // 2
        else:
            bx, by = x // 2, y // 2 - (0 if vy > 0 else 1)
        if bx < 0 or by < 0 or bx >= width or by >= height:
            continue
        next_block = blocks[by][bx]

        if next_block.is_transparent():
            x1, y1 = x + vx, y + vy
            laser_segments.append((x, y, x1, y1))
            new_laser = (x1, y1, vx, vy)
            if new_laser not in laser_history:
                lasers.append(new_laser)
                laser_history.add(new_laser)

        if next_block.is_reflective():
            new_laser = (x, y, -vx, vy) if vertical_wall else (x, y, vx, -vy)
            if new_laser not in laser_history:
                lasers.append(new_laser)
                laser_history.add(new_laser)

    return laser_segments


def _block_combinations(available_locations, num_opaque, num_reflect, num_refract, banned_single=None, banned_pair=None):
    """ Generate combinations for block locations

        **Parameters**

            available_locations: *list, tuple*
                A list of tuples holding all available locations in where a block
                can be placed.
                Example: [(0, 1), (2, 3), ...]

            num_opaque: *int*
                number of available opaque blocks

            num_reflect: *int*
                number of available opaque blocks

            num_refract: *int*
                number of available opaque blocks

            banned_single: *list, tuple*:
                A list of tuples holding all positions where a opaque block can not be placed.
                Example: [(0, 1), (2, 3), ...]

            banned_pair: *list, tuple, tuple*
                A list of tuples holding all positions where two non-transparent blocks can not
                be placed at the same time.
                Example: [((1, 3), (2, 3)), ((4, 4), (5, 4)), ...]

        **Yields**
            loc_opaque, loc_reflect, loc_refract, skip_opaque_count, skip_reflect_count
                Locations of three different block types, each in a separate list.
                And two skip counts for debug purpose.
    """

    locations = frozenset(available_locations)
    loc_opaque_iter = [None]
    loc_reflect_iter = [None]
    skip_opaque_count, skip_reflect_count = 0, 0

    if num_opaque:
        loc_opaque_iter = combinations(locations, num_opaque)

    # Loop in OPAQUE blocks
    for loc_opaque in loc_opaque_iter:
        if num_opaque:
            if banned_single:
                if any(map(lambda b: b in loc_opaque, banned_single)):
                    skip_opaque_count += 1
                    continue
            if banned_pair:
                if any(map(lambda b: b[0] in loc_opaque and b[1] in loc_opaque, banned_pair)):
                    skip_opaque_count += 1
                    continue
            available_for_reflect = locations - set(loc_opaque)
        else:
            available_for_reflect = locations

        if num_reflect:
            loc_reflect_iter = combinations(available_for_reflect, num_reflect)

        # Loop in REFLECT blocks
        for loc_reflect in loc_reflect_iter:
            if num_reflect:
                if banned_pair:
                    tmp_locations = loc_reflect + loc_opaque if loc_opaque else loc_reflect
                    if any(map(lambda b: b[0] in tmp_locations and b[1] in tmp_locations, banned_pair)):
                        skip_reflect_count += 1
                        continue
                available_for_refract = available_for_reflect - set(loc_reflect)
            else:
                available_for_refract = available_for_reflect
            if num_refract:
                loc_refract_iter = combinations(available_for_refract, num_refract)
                for loc_refract in loc_refract_iter:
                    yield loc_opaque, loc_reflect, loc_refract, skip_opaque_count, skip_reflect_count
            else:
                yield loc_opaque, loc_reflect, None, skip_opaque_count, skip_reflect_count


def _solve_large_board(board):
    """ Solve a Lazors Board.
        **Parameters**

        board: *pylazors.Board object*


    **Returns**

        solution_board: *pylazors.Board object*
            One possible solution board. if no solution found, will return None.
    """

    solution_board = board.copy(with_laser_segments=False)
    available_blocks = board.get_available_blocks()
    org_blocks_pickled = pickle.dumps(solution_board.get_blocks())
    org_lasers_pickled = pickle.dumps(solution_board.get_laser_sources())

    # Obtain all unfixed locations
    available_locations = set()
    for y in range(solution_board.height):
        for x in range(solution_board.width):
            if not solution_board.get_block(x, y).is_fixed():
                available_locations.add((x, y))

    num_opaque = available_blocks.count(Block.OPAQUE)
    num_reflect = available_blocks.count(Block.REFLECT)
    num_refract = available_blocks.count(Block.REFRACT)

    targets = solution_board.get_targets()
    laser_sources = solution_board.get_laser_sources()

    # Locations in where OPAQUE block can not be. Because it will block the only laser source directly.
    banned_single = set()
    if num_opaque and len(laser_sources) == 1:
        banned_single.update([_laser_next_block_position(*l) for l in laser_sources])

    # Locations in where two Non-transparent blocks (OPAQUE and REFLECT) can not be at the same time. Because:
    #   1) they will surround a target point, or
    #   2) they will surround the only laser source.
    banned_pair = set()
    if num_opaque or num_reflect:
        banned_pair.update([_target_neighbor_block_positions(*p) for p in targets])
    if (num_opaque or num_reflect) and len(laser_sources) == 1:
        banned_pair.update(([_target_neighbor_block_positions(*l[:2]) for l in laser_sources]))

    location_generator = _block_combinations(available_locations, num_opaque, num_reflect, num_refract,
                                             banned_single, banned_pair)

    i = 0
    for loc_opaque, loc_reflect, loc_refract, skip_opaque_count, skip_reflect_count in location_generator:
        i += 1
        blocks = pickle.loads(org_blocks_pickled)
        laser_sources = pickle.loads(org_lasers_pickled)

        if loc_opaque:
            for x, y in loc_opaque:
                blocks[y][x] = Block.OPAQUE
        if loc_reflect:
            for x, y in loc_reflect:
                blocks[y][x] = Block.REFLECT
        if loc_refract:
            for x, y in loc_refract:
                blocks[y][x] = Block.REFRACT

        laser_segments = _trace_lasers(blocks, laser_sources)

        all_points_on_path = []
        for s in laser_segments:
            all_points_on_path.append((s[0], s[1]))
            all_points_on_path.append((s[2], s[3]))
        if all([p in all_points_on_path for p in targets]):
            solution_board.load_laser_segments(laser_segments)
            solution_board.load_blocks(blocks)
            print('[solve_large_board] # of tested boards: %d' % i)
            print('[solve_large_board] # of skipped combinations: %d (opaque), %d (reflect)' %
                  (skip_opaque_count, skip_reflect_count))
            return solution_board
    return None
