cgrr-gamecube
=============

gci.py provides functions to read GameCube GCI files.

Usage
=====

Reading a GCI file:

```python
>>> import gci
>>> gci.read_gci("test.gci")
{'m_gci_header': {'AnimSpeed': [<AnimSpeed.ANIM_NO_ICON: 0>,
                                <AnimSpeed.ANIM_NO_ICON: 0>,
                                <AnimSpeed.ANIM_12_FRAMES: 3>,
                                <AnimSpeed.ANIM_12_FRAMES: 3>,
                                <AnimSpeed.ANIM_12_FRAMES: 3>,
                                <AnimSpeed.ANIM_12_FRAMES: 3>,
                                <AnimSpeed.ANIM_12_FRAMES: 3>,
                                <AnimSpeed.ANIM_12_FRAMES: 3>],
                  'BIFlags': <BIFlags.BANNER_CI8: 1>,
                  'BlockCount': 3,
                  'CommentsAddr': 0,
                  'CopyCounter': 1,
                  'Filename': 'TestFile',
                  'FirstBlock': 42,
                  'Gamecode': 'TEST',
                  'IconFmt': [<IconFmt.ICON_NONE: 0>,
                              <IconFmt.ICON_NONE: 0>,
                              <IconFmt.ICON_CI8_SHARED: 1>,
                              <IconFmt.ICON_NONE: 0>,
                              <IconFmt.ICON_NONE: 0>,
                              <IconFmt.ICON_CI8_SHARED: 1>,
                              <IconFmt.ICON_NONE: 0>,
                              <IconFmt.ICON_CI8_SHARED: 1>],
                  'ImageOffset': 64,
                  'Makercode': '01',
                  'ModTime': datetime.datetime(2011, 11, 12, 18, 5, 10),
                  'Permissions': {<Permissions.PERM_NO_COPY: 4>},
                  'Unused1': 255,
                  'Unused2': 65535}
 'm_save_data': [b"This is a test GCI file. The data here should be a..."]
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
