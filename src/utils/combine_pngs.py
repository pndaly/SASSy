#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# +
# import(s)
# -
from src import *
from PIL import Image

import argparse
import os
import requests


# +
# function: jpg_to_png()
# -
# noinspection PyBroadException
def jpg_to_png(_jpg=None):

    # check input(s)
    if _jpg is None or not isinstance(_jpg, str) or _jpg.strip() == '':
        return
    _jpg_file = os.path.abspath(os.path.expanduser(_jpg))
    if not os.path.exists(_jpg_file):
        return

    # convert
    try:
        _png_file = _jpg_file.replace('.jpg', '.png')
        _data = Image.open(_jpg)
        _data.save(_png_file)
        return _png_file
    except:
        return


# +
# function: combine_pngs()
# -
def combine_pngs(_files=None, _output='', _log=None):

    # check input(s)
    if _files is None or not isinstance(_files, list) or _files is []:
        return
    if not isinstance(_output, str) or _output.strip() == '':
        return

    # message
    if _log:
        _log.debug(f'_files={_files}, _output={_output}')

    # combine PNGs
    _images = [Image.open(_x) for _x in _files]
    _widths, _heights = zip(*(i.size for i in _images))
    _twidth, _theight, _xoff = sum(_widths), max(_heights), 0
    _finder = Image.new('RGB', (_twidth, _theight))
    for _im in _images:
        if _log:
            _log.debug(f'Adding {_im} to {_output}')
        _finder.paste(_im, (_xoff, 0))
        _xoff += _im.size[0]

    # save output
    try:
        _finder.save(_output)
        return _output
    except Exception as _s:
        if _log:
            _log.error(f'Failed to save output, error={_s}')


# +
# main()
# -
if __name__ == '__main__':

    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description='Combine PNG Files', formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('--files', default='', help="""Files to combine""")

    # execute
    args = _p.parse_args()
    combine_pngs(_files=args.files)
