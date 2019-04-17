import unittest
from pylazors.board import *
from pylazors.solver import _solve_large_board, _solve_board, solve_board
from pylazors.block import *


def sample_board():
    board = Board('test_1', 3, 3)
    board.load_blocks([[Block.BLANK, Block.BLANK, Block.BLANK],
                       [Block.BLANK, Block.BLANK, Block.BLANK],
                       [Block.FIXED_OPAQUE, Block.BLANK, Block.BLANK]])
    board.add_available_blocks(Block.REFLECT, 3)
    board.add_laser_source(5, 0, -1, 1)
    board.add_laser_source(5, 6, -1, -1)
    board.add_target(4, 1)
    board.add_target(0, 3)
    return board


reference_blocks = [[Block.REFLECT, Block.REFLECT, Block.BLANK],
                    [Block.BLANK, Block.BLANK, Block.REFLECT],
                    [Block.FIXED_OPAQUE, Block.BLANK, Block.BLANK]]


class TestSolver(unittest.TestCase):

    def test_solve_board_warpper(self):
        board = sample_board()
        solution = solve_board(board, print_log=False)

        self.assertEqual(reference_blocks, solution.get_blocks())

    def test_solve_board(self):
        board = sample_board()
        solution = _solve_board(board, print_log=False)

        self.assertEqual(reference_blocks, solution.get_blocks())

    def test_solve_large_board(self):
        board = sample_board()
        solution = _solve_large_board(board, print_log=False)

        self.assertEqual(reference_blocks, solution.get_blocks())


if __name__ == '__main__':
    unittest.main()