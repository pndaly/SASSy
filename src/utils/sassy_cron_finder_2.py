#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# +
# import(s)
# -
from src import *
from src.common import *
from src.models.sassy_cron import *
from src.utils.combine_pngs import *
from src.utils.utils import UtilsLogger

import argparse
import os

try:
    import matplotlib as mpl
    mpl.use('Agg')
except Exception:
    pass
import matplotlib.pyplot as plt
import matplotlib.lines as mlines


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
# function: sassy_cron_sdss()
# -
# noinspection PyBroadException,PyUnresolvedReferences
def sassy_cron_sdss(_log=None, _folder=''):

    # get record(s)
    _s = db_connect()
    _query = _s.query(SassyCron)
    for _q in _query.all():

        # get data
        _zoid, _zra, _zdec = _q.zoid, _q.zra, _q.zdec
        _diff, _sci, _tmp = f"{_folder}/{_q.dpng}", f"{_folder}/{_q.spng}", f"{_folder}/{_q.tpng}"
        if _log:
            _log.info(f"_zoid={_zoid}, _zra={_zra}, _zdec={_zdec}, _diff={_diff}, _sci={_sci}, _tmp={_tmp}")

        # convert
        _ra = ra_to_hms(_zra)
        _dec = dec_to_dms(_zdec)
        _dec = f"{_dec}".replace("+", "")
        _sdss = _diff.replace('difference', 'sdss')
        _sdss_j1 = _diff.replace('difference', 'sdss_1').replace('png', 'jpg')
        _sdss_j2 = _diff.replace('difference', 'sdss_2').replace('png', 'jpg')
        _sdss_p1 = None
        _sdss_p2 = None
        if _log:
            _log.info(f"_ra={_ra}, _dec={_dec}, _sdss={_sdss}, _sdss_j1={_sdss_j1}, _sdss_j2={_sdss_j2}, _sdss_p1={_sdss_p1}, _sdss_p2={_sdss_p2}")

        # create _sdss_j1 image
        try:
            _sdss_j1 = get_sdss_image(**{'ra': _ra, 'dec': _dec, 'jpg': f'{_sdss_j1}', 'scale': SDSS_SCALES[1], 'log': _log})
        except Exception as _e1:
            _sdss_j1 = None
            if _log:
                _log.error(f'Failed to get_sdss_image(), error={_e1}')
        if _log:
            _log.info(f"after get_sdss_image(1)> _sdss={_sdss}, _sdss_j1={_sdss_j1}, _sdss_j2={_sdss_j2}, _sdss_p1={_sdss_p1}, _sdss_p2={_sdss_p2}")

        # create _sdss_j2 image
        try:
            _sdss_j2 = get_sdss_image(**{'ra': _ra, 'dec': _dec, 'jpg': f'{_sdss_j2}', 'scale': SDSS_SCALES[0], 'log': _log})
        except Exception as _e2:
            _sdss_j2 = None
            if _log:
                _log.error(f'Failed to get_sdss_image(), error={_e2}')
        if _log:
            _log.info(f"after get_sdss_image(2)> _sdss={_sdss}, _sdss_j1={_sdss_j1}, _sdss_j2={_sdss_j2}, _sdss_p1={_sdss_p1}, _sdss_p2={_sdss_p2}")

        # create _sdss_p1 image
        try:
            if _sdss_j1 is not None and os.path.exists(_sdss_j1):
                _sdss_p1 = jpg_to_png(_jpg=_sdss_j1)
        except Exception as _e3:
            _sdss_p1 = f"{_folder}/KeepCalm.png"
            if _log:
                _log.error(f'Failed to jpg_to_png(), error={_e3}')
        if _log:
            _log.info(f"after jpg_to_png(1)> _sdss={_sdss}, _sdss_j1={_sdss_j1}, _sdss_j2={_sdss_j2}, _sdss_p1={_sdss_p1}, _sdss_p2={_sdss_p2}")

        # create _sdss_p2 image
        try:
            if _sdss_j2 is not None and os.path.exists(_sdss_j2):
                _sdss_p2 = jpg_to_png(_jpg=_sdss_j2)
        except Exception as _e4:
            _sdss_p1 = f"{_folder}/KeepCalm.png"
            if _log:
                _log.error(f'Failed to jpg_to_png(), error={_e4}')
        if _log:
            _log.info(f"after jpg_to_png(2)> _sdss={_sdss}, _sdss_j1={_sdss_j1}, _sdss_j2={_sdss_j2}, _sdss_p1={_sdss_p1}, _sdss_p2={_sdss_p2}")

        # combine sdss pngs
        _images = []
        if _sdss_p2 is not None and os.path.exists(f"{_sdss_p2}"):
            _images.append(f"{_sdss_p2}")
        if _sdss_p1 is not None and os.path.exists(f"{_sdss_p1}"):
            _images.append(f"{_sdss_p1}")
        try:
            _sdss = combine_pngs(_files=_images, _output=_sdss, _log=_log)
            if _sdss is not None and os.path.exists(f"{_sdss}"):
                _sdss = os.rename(_sdss, f"{_folder}/{os.path.basename(_sdss)}")
            else:
                _sdss = f"{_folder}/KeepCalm.png"
        except Exception as _e5:
            _sdss = f"{_folder}/KeepCalm.png"
            if _log:
                _log.error(f'Failed to combine image(s), error={_e5}')
        if _log:
            _log.info(f"after combine_pngs()> _sdss={_sdss}, _sdss_j1={_sdss_j1}, _sdss_p1={_sdss_p1}, _sdss_j2={_sdss_j2}, _sdss_p2={_sdss_p2}")
    db_disconnect(_s)


