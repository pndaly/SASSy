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
# constant(s)
# -
SDSS_HEIGHT = 400
SDSS_SCALE = 0.79224/2.0
SDSS_SCALES = (1.0*SDSS_SCALE, 2.0*SDSS_SCALE, 3.0*SDSS_SCALE, 4.0*SDSS_SCALE)
SDSS_WIDTH = 400
SDSS_URL = 'http://skyserver.sdss.org/dr16/SkyServerWS/ImgCutout/getjpeg'


# +
# function: get_sdss_image()
# -
# noinspection PyBroadException
def get_sdss_image(**kw):

    # get critical input(s): RA, Dec
    try:
        _ra = kw['ra']
        _dec = kw['dec']
        _log = kw['log']
    except Exception as _v:
        raise Exception('No RA/Dec input(s), error={_v}')

    # message
    if _log is not None:
        _log.debug(f'_ra={_ra}, _dec={_dec}')

    # set default(s) [NB: plate scale default is 2x the SDSS value]
    _ra_str = _ra.replace('.', '').replace(':', '').replace(' ', '').strip()[:6]
    _dec_str = _dec.replace('.', '').replace(':', '').replace(' ', '').replace('-', '').replace('+', '').strip()[:6]
    _scale = kw['scale'] if \
        ('scale' in kw and isinstance(kw['scale'], float) and kw['scale'] in SDSS_SCALES) else SDSS_SCALES[0]
    _width = kw['width'] if \
        ('width' in kw and isinstance(kw['width'], int) and kw['width'] > 0) else SDSS_WIDTH
    _height = kw['height'] if \
        ('height' in kw and isinstance(kw['height'], int) and kw['height'] > 0) else SDSS_HEIGHT
    _opt = kw['opt'] if ('opt' in kw and isinstance(kw['opt'], str) and kw['opt'].strip() != '') else 'GL'
    _query = kw['query'] if ('query' in kw and isinstance(kw['query'], str) and kw['query'].strip() != '') else ''
    _jpg = kw['jpg'] if ('jpg' in kw and isinstance(kw['jpg'], str) and kw['jpg'].strip() != '') else \
        f'sdss_{_ra_str}_{_dec_str}.jpg'
    _url, _req = f"{SDSS_URL}?ra={ra_to_decimal(_ra)}&dec={dec_to_decimal(_dec)}&scale={_scale}&" \
                 f"width={_width}&height={_height}&opt={_opt}&query={_query}", None

    if _log:
        _log.debug(f"_url={_url}")

    # request data
    try:
        _req = requests.get(url=f'{_url}')
    except Exception as _e:
        raise Exception(f"failed to complete request, _req={_req}, error={_e}")

    # if everything is ok, create the jpg image and return the path
    if _req is not None and hasattr(_req, 'status_code') and (_req.status_code == 200) and hasattr(_req, 'content'):
        try:
            with open(_jpg, 'wb') as _f:
                _f.write(_req.content)
            return os.path.abspath(os.path.expanduser(_jpg))
        except Exception as _w:
            if _log:
                _log.error(f'failed to create image, error={_w}')
            return


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
