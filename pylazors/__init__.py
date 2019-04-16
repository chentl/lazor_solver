import sys

# In block.py: Use of enum.IntEnum, enum.IntFlag: Require Python 3.6 and higher

if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    raise Exception('Must be using at least Python 3.6')
else:
    from .board import Board
    from .block import Block
    from .solver import solve_board
    from .formats.png import write_png
    from .formats.bff import write_bff, read_bff

