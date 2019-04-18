import unittest
from pylazors.formats.bff import *
import tempfile
import os

bff_content = '''GRID START
o o o
o o o
B o o
GRID STOP

A 3

L 5 0 -1 1
L 5 6 -1 -1

P 4 1
P 0 3

'''


class TestBFFFormat(unittest.TestCase):

    def test_bff_reader(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_bff = os.path.join(tmp_dir, 'a.bff')
            with open(tmp_bff, 'w') as f:
                f.write(bff_content)

            board = read_bff(tmp_bff)

        self.assertEqual(board.width, 3)
        self.assertEqual(board.height, 3)
        self.assertEqual(board.get_block(0, 2), Block.FIXED_OPAQUE)
        self.assertEqual(board.get_laser_sources(), [(5, 0, -1, 1), (5, 6, -1, -1)])
        self.assertEqual(board.get_targets(), [(4, 1), (0, 3)])


if __name__ == '__main__':
    unittest.main()