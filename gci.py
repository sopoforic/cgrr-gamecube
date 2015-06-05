# Classic Game Resource Reader (CGRR): Parse resources from classic games.
# Copyright (C) 2014  Tracy Poff
#
# This file is part of CGRR.
#
# CGRR is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CGRR is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CGRR.  If not, see <http://www.gnu.org/licenses/>.
"""Parses GameCube GCI files."""
try:
    from enum import Enum
except ImportError:
    from enum34 import Enum

from datetime import datetime, timedelta

from cgrr import FileReader

from graphics import parse_ci8

key = "gamecube_gci_a"
title = "GameCube GCI File"

epoch = datetime(2000,1,1) # TODO: should it be datetime(1999,12,31,23,59,59)?

# 1 -> True, 0 -> False
def int_to_bitfield(s):
    return lambda r: [bool((r >> ((s-1) - n) & 1)) for n in range(s)]
# True -> 1, False -> 0
def bitfield_to_int(s):
    return lambda r: sum([2 ** n for n in range(s) if r[(s-1)-n]])

class BIFlags(Enum):
    BANNER_NONE   = 0b00
    BANNER_CI8    = 0b01
    BANNER_RGB5A3 = 0b10
    BANNER_11     = 0b11 # used by time splitters 2 and 3, which have no banner

class IconFmt(Enum):
    ICON_NONE       = 0b00
    ICON_CI8_SHARED = 0b01
    ICON_RGB5A3     = 0b10
    ICON_CI8_UNIQUE = 0b11

class AnimSpeed(Enum):
    ANIM_NO_ICON   = 0b00
    ANIM_4_FRAMES  = 0b01
    ANIM_8_FRAMES  = 0b10
    ANIM_12_FRAMES = 0b11

class Permissions(Enum):
    PERM_NO_MOVE = 0b1000
    PERM_NO_COPY = 0b0100
    PERM_PUBLIC  = 0b0010

def to_iconfmt(num):
    bf = int_to_bitfield(16)(num)
    iconfmt = [IconFmt(bitfield_to_int(2)(bf[i:i+2])) for i in range(0,16,2)]
    return iconfmt

def from_iconfmt(iconfmt):
    l = [i for sl in [int_to_bitfield(2)(i.value) for i in iconfmt] for i in sl]
    num = bitfield_to_int(16)(l)
    return num

def to_animspeed(num):
    bf = int_to_bitfield(16)(num)
    anim = [AnimSpeed(bitfield_to_int(2)(bf[i:i+2])) for i in range(0,16,2)]
    return anim

def from_animspeed(anim):
    l = [i for sl in [int_to_bitfield(2)(i.value) for i in anim] for i in sl]
    num = bitfield_to_int(16)(l)
    return num

def to_permissions(num):
    permissions = set(p for p in Permissions if not p.value ^ num)
    return permissions

def from_permissions(permissions):
    return sum(p.value for p in permissions)

# Based on code from Dolphin in Source/Core/Core/HW/GCMemcard.h
# The names here match the names used there.
gci_header_format = [       # Offset  Size    Notes
    ("Gamecode",    "4s"),  # 0x00    0x04    the fourth byte is the region code
    ("Makercode",   "2s"),  # 0x04    0x02
    ("Unused1",     "B"),   # 0x06    0x01    always 0xff
    ("BIFlags",     "B"),   # 0x07    0x01
    ("Filename",    "32s"), # 0x08    0x20
    ("ModTime",     "L"),   # 0x28    0x04    seconds since 2000-01-01 00:00:00
    ("ImageOffset", "L"),   # 0x2c    0x04
    ("IconFmt", "H"),       # 0x30    0x02
    ("AnimSpeed", "H"),     # 0x32    0x02
    ("Permissions", "B"),   # 0x34    0x01
    ("CopyCounter", "B"),   # 0x35    0x01
    ("FirstBlock", "H"),    # 0x36    0x02    # of first block of file (0 == offset 0)
    ("BlockCount", "H"),    # 0x38    0x02    file length (# of blocks in file)
    ("Unused2", "H"),       # 0x3a    0x02    always 0xffff
    ("CommentsAddr", "L"),  # 0x3c    0x04
]

