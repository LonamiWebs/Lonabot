import random

from commands.command_base import CommandBase
from tempfile import TemporaryFile
import re
import zlib
import struct
from io import BytesIO


html_color_names = {
    'black': 0x000000,
    'night': 0x0C090A,
    'gunmetal': 0x2C3539,
    'midnight': 0x2B1B17,
    'charcoal': 0x34282C,
    'dark slate grey': 0x25383C,
    'oil': 0x3B3131,
    'black cat': 0x413839,
    'iridium': 0x3D3C3A,
    'black eel': 0x463E3F,
    'black cow': 0x4C4646,
    'gray wolf': 0x504A4B,
    'vampire gray': 0x565051,
    'gray dolphin': 0x5C5858,
    'carbon gray': 0x625D5D,
    'ash gray': 0x666362,
    'cloudy gray': 0x6D6968,
    'smokey gray': 0x726E6D,
    'gray': 0x736F6E,
    'granite': 0x837E7C,
    'battleship gray': 0x848482,
    'gray cloud': 0xB6B6B4,
    'gray goose': 0xD1D0CE,
    'platinum': 0xE5E4E2,
    'metallic silver': 0xBCC6CC,
    'blue gray': 0x98AFC7,
    'light slate gray': 0x6D7B8D,
    'slate gray': 0x657383,
    'jet gray': 0x616D7E,
    'mist blue': 0x646D7E,
    'marble blue': 0x566D7E,
    'slate blue': 0x737CA1,
    'steel blue': 0x4863A0,
    'blue jay': 0x2B547E,
    'dark slate blue': 0x2B3856,
    'midnight blue': 0x151B54,
    'navy blue': 0x000080,
    'blue whale': 0x342D7E,
    'lapis blue': 0x15317E,
    'denim dark blue': 0x151B8D,
    'earth blue': 0x0000A0,
    'cobalt blue': 0x0020C2,
    'blueberry blue': 0x0041C2,
    'sapphire blue': 0x2554C7,
    'blue eyes': 0x1569C7,
    'royal blue': 0x2B60DE,
    'blue orchid': 0x1F45FC,
    'blue lotus': 0x6960EC,
    'light slate blue': 0x736AFF,
    'windows blue': 0x357EC7,
    'glacial blue ice': 0x368BC1,
    'silk blue': 0x488AC7,
    'blue ivy': 0x3090C7,
    'blue koi': 0x659EC7,
    'columbia blue': 0x87AFC7,
    'baby blue': 0x95B9C7,
    'light steel blue': 0x728FCE,
    'ocean blue': 0x2B65EC,
    'blue ribbon': 0x306EFF,
    'blue dress': 0x157DEC,
    'dodger blue': 0x1589FF,
    'cornflower blue': 0x6495ED,
    'sky blue': 0x6698FF,
    'butterfly blue': 0x38ACEC,
    'iceberg': 0x56A5EC,
    'crystal blue': 0x5CB3FF,
    'deep sky blue': 0x3BB9FF,
    'denim blue': 0x79BAEC,
    'light sky blue': 0x82CAFA,
    'day sky blue': 0x82CAFF,
    'jeans blue': 0xA0CFEC,
    'blue angel': 0xB7CEEC,
    'pastel blue': 0xB4CFEC,
    'sea blue': 0xC2DFFF,
    'powder blue': 0xC6DEFF,
    'coral blue': 0xAFDCEC,
    'light blue': 0xADDFFF,
    'robin egg blue': 0xBDEDFF,
    'pale blue lily': 0xCFECEC,
    'light cyan': 0xE0FFFF,
    'water': 0xEBF4FA,
    'aliceblue': 0xF0F8FF,
    'azure': 0xF0FFFF,
    'light slate': 0xCCFFFF,
    'light aquamarine': 0x93FFE8,
    'electric blue': 0x9AFEFF,
    'aquamarine': 0x7FFFD4,
    'cyan or aqua': 0x00FFFF,
    'tron blue': 0x7DFDFE,
    'blue zircon': 0x57FEFF,
    'blue lagoon': 0x8EEBEC,
    'celeste': 0x50EBEC,
    'blue diamond': 0x4EE2EC,
    'tiffany blue': 0x81D8D0,
    'cyan opaque': 0x92C7C7,
    'blue hosta': 0x77BFC7,
    'northern lights blue': 0x78C7C7,
    'medium turquoise': 0x48CCCD,
    'turquoise': 0x43C6DB,
    'jellyfish': 0x46C7C7,
    'blue green': 0x7BCCB5,
    'macaw blue green': 0x43BFC7,
    'light sea green': 0x3EA99F,
    'dark turquoise': 0x3B9C9C,
    'sea turtle green': 0x438D80,
    'medium aquamarine': 0x348781,
    'greenish blue': 0x307D7E,
    'grayish turquoise': 0x5E7D7E,
    'beetle green': 0x4C787E,
    'teal': 0x008080,
    'sea green': 0x4E8975,
    'camouflage green': 0x78866B,
    'sage green': 0x848b79,
    'hazel green': 0x617C58,
    'venom green': 0x728C00,
    'fern green': 0x667C26,
    'dark forest green': 0x254117,
    'medium sea green': 0x306754,
    'medium forest green': 0x347235,
    'seaweed green': 0x437C17,
    'pine green': 0x387C44,
    'jungle green': 0x347C2C,
    'shamrock green': 0x347C17,
    'medium spring green': 0x348017,
    'forest green': 0x4E9258,
    'green onion': 0x6AA121,
    'spring green': 0x4AA02C,
    'lime green': 0x41A317,
    'clover green': 0x3EA055,
    'green snake': 0x6CBB3C,
    'alien green': 0x6CC417,
    'green apple': 0x4CC417,
    'yellow green': 0x52D017,
    'kelly green': 0x4CC552,
    'zombie green': 0x54C571,
    'frog green': 0x99C68E,
    'green peas': 0x89C35C,
    'dollar bill green': 0x85BB65,
    'dark sea green': 0x8BB381,
    'iguana green': 0x9CB071,
    'avocado green': 0xB2C248,
    'pistachio green': 0x9DC209,
    'salad green': 0xA1C935,
    'hummingbird green': 0x7FE817,
    'nebula green': 0x59E817,
    'stoplight go green': 0x57E964,
    'algae green': 0x64E986,
    'jade green': 0x5EFB6E,
    'green': 0x00FF00,
    'emerald green': 0x5FFB17,
    'lawn green': 0x87F717,
    'chartreuse': 0x8AFB17,
    'dragon green': 0x6AFB92,
    'mint green': 0x98FF98,
    'green thumb': 0xB5EAAA,
    'light jade': 0xC3FDB8,
    'tea green': 0xCCFB5D,
    'green yellow': 0xB1FB17,
    'slime green': 0xBCE954,
    'goldenrod': 0xEDDA74,
    'harvest gold': 0xEDE275,
    'sun yellow': 0xFFE87C,
    'yellow': 0xFFFF00,
    'corn yellow': 0xFFF380,
    'parchment': 0xFFFFC2,
    'cream': 0xFFFFCC,
    'lemon chiffon': 0xFFF8C6,
    'cornsilk': 0xFFF8DC,
    'beige': 0xF5F5DC,
    'blonde': 0xFBF6D9,
    'antiquewhite': 0xFAEBD7,
    'champagne': 0xF7E7CE,
    'blanchedalmond': 0xFFEBCD,
    'vanilla': 0xF3E5AB,
    'tan brown': 0xECE5B6,
    'peach': 0xFFE5B4,
    'mustard': 0xFFDB58,
    'rubber ducky yellow': 0xFFD801,
    'bright gold': 0xFDD017,
    'golden brown': 0xEAC117,
    'macaroni and cheese': 0xF2BB66,
    'saffron': 0xFBB917,
    'beer': 0xFBB117,
    'cantaloupe': 0xFFA62F,
    'bee yellow': 0xE9AB17,
    'brown sugar': 0xE2A76F,
    'burlywood': 0xDEB887,
    'deep peach': 0xFFCBA4,
    'ginger brown': 0xC9BE62,
    'school bus yellow': 0xE8A317,
    'sandy brown': 0xEE9A4D,
    'fall leaf brown': 0xC8B560,
    'orange gold': 0xD4A017,
    'sand': 0xC2B280,
    'cookie brown': 0xC7A317,
    'caramel': 0xC68E17,
    'brass': 0xB5A642,
    'khaki': 0xADA96E,
    'camel brown': 0xC19A6B,
    'bronze': 0xCD7F32,
    'tiger orange': 0xC88141,
    'cinnamon': 0xC58917,
    'bullet shell': 0xAF9B60,
    'dark goldenrod': 0xAF7817,
    'copper': 0xB87333,
    'wood': 0x966F33,
    'oak brown': 0x806517,
    'moccasin': 0x827839,
    'army brown': 0x827B60,
    'sandstone': 0x786D5F,
    'mocha': 0x493D26,
    'taupe': 0x483C32,
    'coffee': 0x6F4E37,
    'brown bear': 0x835C3B,
    'red dirt': 0x7F5217,
    'sepia': 0x7F462C,
    'orange salmon': 0xC47451,
    'rust': 0xC36241,
    'red fox': 0xC35817,
    'chocolate': 0xC85A17,
    'sedona': 0xCC6600,
    'papaya orange': 0xE56717,
    'halloween orange': 0xE66C2C,
    'pumpkin orange': 0xF87217,
    'construction cone orange': 0xF87431,
    'sunrise orange': 0xE67451,
    'mango orange': 0xFF8040,
    'dark orange': 0xF88017,
    'coral': 0xFF7F50,
    'basket ball orange': 0xF88158,
    'light salmon': 0xF9966B,
    'tangerine': 0xE78A61,
    'dark salmon': 0xE18B6B,
    'light coral': 0xE77471,
    'bean red': 0xF75D59,
    'valentine red': 0xE55451,
    'shocking orange': 0xE55B3C,
    'red': 0xFF0000,
    'scarlet': 0xFF2400,
    'ruby red': 0xF62217,
    'ferrari red': 0xF70D1A,
    'fire engine red': 0xF62817,
    'lava red': 0xE42217,
    'love red': 0xE41B17,
    'grapefruit': 0xDC381F,
    'chestnut red': 0xC34A2C,
    'cherry red': 0xC24641,
    'mahogany': 0xC04000,
    'chilli pepper': 0xC11B17,
    'cranberry': 0x9F000F,
    'red wine': 0x990012,
    'burgundy': 0x8C001A,
    'chestnut': 0x954535,
    'blood red': 0x7E3517,
    'sienna': 0x8A4117,
    'sangria': 0x7E3817,
    'firebrick': 0x800517,
    'maroon': 0x810541,
    'plum pie': 0x7D0541,
    'velvet maroon': 0x7E354D,
    'plum velvet': 0x7D0552,
    'rosy finch': 0x7F4E52,
    'puce': 0x7F5A58,
    'dull purple': 0x7F525D,
    'rosy brown': 0xB38481,
    'khaki rose': 0xC5908E,
    'pink bow': 0xC48189,
    'lipstick pink': 0xC48793,
    'rose': 0xE8ADAA,
    'rose gold': 0xECC5C0,
    'desert sand': 0xEDC9AF,
    'pig pink': 0xFDD7E4,
    'cotton candy': 0xFCDFFF,
    'pink bubblegum': 0xFFDFDD,
    'misty rose': 0xFBBBB9,
    'pink': 0xFAAFBE,
    'light pink': 0xFAAFBA,
    'flamingo pink': 0xF9A7B0,
    'pink rose': 0xE7A1B0,
    'pink daisy': 0xE799A3,
    'cadillac pink': 0xE38AAE,
    'carnation pink': 0xF778A1,
    'blush red': 0xE56E94,
    'hot pink': 0xF660AB,
    'watermelon pink': 0xFC6C85,
    'violet red': 0xF6358A,
    'deep pink': 0xF52887,
    'pink cupcake': 0xE45E9D,
    'pink lemonade': 0xE4287C,
    'neon pink': 0xF535AA,
    'magenta': 0xFF00FF,
    'dimorphotheca magenta': 0xE3319D,
    'bright neon pink': 0xF433FF,
    'pale violet red': 0xD16587,
    'tulip pink': 0xC25A7C,
    'medium violet red': 0xCA226B,
    'rogue pink': 0xC12869,
    'burnt pink': 0xC12267,
    'bashful pink': 0xC25283,
    'dark carnation pink': 0xC12283,
    'plum': 0xB93B8F,
    'viola purple': 0x7E587E,
    'purple iris': 0x571B7E,
    'plum purple': 0x583759,
    'indigo': 0x4B0082,
    'purple monster': 0x461B7E,
    'purple haze': 0x4E387E,
    'eggplant': 0x614051,
    'grape': 0x5E5A80,
    'purple jam': 0x6A287E,
    'dark orchid': 0x7D1B7E,
    'purple flower': 0xA74AC7,
    'medium orchid': 0xB048B5,
    'purple amethyst': 0x6C2DC7,
    'dark violet': 0x842DCE,
    'violet': 0x8D38C9,
    'purple sage bush': 0x7A5DC7,
    'lovely purple': 0x7F38EC,
    'purple': 0x8E35EF,
    'aztech purple': 0x893BFF,
    'medium purple': 0x8467D7,
    'jasmine purple': 0xA23BEC,
    'purple daffodil': 0xB041FF,
    'tyrian purple': 0xC45AEC,
    'crocus purple': 0x9172EC,
    'purple mimosa': 0x9E7BFF,
    'heliotrope purple': 0xD462FF,
    'crimson': 0xE238EC,
    'purple dragon': 0xC38EC7,
    'lilac': 0xC8A2C8,
    'blush pink': 0xE6A9EC,
    'mauve': 0xE0B0FF,
    'wisteria purple': 0xC6AEC7,
    'blossom pink': 0xF9B7FF,
    'thistle': 0xD2B9D3,
    'periwinkle': 0xE9CFEC,
    'lavender pinocchio': 0xEBDDE2,
    'lavender blue': 0xE3E4FA,
    'pearl': 0xFDEEF4,
    'seashell': 0xFFF5EE,
    'milk white': 0xFEFCFF,
    'white': 0xFFFFFF
}


