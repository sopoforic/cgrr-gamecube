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
            color = (a << 8) + b
        except TypeError:
            # python 2
            color = (ord(a) << 8) + ord(b)
        palette.append(gc_to_rgba(color))
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

def gc_to_rgba(color):
    bf = int_to_bitfield(16)(color)
    if bf[0]:
        # no transparency
        alpha = 0
        red = bitfield_to_int(5)(bf[1:6]) * 0x8
        green = bitfield_to_int(5)(bf[6:11]) * 0x8
        blue = bitfield_to_int(5)(bf[11:]) * 0x8
    else:
        alpha = bitfield_to_int(3)(bf[1:4]) * 0x20
        red = bitfield_to_int(4)(bf[4:8]) * 0x11
        green = bitfield_to_int(4)(bf[8:12]) * 0x11
        blue = bitfield_to_int(4)(bf[12:]) * 0x11
    return (red, green, blue, alpha)
