import unittest
from pylazors.block import *


class TestBlockTypes(unittest.TestCase):

    def test_opaque_block(self):
        o = Block.OPAQUE
        self.assertFalse(o.is_transparent())
        self.assertFalse(o.is_reflective())
        self.assertFalse(o.is_fixed())

    def test_blank_block(self):
        o = Block.BLANK
        self.assertTrue(o.is_transparent())
        self.assertFalse(o.is_reflective())
        self.assertFalse(o.is_fixed())

    def test_reflect_block(self):
        o = Block.REFLECT
        self.assertFalse(o.is_transparent())
        self.assertTrue(o.is_reflective())
        self.assertFalse(o.is_fixed())

    def test_refract_block(self):
        o = Block.REFRACT
        self.assertTrue(o.is_transparent())
        self.assertTrue(o.is_reflective())
        self.assertFalse(o.is_fixed())

    def test_fixed_opaque_block(self):
        o = Block.FIXED_OPAQUE
        self.assertFalse(o.is_transparent())
        self.assertFalse(o.is_reflective())
        self.assertTrue(o.is_fixed())

    def test_fixed_blank_block(self):
        o = Block.FIXED_BLANK
        self.assertTrue(o.is_transparent())
        self.assertFalse(o.is_reflective())
        self.assertTrue(o.is_fixed())

    def test_fixed_reflect_block(self):
        o = Block.FIXED_REFLECT
        self.assertFalse(o.is_transparent())
        self.assertTrue(o.is_reflective())
        self.assertTrue(o.is_fixed())

    def test_fixed_refract_block(self):
        o = Block.FIXED_REFRACT
        self.assertTrue(o.is_transparent())
        self.assertTrue(o.is_reflective())
        self.assertTrue(o.is_fixed())

    def test_fix_block(self):
        o = fix_block(Block.REFRACT)
        self.assertTrue(o.is_fixed())

    def test_unfix_block(self):
        o = unfix_block(Block.FIXED_REFLECT)
        self.assertFalse(o.is_fixed())


if __name__ == '__main__':
    unittest.main()