gci_header_reader = FileReader(
    format = gci_header_format,
    massage_in = {
        "Gamecode"    : (lambda s: s.decode('ascii').strip('\x00')),
        "Makercode"   : (lambda s: s.decode('ascii').strip('\x00')),
        "BIFlags"     : (BIFlags),
        "Filename"    : (lambda s: s.decode('ascii').strip('\x00')),
        "ModTime"     : (lambda t: (epoch + timedelta(seconds=t))),
        "IconFmt"     : (to_iconfmt),
        "AnimSpeed"   : (to_animspeed),
        "Permissions" : (to_permissions),
    },
    massage_out = {
        "Gamecode"    : (lambda s: s.encode('ascii')),
        "Makercode"   : (lambda s: s.encode('ascii')),
        "BIFlags"     : (lambda b: b.value),
        "Filename"    : (lambda s: s.encode('ascii')),
        "ModTime"     : (lambda t: ((t - epoch).days*86400 + (t - epoch).seconds)),
        "IconFmt"     : (from_iconfmt),
        "AnimSpeed"   : (from_animspeed),
        "Permissions" : (from_permissions),
    },
    byte_order = ">"
)

HEADER_LENGTH = gci_header_reader.struct.size

def get_gci_reader(path=None, block_count=None):
    """Return a FileReader suited to a particular GCI file.

    Since GCI files are of variable length, this function determines the length
    of the GCI file given by path and returns an appropriate FileReader.

    Alternatively, if given a block_count, this function produces a FileReader
    that for a GCI file with that many blocks. This is particularly useful when
    writing a GCI file from its dictionary representation.

    """
    if not block_count:
        header = read_header(path)
        block_count = header['BlockCount']
    data_length = block_count * 8192
    gcifile_format = [
        ("m_gci_header", "{}s".format(HEADER_LENGTH)),
        ("m_save_data", "{}s".format(data_length)),
    ]
    gci_reader = FileReader(
        format = gcifile_format,
        massage_in = {
            "m_gci_header" : gci_header_reader.unpack,
            "m_save_data"  : (lambda s: [s[i:i+8192] for i in range(0, data_length, 8192)])
        },
        massage_out = {
            "m_gci_header" : gci_header_reader.pack,
            "m_save_data"  : b"".join,
        },
    )
    return gci_reader

def read_header(path):
    """Return the header of a GCI file located on disk."""
    with open(path, "rb") as gcifile:
        data = gcifile.read(HEADER_LENGTH)
    header = parse_header(data)
    return header

def parse_header(data):
    """Parse the header given as a bytestring."""
    header = gci_header_reader.unpack(data)
    return header

def read_gci(path):
    """Parse and return a GCI file located on disk."""
    with open (path, "rb") as gcifile:
        data = gcifile.read()
    gci = parse_gci(data)
    return gci

def parse_gci(data):
    """Parse and return a bytestring representing a GCI file."""
    block_count = parse_header(data[:HEADER_LENGTH])['BlockCount']
    gci_reader = get_gci_reader(block_count=block_count)
    gci = gci_reader.unpack(data)
    return gci

def write_gci(gci): # TODO: rename?
    """Return a bytestring representing a GCI file."""
    block_count = gci['m_gci_header']['BlockCount']
    data = get_gci_reader(block_count=block_count).pack(gci)
    return data

def parse_extra_data(gci):
    """Parses additional (non-header) data in a gci."""
    extra = {}
    offset = gci['m_gci_header']['CommentsAddr']
    extra['game_name'] = gci['m_save_data'][0][offset:offset+32].decode('ascii').rstrip('\x00')
    extra['file_info'] = gci['m_save_data'][0][offset+32:offset+64].decode('ascii').rstrip('\x00')
    # TODO: decode icon and other banner format
    if gci['m_gci_header']['BIFlags'] == BIFlags.BANNER_CI8:
        offset = gci['m_gci_header']['ImageOffset']
        block = gci['m_save_data'][0]
        data = block[offset:offset+3584]
        img = parse_ci8(data, 96)
        extra['banner'] = img
    else:
        # raise NotImplementedError("This banner format is not yet supported.")
        pass
    return extra
