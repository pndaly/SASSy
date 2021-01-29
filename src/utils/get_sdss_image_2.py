#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# +
# import(s)
# -
from src import *
from PIL import Image
from src.utils.utils import *

import argparse
import os
import requests


# +
# constant(s)
# -
SDSS_HEIGHT = 400
SDSS_SCALE = 0.79224/2.0
SDSS_SCALES = (0.5*SDSS_SCALE, 1.0*SDSS_SCALE, 1.5*SDSS_SCALE, 2.0*SDSS_SCALE, 2.5*SDSS_SCALE, 3.0*SDSS_SCALE, 3.5*SDSS_SCALE, 4.0*SDSS_SCALE)
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
    if _log:
        _log.debug(f'entry ... kw={kw}')

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
            if _log:
                _log.debug(f"exit ...  {os.path.abspath(os.path.expanduser(_jpg))}")
            return os.path.abspath(os.path.expanduser(_jpg))
        except Exception as _w:
            if _log:
                _log.error(f'failed to create image, error={_w}')
                _log.debug(f"exit ...  {os.path.abspath(os.path.expanduser(_jpg))}")
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
# main()
# -
if __name__ == '__main__':

    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description='Get SDSS Image', formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('--ra', default='', help="""Right Ascension (hh:mm:ss.s)""")
    _p.add_argument('--dec', default='', help="""Declination (+/-dd:mm:ss.s)""")
    _p.add_argument(f'--png', default=False, action='store_true', help='if present, return PNG image')
    _p.add_argument(f'--verbose', default=False, action='store_true', help='if present, produce more verbose output')
    args = _p.parse_args()

    # initialize
    _l = UtilsLogger('GetSDSSImage').logger if bool(args.verbose) else None

    # convert RA, Dec
    if ':' in args.ra and ':' in args.dec:
        _ra = args.ra
        _dec = args.dec
    else:
        _ra = ra_to_hms(args.ra)
        _dec = dec_to_dms(args.dec)

    # execute
    _l.info("Calling get_sdss_image(**{" + f"'ra': {_ra}, 'dec': {_dec}"+"})")
    _jpg = get_sdss_image(**{'ra': _ra, 'dec': _dec, 'log': _l})
    _l.info("Called  get_sdss_image(**{" + f"'ra': {_ra}, 'dec': {_dec}"+"})")
    _l.info(f"_jpg={_jpg}")
    if bool(args.png) and _jpg is not None:
        _png = jpg_to_png(_jpg=_jpg)
        _l.info(f"_png={_png}")

