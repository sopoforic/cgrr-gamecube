from PIL import Image

def parse_ci8(data, width):
    if ((len(data) - 512)/4) % width != 0:
        raise ValueError("Invalid number of tiles for width {}".format(width))
    height = (len(data) - 512)//width
    palette = parse_palette(data[-512:])
    img = Image.new("RGBA", size=(width, height))
    imgdata = reorder_tiles(data[:-512], width)
    try:
        pixmap = [palette[pixel] for pixel in imgdata]
    except TypeError:
        # python 2
        pixmap = [palette[ord(pixel)] for pixel in imgdata]
    img.putdata(pixmap)
    return img

def parse_palette(data):
    if len(data) != 512:
        raise ValueError("Palette length must be 512 bytes.")
    palette = []
    for a, b in (data[i:i+2] for i in range(0, 512, 2)):
        try:
            value = (a << 8) + b
        except TypeError:
            # python 2
            value = (ord(a) << 8) + ord(b)
        bf = int_to_bitfield(16)(value)
        # These are five bits per channel plus a transparency bit, for a total
        # of 16 bits per pixel.
        transparent = 0xff if bf[0] else 0x00
        red = five_to_eight(bitfield_to_int(5)(bf[1:6]))
        green = five_to_eight(bitfield_to_int(5)(bf[6:11]))
        blue = five_to_eight(bitfield_to_int(5)(bf[11:]))
        palette.append((red, green, blue, transparent))
    return palette

def reorder_tiles(data, width):
    tiles_per_row = width//8
    tile_rows = len(data)//(width*4)
    newdata = b''
    # This is an awful monstrosity, but all it's doing is reordering the data so
    # that instead of being ordered in 8x4 tiles, it's all just in a line, one
    # row at a time.
    for tile_row in range(tile_rows):
        for row in range(4):
            for tile in range(tiles_per_row):
                newdata += data[(tile_row*32*tiles_per_row) + (row*8) + (32*tile):(tile_row*32*tiles_per_row) + (row*8)+(32*tile)+8]
    return newdata

# 1 -> True, 0 -> False
def int_to_bitfield(s):
    return lambda r: [bool((r >> ((s-1) - n) & 1)) for n in range(s)]
# True -> 1, False -> 0
def bitfield_to_int(s):
    return lambda r: sum([2 ** n for n in range(s) if r[(s-1)-n]])

def five_to_eight(num):
    """Changes a 5-bit color to 8-bit."""
    # colors used by Dolphin in Source/Core/Common/ColorUtil.cpp
    colors = [0x00,0x08,0x10,0x18,0x20,0x29,0x31,0x39,
	          0x41,0x4A,0x52,0x5A,0x62,0x6A,0x73,0x7B,
	          0x83,0x8B,0x94,0x9C,0xA4,0xAC,0xB4,0xBD,
	          0xC5,0xCD,0xD5,0xDE,0xE6,0xEE,0xF6,0xFF]
    return colors[num]
