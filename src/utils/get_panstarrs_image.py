#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# +
# import(s)
# -
from src import *
from src.utils.utils import *
from astropy.table import Table
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from io import BytesIO

import argparse
import math
import numpy
import os
import pylab
import requests


# +
# constant(s)
# -
PANSTARRS_FILTERS = 'grizy'
PANSTARRS_FILTER = ('g', 'r', 'i', 'z', 'y')
PANSTARRS_FORMATS = ('jpg', 'png')
PANSTARRS_FORMAT = 'png'
PANSTARRS_SIZES = (320, 640)
PANSTARRS_SIZE = 320
PANSTARRS_URL = "https://ps1images.stsci.edu/cgi-bin/ps1filenames.py"
PANSTARRS_FURL = f"https://ps1images.stsci.edu/cgi-bin/fitscut.cgi"

SASSY_TTF = os.getenv('SASSY_TTF')


# +
# function: get_panstarrs_url()
# -
# noinspection PyBroadException
def get_panstarrs_url(_ra=math.nan, _dec=math.nan, _size=PANSTARRS_SIZE, _output_size=PANSTARRS_SIZE, 
                      _filters=PANSTARRS_FILTERS, _format=PANSTARRS_FORMAT, _color=True, _log=None):

    # entry
    if _log:
        _log.debug(f"entry ... _ra={_ra:.4f}, _dec={_dec:.4f}, _size={_size}, _output_size={_output_size}, _filters={_filters}, _format={_format}, _color={_color}")

    # get table(s)
    _table, _url = None, None
    try:
        _table = Table.read(f"{PANSTARRS_URL}?ra={_ra:.4f}&dec={_dec:.4f}&size={_size}&format=fits&filters={_filters}", format='ascii')
    except:
        _table = None
    if _log:
        _log.debug(f"_table={_table}")
    if _table is None:
        return

    # sort by filter
    _url = f"{PANSTARRS_FURL}?ra={_ra:.4f}&dec={_dec:.4f}&size={_size}&format={_format}&output_size={_output_size}"
    _flist = [PANSTARRS_FILTERS[::-1].find(_x) for _x in _table['filter']]
    if _log:
        _log.debug(f"_url={_url}, _flist={_flist}")
    if len(_flist) == 0:
        return

    # calculate url
    _table = _table[numpy.argsort(_flist)]
    if _log:
        _log.debug(f"_table={_table}")
    if not _color:
        _urlbase = _url + "&red="
        _url = []
        for _fn in _table['filename']:
            _url.append(_urlbase + _fn)
    else:
        if len(_table) > 3:
            _f1 = list(PANSTARRS_FILTER)
            _f1s = random.choice(_f1)
            _f1i = PANSTARRS_FILTER.index(_f1s)
            _f1.pop(_f1.index(_f1s))
            _f2s = random.choice(_f1)
            _f2i = PANSTARRS_FILTER.index(_f2s)
            _f1.pop(_f1.index(_f2s))
            _f3s = random.choice(_f1)
            _f3i = PANSTARRS_FILTER.index(_f3s)
            _f1.pop(_f1.index(_f3s))
            if _log:
                _log.debug(f"Random filters: {_f1s} ({_f1i}), {_f2s} ({_f2i}), {_f3s} ({_f3i})")
            _table = _table[[_f1i, _f2i, _f3i]]
            if _log:
                _log.debug(f">>>> _table={_table}")
        for _i, _p in enumerate(['red', 'green', 'blue']):
            if _log:
                _log.debug(f">>>> _i={_i}, _p={_p}, _table['filename']={_table['filename']}")
            try:
                _url = _url + "&{}={}".format(_p, _table['filename'][_i])
            except:
                pass

    # exit
    if _log:
        _log.debug(f"exit ... _url={_url}")
    return _url


# +
# function: get_panstarrs_object()
# -
# noinspection PyBroadException
def get_panstarrs_object(url='', _log=None):

    if _log:
        _log.debug(f"entry ... url={url}")

    # request data
    _req = None
    try:
        _req = requests.get(url=f'{url}')
    except Exception as _e:
        raise Exception(f"failed to complete request, _req={_req}, error={_e}")

    # if everything is ok, create the png image and return the path
    if _req is not None and hasattr(_req, 'status_code') and (_req.status_code == 200) and hasattr(_req, 'content'):
        try:
            return Image.open(BytesIO(_req.content))
        except Exception as _w:
            if _log:
                _log.error(f'failed to create object, error={_w}')


