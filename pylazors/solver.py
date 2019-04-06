from pylazors.board import Board
from pylazors.blocks import Block


def trace_lasers(blocks, lasers, with_outbound_lasers=False):
    laser_history = set(lasers)
    laser_segments = []
    outbound_lasers = []
    width, height = len(blocks[0]), len(blocks)

    while len(lasers):
        x, y, vx, vy = lasers.pop()
        vertical_wall = True if y % 2 else False
        if vertical_wall:
            bx = x // 2 - (0 if vx > 0 else 1)
            by = y // 2
        else:
            bx = x // 2
            by = y // 2 - (0 if vy > 0 else 1)
        if bx < 0 or by < 0 or bx >= width or by >= height:
            if with_outbound_lasers:
                outbound_lasers.append((x, y, vx, vy))
            continue
        block_to_check = blocks[by][bx]

        if block_to_check.is_transparent():
            x1, y1 = x + vx, y + vy
            laser_segments.append((x, y, x1, y1))
            new_laser = (x1, y1, vx, vy)
            if new_laser not in laser_history:
                lasers.append(new_laser)
                laser_history.add(new_laser)

        if block_to_check.is_reflective():
            new_laser = (x, y, -vx, vy) if vertical_wall else (x, y, vx, -vy)
            if new_laser not in laser_history:
                lasers.append(new_laser)
                laser_history.add(new_laser)

    if with_outbound_lasers:
        return laser_segments, outbound_lasers
    else:
        return laser_segments
