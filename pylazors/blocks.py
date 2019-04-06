from enum import IntEnum, IntFlag


class BlockProperty(IntFlag):
    NONE = 0
    FIXED = 1 << 0
    TRANSPARENT = 1 << 1
    REFLECTIVE = 1 << 2


class Block(IntEnum):
    BLANK = BlockProperty.TRANSPARENT
    OPAQUE = BlockProperty.NONE
    REFLECT = BlockProperty.REFLECTIVE
    REFRACT = BlockProperty.TRANSPARENT | BlockProperty.REFLECTIVE
    FIXED_BLANK = BlockProperty.FIXED | BlockProperty.TRANSPARENT
    FIXED_OPAQUE = BlockProperty.FIXED
    FIXED_REFLECT = BlockProperty.FIXED | BlockProperty.REFLECTIVE
    FIXED_REFRACT = BlockProperty.FIXED | BlockProperty.TRANSPARENT | BlockProperty.REFLECTIVE

    def is_fixed(self):
        return bool(self & BlockProperty.FIXED)

    def is_reflective(self):
        return bool(self & BlockProperty.REFLECTIVE)

    def is_transparent(self):
        return bool(self & BlockProperty.TRANSPARENT)

    def __repr__(self):
        return "<%s>" % self._name_

    def __str__(self):
        return repr(self)


def fix_block(block):
    return Block(block | BlockProperty.FIXED)


def unfix_block(block):
    return Block(block & (~ BlockProperty.FIXED))