# +
# function: get_panstarrs_image()
# -
# noinspection PyBroadException
def get_panstarrs_image(**kw):

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

    # set default(s)
    _ra_dec = ra_to_decimal(_ra)
    _ra_str = _ra.replace('.', '').replace(':', '').replace(' ', '').strip()[:6]
    _dec_dec = dec_to_decimal(_dec)
    _dec_str = _dec.replace('.', '').replace(':', '').replace(' ', '').replace('-', '').replace('+', '').strip()[:6]
    _color = kw['color'] if ('color' in kw and isinstance(kw['color'], bool)) else True
    _filters = kw['filters'] if \
        ('filters' in kw and isinstance(kw['filters'], str) and kw['filters'].lower() in PANSTARRS_FILTERS) else PANSTARRS_FORMAT
    _format = kw['format'] if \
        ('format' in kw and isinstance(kw['format'], str) and kw['format'].lower() in PANSTARRS_FORMATS) else PANSTARRS_FORMAT
    _size = kw['size'] if \
        ('size' in kw and isinstance(kw['size'], int) and kw['size'] in PANSTARRS_SIZES) else PANSTARRS_SIZE
    _output_size = kw['output_size'] if \
        ('output_size' in kw and isinstance(kw['output_size'], int) and kw['output_size'] in PANSTARRS_SIZES) else PANSTARRS_SIZE
    _png = kw['png'] if ('png' in kw and isinstance(kw['png'], str) and kw['png'].strip() != '') else \
        f'panstarrs_{_ra_str}_{_dec_str}.png'

    if _log:
        _log.debug(f"_ra={_ra}, _ra_dec={_ra_dec:.4f}, _ra_str={_ra_str}, _dec={_dec}, _dec_dec={_dec_dec:.4f}, _dec_str={_dec_str}")
        _log.debug(f"_color={_color}, _filters={_filters}, _format={_format}, _size={_size}")
        _log.debug(f"_output_size={_output_size}, _png={_png}")

    # get url
    _req, _url = None, None
    try:
        _url = get_panstarrs_url(_ra=_ra_dec, _dec=_dec_dec, _size=_size, _filters=_filters, 
                                 _output_size=_output_size, _format=_format, _color=_color, _log=_log)
        if _log:
            _log.debug(f"_url={_url}")
    except Exception as _u:
        raise Exception(f"failed to create url={_url}, error={_u}")
    if _log:
        _log.debug(f"_req={_req}, _url={_url}")

    # get image object
    _imobj = None
    if _color:
        _imobj = get_panstarrs_object(url=_url, _log=_log)
    else:
        _imobj = get_panstarrs_object(url=_url[0], _log=_log)

    if _imobj is None:
        return

    _draw  = ImageDraw.Draw(_imobj)
    _scale = 0.25
    _font  = ImageFont.truetype(f'{SASSY_TTF}/Arial.ttf', 12)
    # title
    _draw.text((20,20), 'PanSTARRS DR2', fill='white', font=_font)
    _draw.text((20,35), f'ra: {ra_to_decimal(_ra):.3f} dec: {dec_to_decimal(_dec):.3f}', fill='white', font=_font)
    _draw.text((20,50), f'scale: {_scale} arcsec/pix', fill='white', font=_font)
    _draw.line(((20,80), (60,80)), width=2, fill='yellow')
    # border(s)
    for _i in [40, 80, 120, 160, 200, 240, 280]:
        _draw.line(((0, _i), (10, _i)), width=1, fill='white')
        _draw.line(((310, _i), (320, _i)), width=1, fill='white')
        _draw.line(((_i, 0), (_i, 10)), width=1, fill='white')
        _draw.line(((_i, 310), (_i, 320)), width=1, fill='white')
    # cardinal points
    for _k, _v in {'E': (20,155), 'W': (295,155), 'N': (155,20), 'S': (155,295)}.items(): 
        _draw.text(_v, _k, fill='white', font=_font)
    for _i in [((35,160), (145,160)), ((175,160), (285,160)), ((160,35), (160,145)), ((160,175), (160,285))]:
        _draw.line((_i[0], _i[1]), width=1, fill='white')
        _draw.line((_i[0], _i[1]), width=1, fill='white')
        _draw.line((_i[0], _i[1]), width=1, fill='white')
        _draw.line((_i[0], _i[1]), width=1, fill='white')
    if _size == PANSTARRS_SIZES[0]:
        # title
        _draw.text((20,65), f'10"             FoV: 80"', fill='white', font=_font)

    elif _size == PANSTARRS_SIZES[1]:
        # title
        _draw.text((20,65), f'20"             FoV: 160"', fill='white', font=_font)

    # save
    _imobj.save(_png)

    # return
    return os.path.abspath(os.path.expanduser(_png))


# +
# main()
# -
if __name__ == '__main__':

    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description='Get PanStarrs Image', formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('--ra', default='', help="""Right Ascension (decimal or hh:mm:ss.s)""")
    _p.add_argument('--dec', default='', help="""Declination (decimal or +/-dd:mm:ss.s)""")
    _p.add_argument('--filters', default=PANSTARRS_FILTERS, help="""Filter '%(default)s'""")
    _p.add_argument('--size', default=PANSTARRS_SIZE, help=f"""Size {PANSTARRS_SIZES}""")
    _p.add_argument(f'--color', default=False, action='store_true', help='if present, produce color image')
    _p.add_argument(f'--verbose', default=False, action='store_true', help='if present, produce more verbose output')
    args = _p.parse_args()

    # initialize
    _l = UtilsLogger('GetPanStarrsImage').logger if bool(args.verbose) else None

    # convert RA, Dec
    if ':' in args.ra and ':' in args.dec:
        _ra = args.ra
        _dec = args.dec
    else:
        _ra = ra_to_hms(args.ra)
        _dec = dec_to_dms(args.dec)

    # execute
    _png = get_panstarrs_image(**{'ra': _ra, 'dec': _dec, 'filters': args.filters, 'size': int(args.size), 'output_size': PANSTARRS_SIZE, 'color': bool(args.color), 'log': _l})
    _l.info(f"_png={_png}")