def _write_IHDR(handle, width, height, bit_depth, color_type):
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
        block.write(struct.pack('>B', 0))  # Adaptive filter type
        block.write(struct.pack('>B', 0))  # Not interlaced

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
                block.write(b'\0')  # No filter
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
    if height <= 0:
        raise ValueError('The height must be a value greater than 0.')

    if width is None:
        # Irregular dimensions are allowed
        width = max(len(row) for row in data)
    if width <= 0:
        raise ValueError('The width must be a value greater than 0.')

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
                             '/color #a2c',
                             '/color rgb(50, 100, 150)',
                             '/color rgb(100%, 55%, 10%)',
                             '/color indigo',
                             '/color random'
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
            self.send_rgb(data, color)
            return

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

            self.send_rgb(data, color)
            return

        data.parameter = data.parameter.lower()
        if data.parameter in html_color_names:
            self.send_rgb(data, color_to_rgb(html_color_names[data.parameter]))
            return

        if data.parameter == 'random':
            values = list(html_color_names.values())
            self.send_rgb(data, color_to_rgb(random.choice(values)))
            return

        self.show_invalid_syntax(data)

    @staticmethod
    def send_rgb(data, color):
        with TemporaryFile('w+b') as f:
            size = 256
            save_png(f,
                     data=[[]],
                     width=size,
                     height=size,
                     color_type='c',
                     default_pixel=color)
            f.seek(0)
            data.bot.send_photo(data.chat, file_handle=f)
