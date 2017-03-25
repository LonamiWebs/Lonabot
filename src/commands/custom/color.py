from commands.command_base import CommandBase
from tempfile import TemporaryFile
import re
import zlib
import struct
from io import BytesIO


def _write_IHDR(handle, width, height, bit_depth=8, color_type=''):
    """Writes the IHDR chunk, defined as follows:
        [ 0] width
        [ 4] height
        [ 8] bit depth (bits per channel, not per pixel)
        [ 9] color type ('p' for palette, 'c' for color, 'a' for alpha)
        [ A] compression method (zlib)
        [ B] filter method (adaptative)
        [ C] interlace method (none)
        [ D] (13 bytes in total)
    """
    ct = 0
    if 'p' in color_type:
        ct |= 1
    if 'c' in color_type:
        ct |= 2
    if 'a' in color_type:
        ct |= 4

    if ct not in [0, 2, 3, 4, 6]:
        raise ValueError('Invalid color type given: ' + str(ct))

    with BytesIO() as block:
        block.write(struct.pack('>I', width))
        block.write(struct.pack('>I', height))
        block.write(struct.pack('>B', bit_depth))
        block.write(struct.pack('>B', ct))
        block.write(struct.pack('>B', 0))  # zlib compression
        block.write(struct.pack('>B', 0))  # adaptative filter type
        block.write(struct.pack('>B', 0))  # not interlaced

        # Position equals the size of the block (omitting the header)
        handle.write(struct.pack('>I', block.tell()))

        full_block = b'IHDR' + block.getvalue()
        handle.write(full_block)
        handle.write(struct.pack('>I', zlib.crc32(full_block)))


def _write_IDAT(handle, data, width, height, color_type, default_pixel=None):
    """Writes the IDAT chunk, with the data given in a row-major order.
        Every line specifies that the current scan line has no filter applied.
    """
    if default_pixel is None:
        default_pixel = b'\0\0\0' if 'c' in color_type else b'\0'
    else:
        if not color_type:
            default_pixel = struct.pack('>B', default_pixel)
        elif color_type in 'c':
            default_pixel = (struct.pack('>B', default_pixel[0]) +
                             struct.pack('>B', default_pixel[1]) +
                             struct.pack('>B', default_pixel[2]))
        else:
            raise ValueError('Non-supported color_type given: ' + color_type)

    # TODO Not sure why irregular blocks don't work properly, it generates strange things
    with BytesIO() as block:
        if not color_type:
            # Gray-scale, 1 byte per pixel
            for i in range(len(data)):
                block.write(b'\0')  # No filter
                for j in range(len(data[i])):
                    block.write(struct.pack('>B', data[i][j]))

                # Default pixel for irregular (non-complete) rows
                for j in range(len(data[i]), width):
                    block.write(default_pixel)

            # Default pixel when not enough rows were provided
            for i in range(len(data), height):
                for j in range(width):
                    block.write(default_pixel)

        elif 'c' in color_type:
            # True color (RGB), 3 bytes per pixel
            for i in range(len(data)):
                block.write(b'\0')  # No filter
                for j in range(len(data[i])):
                    block.write(struct.pack('>B', data[i][j][0]))
                    block.write(struct.pack('>B', data[i][j][1]))
                    block.write(struct.pack('>B', data[i][j][2]))

                # Default pixel for irregular (non-complete) rows
                for j in range(len(data[i]), width):
                    block.write(default_pixel)

            # Default pixel when not enough rows were provided
            for i in range(len(data), height):
                for j in range(width):
                    block.write(default_pixel)
        else:
            raise ValueError('Non-supported color_type given: ' + color_type)

        compressor = zlib.compressobj()
        compressed = compressor.compress(block.getvalue())
        compressed += compressor.flush()

        full_block = b'IDAT' + compressed
        handle.write(struct.pack('>I', len(compressed)))
        handle.write(full_block)
        handle.write(struct.pack('>I', zlib.crc32(full_block)))


def _write_IEND(handle):
    """Writes the IEND chunk"""
    block = b'IEND'
    handle.write(struct.pack('>I', 0))
    handle.write(block)
    handle.write(struct.pack('>I', zlib.crc32(block)))


def save_png(handle, data, width=None, height=None,
             color_type=None, bit_depth=8, default_pixel=None):
    """Saves the .png described by the data to the output handle.

        The data can be an array of irregular dimensions, composed of either:
            - Single integer values < 256, color type is assumed grayscale
            - Tuples of 3 integers < 256, true color is assumed

        The color_type is also inferred from the first value on the data.

        If no bit_depth is defined, it is assumed to be 8 bits per channel.

        The default_pixel will default to black for either color type.
    """
    if height is None:
        height = len(data)
    elif height <= 0:
        raise ValueError('The height must be a value greater than 0')

    if width is None:
        # Irregular dimensions are allowed
        width = max(len(row) for row in data)
    elif width <= 0:
        raise ValueError('The width must be a value greater than 0')

    if color_type is None:
        # Infer the color type from the first datum
        if isinstance(data[0][0], int):
            color_type = ''
        else:
            # Assume it's an iterable of the correct length (tuple or list)
            color_type = 'c'

    # Header: 0x89, 'PNG', DOS line ending, EOF, Unix line ending
    handle.write(b'\x89PNG\r\n\x1A\n')

    _write_IHDR(handle, width, height, bit_depth, color_type)
    _write_IDAT(handle, data, width, height, color_type, default_pixel)
    _write_IEND(handle)


def color_to_rgb(color):
    return (
        (color >> 16) & 0xFF,
        (color >> 8) & 0xFF,
        color & 0xFF
    )


class ColorCommand(CommandBase):
    """Sends a color image for a given value"""
    def __init__(self):
        super().__init__(command='color',
                         examples=[
                             '/color #123ABC',
                             '/color #A2C',
                             '/color rgb(50, 100, 150)'
                         ])
        self.pats = []

    def act(self, data):
        if not data.parameter:
            self.show_invalid_syntax(data)
            return

        match = re.match(r'(?:#|0x)([0-9a-fA-F]{3,6})', data.parameter)
        if match:
            hex_color = match.group(1)
            if len(hex_color) not in [3, 6]:
                self.show_invalid_syntax(data)
                return

            if len(hex_color) == 3:
                hex_color = ''.join(h+h for h in hex_color)

            color = color_to_rgb(int(hex_color, base=16))


        match = re.match(r'rgb\s*\(\s*(\d+%?)\s*,\s*(\d+%?)\s*,\s*(\d+%?)\s*\)', data.parameter)
        if match:
            # Get the RGB matches
            rgb = [match.group(i) for i in range(1, 4)]

            # Map x% values to [0, 255]; do nothing with the rest
            color = tuple(
                int(255 * int(v[:-1]) / 100) if v[-1] == '%' else
                int(v) for v in rgb
            )
            if any(v < 0 or v > 255 for v in color):
                data.bot.send_message(data.chat, 'Invalid color range given.')
                return
        else:
            self.show_invalid_syntax(data)
            return

        with TemporaryFile('w+b') as f:
            # TODO So, irregular dimensions v (if not match with width height) cause weird bugs
            # So that's probably the problem with the width and height
            # Maybe it gets overrode
            # And does weird things
            size = 256
            color_data = [[color for j in range(size)] for i in range(size)]
            save_png(f,
                     data=color_data,
                     width=size,
                     height=size,
                     color_type='c')
            f.seek(0)
            data.bot.send_photo(data.chat, file_handle=f)
