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

        _ra = ra_to_hms(_zra)
        _dec = dec_to_dms(_zdec)
        _dec = f"{_dec}".replace("+", "")
        _finder = _diff.replace('difference', 'finder')
        _sdss_j = _diff.replace('difference', 'sdss').replace('png', 'jpg')
        _sdss_p = None
        if _log:
            _log.info(f"_zoid={_zoid}, _zra={_zra}, _zdec={_zdec}, _diff={_diff}, _sci={_sci}, _tmp={_tmp}")
            _log.info(f"_ra={_ra}, _dec={_dec}, _finder={_finder}, _sdss_j={_sdss_j}, _sdss_p={_sdss_p}")

        # create sdss image
        try:
            _sdss_j = get_sdss_image(**{'ra': _ra, 'dec': _dec, 'jpg': f'{_sdss_j}', 'log': _log})
        except Exception as _e1:
            _sdss_j = None
            if _log:
                    _log.error(f'Failed to get_sdss_image(), error={_e1}')
        if _log:
            _log.info(f"after get_sdss_image()> _finder={_finder}, _sdss_j={_sdss_j}, _sdss_p={_sdss_p}")

        # convert to png
        try:
            if _sdss_j is not None and os.path.exists(_sdss_j):
                _sdss_p = jpg_to_png(_jpg=_sdss_j)
        except Exception as _e2:
            _sdss_p = None
            if _log:
                    _log.error(f'Failed to jpg_to_png(), error={_e2}')
        else:
            if _log:
                _log.info(f"after jpg_to_png()> _finder={_finder}, _sdss_j={_sdss_j}, _sdss_p={_sdss_p}")

        # move file(s)
        #try:
        #    if _sdss_p is not None and os.path.exists(_sdss_p):
        #        os.rename(_sdss_p, f"{_folder}/{os.path.basename(_sdss_p)}")
        #except Exception as _e:
        #    _sdss_j = None
        #    _sdss_p = None
        #    if _log:
        #            _log.error(f'Failed to move image(s), error={_e}')

        if _log:
            _log.info(f"after os.rename()> _finder={_finder}, _sdss_j={_sdss_j}, _sdss_p={_sdss_p}")

        # combine all pngs
        _images = []
        if _sdss_p is not None and os.path.exists(f"{_sdss_p}"):
            _images.append(f"{_sdss_p}")
        if _sci is not None and os.path.exists(f"{_sci}"):
            _images.append(f"{_sci}")
        if _tmp is not None and os.path.exists(f"{_tmp}"):
            _images.append(f"{_tmp}")
        if _diff is not None and os.path.exists(f"{_diff}"):
            _images.append(f"{_diff}")
        if _log:
            _log.info(f'_images={_images}')
        try:
            _finder = combine_pngs(_files=_images, _output=_finder, _log=_log)
            if _finder is not None and os.path.exists(f"{_finder}"):
                _finder = os.rename(_finder, f"{_folder}/{os.path.basename(_finder)}")
        except Exception as _c:
            if _log:
                _log.error(f'Failed to combine image(s), error={_c}')
        else:
            if _log:
                _log.info(f"after combine_pngs()> _finder={_finder}, _sdss_j={_sdss_j}, _sdss_p={_sdss_p}")
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
    _log = UtilsLogger('SassyCronFinder').logger if bool(args.verbose) else None
    sassy_cron_finder(_log=_log, _folder=args.folder)
