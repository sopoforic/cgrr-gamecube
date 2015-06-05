cgrr-gamecube
=============

gci.py provides functions to read GameCube GCI files.

Usage
=====

Reading a GCI file:

```python
>>> import gci
>>> gci.read_gci("test.gci")
{'m_gci_header': {'AnimSpeed': 4095,
                  'BIFlags': <BIFlags.BANNER_CI8: 1>,
                  'BlockCount': 3,
                  'CommentsAddr': 0,
                  'CopyCounter': 1,
                  'Filename': 'TestFile',
                  'FirstBlock': 42,
                  'Gamecode': 'TEST',
                  'IconFmt': 1041,
                  'ImageOffset': 64,
                  'Makercode': '01',
                  'ModTime': datetime.datetime(2011, 11, 12, 18, 5, 10),
                  'Permissions': 4,
                  'Unused1': 255,
                  'Unused2': 65535}
 'm_save_data': [b"This is a test GCI file. The data here should be a part of
 the first block. After this, it's all zeroes until the next block.\x00\x00..."]
 ```

Editing a gci file:

```python
import gci
g = gci.read_gci("test.gci")
g['m_gci_header']['GameCode'] = "EDIT"
g['m_gci_header']['Filename'] = "EditedFileName"
data = gci.write_gci(g)
with open("edited.gci") as out:
    out.write(data)
```

Requirements
============

* Python 2.7+ or 3.2+
* cgrr from https://github.com/sopoforic/cgrr
* enums
    * These are part of python 3.4+
    * For older python versions, `pip install enum34`

You can install cgrr with `pip install -r requirements.txt`.

License
=======

This module is available under the GPL v3 or later. See the file COPYING for
details.

[![Build Status](https://travis-ci.org/sopoforic/cgrr-gamecube.svg?branch=master)](https://travis-ci.org/sopoforic/cgrr-gamecube)
[![Code Health](https://landscape.io/github/sopoforic/cgrr-gamecube/master/landscape.svg?style=flat)](https://landscape.io/github/sopoforic/cgrr-gamecube/master)
