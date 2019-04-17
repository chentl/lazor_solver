import unittest
from pylazors.board import *
from pylazors.block import *
from pylazors.formats.png import write_png
from PIL import Image
import tempfile
import os


def sample_solution():
    board = Board('test_1', 3, 3)
    board.load_blocks([[Block.REFLECT, Block.REFLECT, Block.BLANK],
                      [Block.BLANK, Block.BLANK, Block.REFLECT],
                      [Block.FIXED_OPAQUE, Block.BLANK, Block.BLANK]])
    board.add_available_blocks(Block.REFLECT, 3)
    board.add_laser_source(5, 0, -1, 1)
    board.add_laser_source(5, 6, -1, -1)
    board.add_target(4, 1)
    board.add_target(0, 3)
    board.load_laser_segments([(5, 6, 4, 5), (4, 5, 3, 4), (3, 4, 2, 3), (2, 3, 1, 2),
                               (1, 2, 0, 3), (5, 0, 4, 1), (4, 1, 5, 2), (5, 2, 6, 1)])

    return board


class TestPNGFormat(unittest.TestCase):

    def test_png_writer(self):
        solution = sample_solution()

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_png = os.path.join(tmp_dir, 'a.png')

            write_png(solution, tmp_png)

            try:
                img = Image.open(tmp_png)
            except IOError:
                self.fail('Output PNG file not exists.')

            self.assertEqual('PNG', img.format)


if __name__ == '__main__':
    unittest.main()