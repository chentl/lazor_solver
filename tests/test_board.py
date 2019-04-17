import unittest
from pylazors.board import *


class TestBoard(unittest.TestCase):

    def test_board_blocks(self):
        board = Board('test_1', 2, 2)
        board.load_blocks([[Block.BLANK, Block.BLANK], [Block.FIXED_REFLECT, Block.BLANK]])
        self.assertEqual(board.get_block(0, 0), Block.BLANK)
        self.assertEqual(board.get_block(0, 1), Block.FIXED_REFLECT)

    def test_board_lasers(self):
        board = Board('test_1', 2, 2)
        board.load_blocks([[Block.BLANK, Block.BLANK], [Block.FIXED_REFLECT, Block.BLANK]])

        board.add_laser_source(0, 1, 1, 1)
        self.assertEqual(board.get_laser_sources(), [(0, 1, 1, 1)])

        with self.assertRaises(AssertionError):
            board.add_laser_source(0, 1, -2, 1)

        with self.assertRaises(AssertionError):
            board.add_laser_source(0, 10, -1, 1)

    def test_board_targets(self):
        board = Board('test_1', 2, 2)
        board.load_blocks([[Block.BLANK, Block.BLANK], [Block.FIXED_REFLECT, Block.BLANK]])

        board.add_target(0, 0)
        self.assertEqual(board.get_targets(), [(0, 0)])

        with self.assertRaises(AssertionError):
            board.add_target(0, 10)

    def test_board_available_blocks(self):
        board = Board('test_1', 2, 2)
        board.load_blocks([[Block.BLANK, Block.BLANK], [Block.BLANK, Block.BLANK]])

        board.add_available_blocks(Block.REFRACT)
        board.add_available_blocks(Block.REFLECT, 2)
        self.assertEqual(board.get_available_blocks(), [Block.REFRACT, Block.REFLECT, Block.REFLECT])

        with self.assertRaises(AssertionError):
            board.add_available_blocks(Block.BLANK, 2)


if __name__ == '__main__':
    unittest.main()