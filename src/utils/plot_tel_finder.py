#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# +
# import(s)
# -
from src import *
from src.common import *
from src.utils.combine_pngs import *
from src.utils.get_panstarrs_image import *
from src.utils.get_sdss_image import *
from src.utils.utils import *

import argparse
import os
import shutil


# +
# constant(s)
# -
SASSY_FINDERS = os.getenv('SASSY_FINDERS', '/var/www/SASSy/img/finders')
KEEP_CALM_PNG = f"{SASSY_FINDERS}/KeepCalm.png"
KEEP_CALM_JPG = f"{SASSY_FINDERS}/KeepCalm.jpg"


# +
# function: sassy_cron_finders()
# -
# noinspection PyBroadException,PyUnresolvedReferences
def plot_tel_finder(_log=None, _ra=math.nan, _dec=math.nan, _oid='', _img=''):

    # convert
    _ra_hms = ra_to_hms(_ra)
    _dec_dms = dec_to_dms(_dec)
    _dec_dms = f"{_dec_dms}".replace("+", "")
    if _log:
        _log.info(f"_ra={_ra}, _dec={_dec}, _img={_img}")
        _log.info(f"_ra_hms={_ra_hms}, _dec_dms={_dec_dms}")

    # set default(s)
    _img = os.path.abspath(os.path.expanduser(_img))
    _dir, _file = os.path.dirname(_img), os.path.basename(_img)
    if _log:
        _log.info(f"_img={_img}, _dir={_dir}, _file={_file}")

    # create _[jp]1 image
    _j1 = f"{_dir}/{_file.split('.')[0]}_1.jpg"
    try:
        _j1 = get_sdss_image(**{'ra': _ra_hms, 'dec': _dec_dms, 'jpg': f'{_j1}', 'scale': SDSS_SCALES[1], 'log': _log})
    except Exception as _es1:
        _j1 = None
        if _log:
            _log.error(f'Failed to get_sdss_image(), error={_es1}')
    if _log:
        _log.info(f"_j1={_j1}")

    _p1 = None
    if _j1 is not None and os.path.exists(_j1):
        try:
            _p1 = jpg_to_png(_jpg=_j1)
        except Exception as _ef1:
            _p1 = None
            if _log:
                _log.error(f'Failed to convert jpg_to_png(), error={_ef1}')

    if _p1 is None or not os.path.exists(_p1):
        _p1 = f"{_dir}/{_file.split('.')[0]}_1.png"
        try:
            _p1 = get_panstarrs_image(**{'ra': _ra_hms, 'dec': _dec_dms, 'filters': 'grizy', 'size': 320, 'output_size': 320, 
                                         'color': True, 'log': _log, 'png': _p1})
        except Exception as _ep1:
            _p1 = None
            if _log:
                _log.error(f'Failed to get_panstarrs_image(), error={_ep1}')

    if _p1 is None or not os.path.exists(_p1):
        _p1 = KEEP_CALM_PNG
    if _log:
        _log.info(f"_p1={_p1}")

    # create _[jp]2 image
    _j2 = f"{_dir}/{_file.split('.')[0]}_2.jpg"
    try:
        _j2 = get_sdss_image(**{'ra': _ra_hms, 'dec': _dec_dms, 'jpg': f'{_j2}', 'scale': SDSS_SCALES[0], 'log': _log})
    except Exception as _es2:
        _j2 = None
        if _log:
            _log.error(f'Failed to get_sdss_image(), error={_es2}')
    if _log:
        _log.info(f"_j2={_j2}")

    _p2 = None
    if _j2 is not None and os.path.exists(_j2):
        try:
            _p2 = jpg_to_png(_jpg=_j2)
        except Exception as _ef2:
            _p2 = None
            if _log:
                _log.error(f'Failed to convert jpg_to_png(), error={_ef2}')

    if _p2 is None or not os.path.exists(_p2):
        _p2 = f"{_dir}/{_file.split('.')[0]}_2.png"
        try:
            _p2 = get_panstarrs_image(**{'ra': _ra_hms, 'dec': _dec_dms, 'filters': 'grizy', 'size': 640, 'output_size': 320, 
                                         'color': True, 'log': _log, 'png': _p2})
        except Exception as _ep2:
            _p2 = None
            if _log:
                _log.error(f'Failed to get_panstarrs_image(), error={_ep2}')

    if _p2 is None or not os.path.exists(_p2):
        _p2 = KEEP_CALM_PNG
    if _log:
        _log.info(f"_p2={_p2}")

    # combine pngs
    _images = []
    if 'KeepCalm' in _p1 or 'KeepCalm' in _p2:
        _images.append(f"{_p1}")
    else:
        if _p2 is not None and os.path.exists(f"{_p2}"):
            _images.append(f"{_p2}")
        if _p1 is not None and os.path.exists(f"{_p1}"):
            _images.append(f"{_p1}")
    if _log:
        _log.info(f"_images={_images}")

    if len(_images) == 0:
        _finder = KEEP_CALM_PNG
    if len(_images) == 1:
        _finder = KEEP_CALM_PNG
    else:
        try:
            _finder = combine_pngs(_files=_images, _output=_img, _log=_log)
        except Exception as _eo1:
            _finder = None
            if _log:
                _log.error(f'Failed to combine image(s), error={_eo1}')
        else:
            if _log:
                _log.debug(f'combined image(s), _finder={_finder}')
    if _finder is None or not os.path.exists(f"{_finder}"):
        _finder = KEEP_CALM_PNG

    # return
    _finder = os.path.abspath(os.path.expanduser(_finder))
    if os.path.exists(_finder):
        if _log:
            _log.debug(f"created {_finder}")
        return _finder
    else:
        if _log:
            _log.debug(f"created None")
        return


# +
# main()
# -
if __name__ == '__main__':

    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description='Plot Finder', formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument(f'--image', default='output.png', help="""Output Image""")
    _p.add_argument(f'--dec', default='0.0', help="""Dec (J2k)""")
    _p.add_argument(f'--oid', default='ZTF', help="""Observation ID '%(default)s'""")
    _p.add_argument(f'--ra', default='0.0', help="""RA (J2k)""")
    _p.add_argument(f'--verbose', default=False, action='store_true', help='if present, produce more verbose output')

    # execute
    args = _p.parse_args()
    plot_tel_finder(_log=UtilsLogger('PlotFinder').logger, _ra=float(args.ra), _dec=float(args.dec), _oid=args.oid, _img=args.image)
