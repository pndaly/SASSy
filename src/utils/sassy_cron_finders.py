#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# +
# import(s)
# -
from src import *
from src.common import *
from src.models.sassy_cron import *
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
SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PORT = os.getenv('SASSY_DB_PORT', None)


# +
# function: db_connect()
# -
# noinspection PyBroadException
def db_connect():
    try:
        engine = create_engine(
            f'postgresql+psycopg2://{SASSY_DB_USER}:{SASSY_DB_PASS}@{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}')
        get_session = sessionmaker(bind=engine)
        return get_session()
    except Exception:
        return None


# +
# function: db_disconnect()
# -
# noinspection PyBroadException
def db_disconnect(_session=None):
    try:
        _session.close()
        _session.close_all_sessions()
    except Exception:
        pass


# +
# function: sassy_cron_finders()
# -
# noinspection PyBroadException,PyUnresolvedReferences
def sassy_cron_finders(_log=None, _folder=''):

    # get record(s)
    _s = db_connect()
    _query = _s.query(SassyCron)
    for _q in _query.all():

        # get data
        _zoid, _zra, _zdec = _q.zoid, _q.zra, _q.zdec
        _base = f"{_folder}/{_q.dpng}"
        _replace = 'difference'
        if _base == '':
            _base = f"{_folder}/{_q.spng}"
            _replace = 'science'
        if _base == '':
            _base = f"{_folder}/{_q.tpng}"
            _replace = 'template'
        if _base == '':
            return
        if _log:
            _log.info(f"_zoid={_zoid}, _zra={_zra}, _zdec={_zdec}, _base={_base}, _replace={_replace}")

        # convert
        _ra = ra_to_hms(_zra)
        _dec = dec_to_dms(_zdec)
        _dec = f"{_dec}".replace("+", "")
        if _log:
            _log.info(f"_ra={_ra}, _dec={_dec}")

        # create _[jp]1 image
        _j1 = _base.replace(_replace, 'jpg_1').replace('png', 'jpg')
        _p1 = None
        try:
            _j1 = get_sdss_image(**{'ra': _ra, 'dec': _dec, 'jpg': f'{_j1}', 'scale': SDSS_SCALES[1], 'log': _log})
        except Exception as _es1:
            _j1 = None
            if _log:
                _log.error(f'Failed to get_sdss_image(), error={_es1}')
        if _log:
            _log.info(f"_j1={_j1}")
        if _j1 is not None and os.path.exists(_j1):
            try:
                _p1 = jpg_to_png(_jpg=_j1)
            except Exception as _ef1:
                _p1 = None
                if _log:
                    _log.error(f'Failed to convert jpg_to_png(), error={_ef1}')
        if _p1 is None or not os.path.exists(_p1):
            _p1 = _base.replace(_replace, 'png_1')
            #try:
            _p1 = get_panstarrs_image(**{'ra': _ra, 'dec': _dec, 'filters': 'grizy', 'size': 320, 'output_size': 320, 
                                         'color': True, 'log': _log, 'png': _p1})
            #except Exception as _ep1:
            #    _p1 = f"{_folder}/KeepCalm.png"
            #    if _log:
            #        _log.error(f'Failed to get_panstarrs_image(), error={_ep1}')
        if _p1 is None or not os.path.exists(_p1):
            _p1 = f"{_folder}/KeepCalm.png"
        if _log:
            _log.info(f"_p1={_p1}")

        # create _[jp]2 image
        _j2 = _base.replace(_replace, 'jpg_2').replace('png', 'jpg')
        _p2 = None
        try:
            _j2 = get_sdss_image(**{'ra': _ra, 'dec': _dec, 'jpg': f'{_j2}', 'scale': SDSS_SCALES[0], 'log': _log})
        except Exception as _es2:
            _j2 = None
            if _log:
                _log.error(f'Failed to get_sdss_image(), error={_es2}')
        if _log:
            _log.info(f"_j2={_j2}")
        if _j2 is not None and os.path.exists(_j2):
            try:
                _p2 = jpg_to_png(_jpg=_j2)
            except Exception as _ef2:
                _p2 = None
                if _log:
                    _log.error(f'Failed to convert jpg_to_png(), error={_ef2}')
        if _p2 is None or not os.path.exists(_p2):
            _p2 = _base.replace(_replace, 'png_2')
            try:
                _p2 = get_panstarrs_image(**{'ra': _ra, 'dec': _dec, 'filters': 'grizy', 'size': 640, 'output_size': 320, 
                                             'color': True, 'log': _log, 'png': _p2})
            except Exception as _ep2:
                _p2 = f"{_folder}/KeepCalm.png"
                if _log:
                    _log.error(f'Failed to get_panstarrs_image(), error={_ep2}')
        if _p2 is None or not os.path.exists(_p2):
            _p2 = f"{_folder}/KeepCalm.png"
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
        _finder = _base.replace(_replace, 'finder')
        if _log:
            _log.debug(f"creating, _finder)={_finder}")
        if len(_images) < 2:
            if _log:
                _log.debug(f"too few images, len(_images)={len(_images)}")
            _finder = shutil.copy(f"{_folder}/KeepCalm.png", f"{_folder}/{os.path.basename(_finder)}")
        else:
            try:
                _finder = combine_pngs(_files=_images, _output=_finder, _log=_log)
            except Exception as _eo1:
                if _log:
                    _log.error(f'Failed to combine image(s), error={_eo1}')
            else:
                if _log:
                    _log.debug(f'combined image(s), _finder={_finder}')
            if _finder is None or not os.path.exists(f"{_finder}"):
                _finder = _base.replace(_replace, 'finder')
                _finder = shutil.copy(f"{_folder}/KeepCalm.png", f"{_folder}/{os.path.basename(_finder)}")
        if _log:
            _log.info(f"exit ...  _finder={_finder}")
    db_disconnect(_s)


# +
# main()
# -
if __name__ == '__main__':

    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description='SassyCron Finder', formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument(f'--folder', default='/var/www/SASSy/src/static/img', help="""Image Folder""")
    _p.add_argument(f'--verbose', default=False, action='store_true', help='if present, produce more verbose output')

    # execute
    args = _p.parse_args()
    _log = UtilsLogger('SassyCronFinders').logger if bool(args.verbose) else None
    sassy_cron_finders(_log=_log, _folder=args.folder)
