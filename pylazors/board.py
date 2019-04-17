"""
This file contains classes used for describing a board.

*Board* class is used to represent boards in this module.
"""

from pylazors.utils import deepcopy
from pylazors.block import Block
from math import factorial


class Board:
    """
    The class for representing a Lazors board.

    There are two different coordinates systems used in this class, one for blocks, and another one
    for laser and target points. The coordinate system for blocks start from top-left as (0, 0),
    and its step size is by one block. The coordinate system for laser and target points also
    start from top-left as (0, 0), but its step size is by half block.
    """

    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height
        self._blocks = [[None for _ in range(width)] for _ in range(height)]
        self._laser_sources = []
        self._targets = []
        self._available_blocks = []
        self._laser_segments = []

    def mod_block(self, x, y, btype):
        """ Change the block type at position (x, y) """

        assert isinstance(x, int) and 0 <= x < self.width
        assert isinstance(y, int) and 0 <= y < self.height
        assert isinstance(btype, Block)
        self._blocks[y][x] = btype

    def load_blocks(self, blocks):
        """
        Load a list of lists as all blocks.

        This should be only called internally by pylazors module since it will not perform any
        checks for performance reasons.
        """

        self._blocks = deepcopy(blocks)

    def get_movable_blocks_num(self):
        """ Return the number of unfixed locations on the board. """

        return len([b for bs in self._blocks for b in bs if not b.is_fixed()])

    def get_block(self, x, y):
        """ Return the block type at position (x, y) """

        assert isinstance(x, int) and 0 <= x < self.width
        assert isinstance(y, int) and 0 <= y < self.height
        return self._blocks[y][x]

    def get_blocks(self):
        """ Return a list of lists of all blocks. """

        return deepcopy(self._blocks)

    def add_target(self, x, y):
        """ Add a target point at position (x, y) """

        assert isinstance(x, int) and 0 <= x <= (2 * self.width)
        assert isinstance(y, int) and 0 <= y <= (2 * self.height)
        self._targets.append((x, y))

    def get_targets(self):
        """ Return all target points. """

        return deepcopy(self._targets)

    def add_laser_source(self, x, y, vx, vy):
        """ Add a laser source at (x, y) with direction (vx, vy) """

        assert isinstance(x, int) and 0 <= x <= (2 * self.width)
        assert isinstance(y, int) and 0 <= y <= (2 * self.height)
        assert isinstance(vx, int)
        assert isinstance(vy, int)
        assert abs(vx) == abs(vy)
        vx, vy = abs(vx) // vx, abs(vy) // vy
        self._laser_sources.append((x, y, vx, vy))

    def add_laser_segment(self, x0, y0, x1, y1):
        """ Add a laser path segment from (x0, y0) to (x1, y1) """

        assert isinstance(x0, int) and 0 <= x0 <= (2 * self.width)
        assert isinstance(y0, int) and 0 <= y0 <= (2 * self.height)
        assert isinstance(x1, int) and 0 <= x1 <= (2 * self.width)
        assert isinstance(y1, int) and 0 <= y1 <= (2 * self.height)
        assert abs(x0 - x1) == 1 and abs(y0 - y1) == 1, 'The laser segment must have length of sqrt(2)'
        self._laser_segments.append((x0, y0, x1, y1))

    def load_laser_segments(self, laser_segments):
        """
        Load a list of tuples as all laser path segments.

        This should be only called internally by pylazors module since it will not perform any
        checks for performance reasons.
        """

        self._laser_segments = deepcopy(laser_segments)

    def clear_laser_segments(self):
        """ Remove all laser path segments """

        self._laser_segments = []

    def get_laser_segments(self):
        """ Return all laser path segments """

        return deepcopy(self._laser_segments)

    def get_laser_sources(self):
        """ Return all laser path segments """

        return deepcopy(self._laser_sources)

    def add_available_blocks(self, block, count=1):
        """ Add *count* *block*(s) as movable block(s) """

        assert block in [Block.REFRACT, Block.REFLECT, Block.OPAQUE]
        self._available_blocks += [block] * count

    def get_available_blocks(self):
        """ Return a list of all movable blocks """

        return deepcopy(self._available_blocks)

    def clean_board(self):
        """ Set all non-fixed block to <Block.BLANK>. """

        for x in range(self.width):
            for y in range(self.height):
                if not self.get_block(x, y).is_fixed():
                    self.mod_block(x, y, Block.BLANK)
                    
    def get_estimate_complexity(self):
        """ Return estimate complexity represent by an integer """
        available_blocks = self.get_available_blocks()
        num_pos = self.get_movable_blocks_num()
        num_blocks = len(available_blocks)
        num_opaque = available_blocks.count(Block.OPAQUE)
        num_reflect = available_blocks.count(Block.REFLECT)
        num_refract = available_blocks.count(Block.REFRACT)
        
        # from solver.py
        return int(factorial(num_pos) / (factorial(num_pos - num_blocks) * 
               factorial(num_opaque) * factorial(num_reflect) * factorial(num_refract)))

    def copy(self, with_blocks=True, with_laser_sources=True, with_targets=True,
             with_available_blocks=True, with_laser_segments=True):
        """ Return a copy of this board """

        new_board = Board(self.name, self.width, self.height)
        if with_blocks:
            new_board._blocks = deepcopy(self._blocks)
        if with_laser_sources:
            new_board._laser_sources = deepcopy(self._laser_sources)
        if with_targets:
            new_board._targets = deepcopy(self._targets)
        if with_available_blocks:
            new_board._available_blocks = deepcopy(self._available_blocks)
        if with_laser_segments:
            new_board._laser_segments = deepcopy(self._laser_segments)
        return new_board

    def __str__(self):
        return '<Board: %s (%dx%d)>' % (self.name, self.width, self.height)
