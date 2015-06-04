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
from cgrr import FileReader

key = "gamecube_gci_a"
title = "GameCube GCI File"

# Based on code from Dolphin in Source/Core/Core/HW/GCMemcard.h
# TODO: decode flags
gci_header_format = [       # Offset  Size    Notes
    ("Gamecode",    "4s"),  # 0x00    0x04
    ("Makercode",   "2s"),  # 0x04    0x02
    ("Unused1",     "B"),   # 0x06    0x01    Always 0xff
    ("BIFlags",     "B"),   # 0x07    0x01
    ("Filename",    "32s"), # 0x08    0x20
    ("ModTime",     "L"),   # 0x28    0x04    Seconds since 2000-01-01 00:00:00
    ("ImageOffset", "L"),   # 0x2c    0x04
    ("IconFmt", "H"),       # 0x30    0x02
    ("AnimSpeed", "H"),     # 0x32    0x02
    ("Permissions", "B"),   # 0x34    0x01
    ("CopyCounter", "B"),   # 0x35    0x01
    ("FirstBlock", "H"),    # 0x36    0x02    # of first block of file (0 == offset 0)
    ("BlockCount", "H"),    # 0x38    0x02    File length (# of blocks in file)
    ("Unused2", "H"),       # 0x3a    0x02    Always 0xffff
    ("CommentsAddr", "L"),  # 0x3c    0x04
]

gci_header_reader = FileReader(
    format = gci_header_format,
    massage_in = {
        "Gamecode"  : (lambda s: s.decode('ascii').strip('\x00')),
        "Makercode" : (lambda s: s.decode('ascii').strip('\x00')),
        "Filename"  : (lambda s: s.decode('ascii').strip('\x00')),
    },
    massage_out = {
        "Gamecode"  : (lambda s: s.encode('ascii')),
        "Makercode" : (lambda s: s.encode('ascii')),
        "Filename"  : (lambda s: s.encode('ascii')),
    },
    byte_order = ">"
)

def get_gci_reader(path):
    header = read_header(path)
    data_length = header['BlockCount']*8192
    gcifile_format = [
        ("m_gci_header", "{}s".format(gci_header_reader.struct.size)),
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
            "m_save_data"  : "".join,
        },
    )
    return gci_reader

def read_header(path):
    with open(path, "rb") as gcifile:
        data = gcifile.read(gci_header_reader.struct.size)
    header = gci_header_reader.unpack(data)
    return header

def read_gci(path):
    gci_reader = get_gci_reader(path)
    with open (path, "rb") as gcifile:
        data = gcifile.read()
    gci = gci_reader.unpack(data)
    return gci
