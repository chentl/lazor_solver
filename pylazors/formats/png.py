from pylazors.block import *
from PIL import Image, ImageDraw, ImageFont
import os
import pylazors.formats as pylazors_formats


_BLOCK_SIZE = 256
_TEXTURE_DIR = os.path.join(os.path.dirname(pylazors_formats.__file__), 'textures')
_FONT_DIR = os.path.join(os.path.dirname(pylazors_formats.__file__), 'fonts')


def _load_texture(fname, size=_BLOCK_SIZE):
    img = Image.open(os.path.join(_TEXTURE_DIR, fname))
    return img.convert('RGBA').resize((size, size))


_block_textures = {
    Block.BLANK: _load_texture('blank.png'),
    Block.OPAQUE: _load_texture('opaque.png'),
    Block.FIXED_OPAQUE: _load_texture('opaque_fixed.png'),
    Block.REFLECT: _load_texture('reflect.png'),
    Block.FIXED_REFLECT: _load_texture('reflect_fixed.png'),
    Block.REFRACT: _load_texture('refract.png'),
    Block.FIXED_REFRACT: _load_texture('refract_fixed.png'),
}

_other_textures = {
    'laser': _load_texture('laser.png', size=_BLOCK_SIZE // 5 * 3),
    'target_hit': _load_texture('target_hit.png', size=_BLOCK_SIZE // 5 * 4),
}

_font_file = os.path.join(_FONT_DIR, 'SourceCodeVariable-Roman.ttf')


def write_png(board, fname, note=None):
    '''
    Write *board* as a PNG image.

        **Parameters**

        board: *pylazors.board.Board*
            The board to be exported.
        fname: *str*
            file name of the destined PNG file.
        note: *str, optional*
            If given, will be added at the bottom of the image.

    **Returns**

        None

    '''

    if not fname.endswith('.png'):
        fname += '.png'

    margin = _BLOCK_SIZE
    width, height = board.width, board.height
    img_size = margin * 2 + width * _BLOCK_SIZE, margin * 2 + height * _BLOCK_SIZE
    img = Image.new('RGB', img_size, color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(_font_file, _BLOCK_SIZE // 3)

    text_size = draw.textsize(board.name, font=font)
    test_pos = (img_size[0] - text_size[0]) / 2, (margin - text_size[1]) / 2
    draw.text(test_pos, board.name, fill=(0, 0, 0), font=font)

    if note:
        note_font = ImageFont.truetype(_font_file, _BLOCK_SIZE // 4)
        note_size = draw.textsize(note, font=note_font)
        note_pos = (img_size[0] - note_size[0]) / 2, margin + _BLOCK_SIZE * height + (margin - note_size[1]) / 2
        draw.text(note_pos, note, fill=(0, 0, 0), font=note_font)

    draw.rectangle((margin, margin, margin + width * _BLOCK_SIZE, margin + height * _BLOCK_SIZE),
                   fill=(200, 200, 200))

    for y in range(height):
        for x in range(width):
            block = board.get_block(x, y)
            if block in _block_textures and block.is_transparent():
                texture = _block_textures[block]
                img.paste(texture, (x * _BLOCK_SIZE + margin, y * _BLOCK_SIZE + margin,
                            x * _BLOCK_SIZE + margin + _BLOCK_SIZE, y * _BLOCK_SIZE + margin + _BLOCK_SIZE),
                          mask=texture)

    for x0, y0, x1, y1 in board.get_laser_segments():
        draw.line([x0 * _BLOCK_SIZE // 2 + margin, y0 * _BLOCK_SIZE // 2 + margin,
                   x1 * _BLOCK_SIZE // 2 + margin, y1 * _BLOCK_SIZE // 2 + margin],
                  fill=(255, 0, 0, 128), width=max(_BLOCK_SIZE//32, 1))

    texture = _other_textures['laser']
    texture_size = _BLOCK_SIZE // 5 * 3
    d_size = texture_size // 2, texture_size - texture_size // 2
    for x, y, _, _ in board.get_lasers():
        img.paste(texture, [int(x / 2 * _BLOCK_SIZE) - d_size[0] + margin,
                            int(y / 2 * _BLOCK_SIZE) - d_size[0] + margin,
                            int(x / 2 * _BLOCK_SIZE) + d_size[1] + margin,
                            int(y / 2 * _BLOCK_SIZE) + d_size[1] + margin], mask=texture)

    texture = _other_textures['target_hit']
    texture_size = _BLOCK_SIZE // 5 * 4
    d_size = texture_size // 2, texture_size - texture_size // 2
    for x, y, in board.get_points():
        img.paste(texture, [int(x / 2 * _BLOCK_SIZE) - d_size[0] + margin,
                            int(y / 2 * _BLOCK_SIZE) - d_size[0] + margin,
                            int(x / 2 * _BLOCK_SIZE) + d_size[1] + margin,
                            int(y / 2 * _BLOCK_SIZE) + d_size[1] + margin], mask=texture)

    for y in range(height):
        for x in range(width):
            block = board.get_block(x, y)
            if block in _block_textures and not block.is_transparent():
                texture = _block_textures[block]
                img.paste(texture, (x * _BLOCK_SIZE + margin, y * _BLOCK_SIZE + margin,
                            x * _BLOCK_SIZE + margin + _BLOCK_SIZE, y * _BLOCK_SIZE + margin + _BLOCK_SIZE),
                          mask=texture)

    img = img.resize((img_size[0] // 2, img_size[1] // 2), Image.LANCZOS)
    img.save(fname)