# +
# function: sassy_cron_finder()
# -
# noinspection PyBroadException,PyUnresolvedReferences
def sassy_cron_finder(_log=None, _folder=''):

    # get record(s)
    _s = db_connect()
    _query = _s.query(SassyCron)
    for _q in _query.all():

        # get data
        _zoid, _zra, _zdec = _q.zoid, _q.zra, _q.zdec
        _diff, _sci, _tmp = f"{_folder}/{_q.dpng}", f"{_folder}/{_q.spng}", f"{_folder}/{_q.tpng}"
        if _log:
            _log.info(f"_zoid={_zoid}, _zra={_zra}, _zdec={_zdec}, _diff={_diff}, _sci={_sci}, _tmp={_tmp}")

        # convert
        _ra = ra_to_hms(_zra)
        _dec = dec_to_dms(_zdec)
        _dec = f"{_dec}".replace("+", "")
        _finder = _diff.replace('difference', 'finder')
        _sdss = _diff.replace('difference', 'sdss')
        if _log:
            _log.info(f"_ra={_ra}, _dec={_dec}, _finder={_finder}, _sdss={_sdss}")

        # combine all pngs
        _images = []
        if _sdss is not None and os.path.exists(f"{_sdss}"):
            _images.append(f"{_sdss}")
        if _sci is not None and os.path.exists(f"{_sci}"):
            _images.append(f"{_sci}")
        if _tmp is not None and os.path.exists(f"{_tmp}"):
            _images.append(f"{_tmp}")
        if _diff is not None and os.path.exists(f"{_diff}"):
            _images.append(f"{_diff}")
        try:
            _finder = combine_pngs(_files=_images, _output=_finder, _log=_log)
            if _finder is not None and os.path.exists(f"{_finder}"):
                _finder = os.rename(_finder, f"{_folder}/{os.path.basename(_finder)}")
        except Exception as _e1:
            if _log:
                _log.error(f'Failed to combine image(s), error={_e1}')
        else:
            if _log:
                _log.info(f"after combine_pngs()> _finder={_finder}, _sdss={_sdss}")
    db_disconnect(_s)


# +
# function: sassy_cron_images()
# -
# noinspection PyBroadException,PyUnresolvedReferences
def sassy_cron_images(_log=None, _folder=''):
    sassy_cron_sdss(_log=_log, _folder=_folder)
    sassy_cron_finder(_log=_log, _folder=_folder)


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
    _log = UtilsLogger('SassyCronFinder').logger if bool(args.verbose) else None
    sassy_cron_images(_log=_log, _folder=args.folder)
