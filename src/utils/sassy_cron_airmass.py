#!/usr/bin/env python3


# +
# import(s)
# -
from src import *
from src.common import *
from src.models.sassy_cron import *
from src.utils.utils import *

from astropy import units as u
from astropy.coordinates import AltAz
from astropy.coordinates import EarthLocation
from astropy.coordinates import SkyCoord
from astroplan import FixedTarget
from astroplan import Observer
# from astroplan.plots import plot_airmass
from matplotlib import dates as mdates

import argparse
import io
import numpy as np
import os
import shutil
import unicodedata


# +
# constant(s)
# -
ASTRONOMICAL_DAWN = -18.0
CIVIL_DAWN = -6.0
LUNAR_STYLE = {'linestyle': '--', 'color': 'r'}
MMT_LATITUDE = 31.6883
MMT_LONGITUDE = -110.8850
MMT_ELEVATION = 8585.0 / 3.28083
NAUTICAL_DAWN = -12.0
OBS_DEGREE = unicodedata.lookup('DEGREE SIGN')
SOLAR_STYLE = {'linestyle': '--', 'color': 'g'}


# +
# database(s)
# -
SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PORT = os.getenv('SASSY_DB_PORT', None)


# +
# initialize
# -
# noinspection PyBroadException
random.seed(os.getpid())
try:
    import matplotlib as mpl
    mpl.use('Agg')
except Exception:
    pass
import matplotlib.pyplot as plt
import matplotlib.lines as mlines


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
# function: sassy_cron_airmass()
# -
# noinspection PyBroadException,PyUnresolvedReferences
def sassy_cron_airmass(_log=None, _folder=''):

    # define observer, observatory, time, frame, sun and moon
    _observatory = EarthLocation(lat=MMT_LATITUDE*u.deg, lon=MMT_LONGITUDE * u.deg, height=MMT_ELEVATION * u.m)
    _observer = Observer(location=_observatory, name='MMT', timezone='US/Arizona')

    _now_isot = get_isot(0)
    _now = Time(_now_isot)
    _start_time = Time(_now_isot.replace('T', ' ')) + 1.0*u.day * np.linspace(0.0, 1.0, int(24.0*60.0/5.0))

    _frame = AltAz(obstime=_start_time, location=_observatory)

    _moon = _observer.moon_altaz(_start_time)
    _moon_time = _moon.obstime
    _moon_alt = _moon.alt
    _moon_az = _moon.az

    _sun = _observer.sun_altaz(_start_time)
    _sun_time = _sun.obstime
    _sun_alt = _sun.alt
    _sun_az = _sun.az

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
        _airmass = _base.replace(_replace, 'airmass')
        if _log:
            _log.info(f"_zoid={_zoid}, _zra={_zra}, _zdec={_zdec}, _base={_base}, _replace={_replace}, _airmass={_airmass}")

        # convert
        _ra = ra_to_hms(_zra)
        _dec = dec_to_dms(_zdec)
        _dec = f"{_dec}".replace("+", "")
        _title = f"{_zoid} Airmass @ MMT\nRA={_ra} ({_zra:.3f}), Dec={_dec} ({_zdec:.3f})"

        # get target
        _coords = SkyCoord(ra=_zra*u.deg, dec=_zdec*u.deg)
        _target = _coords.transform_to(_frame)
        _target_time = _target.obstime
        _target_alt = _target.alt
        _target_az = _target.az

        # plot data
        _time = str(_target_time[0]).split()[0]
        fig, ax = plt.subplots()
        _ax_scatter = ax.plot(_moon_time.datetime, _moon_alt.degree, 'g--', label='Moon')
        _ax_scatter = ax.plot(_sun_time.datetime, _sun_alt.degree, 'r--', label='Sun')
        _ax_scatter = ax.scatter(_target_time.datetime, _target_alt.degree,
                                 c=np.array(_target_az.degree), lw=0, s=8, cmap='viridis')
        ax.plot([_now.datetime, _now.datetime], [ASTRONOMICAL_DAWN, 90.0], 'orange')
        ax.plot([_target_time.datetime[0], _target_time.datetime[-1]], [0.0, 0.0], 'black')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gcf().autofmt_xdate()
        plt.colorbar(_ax_scatter, ax=ax).set_label(f'Azimuth ({OBS_DEGREE})')
        ax.set_ylim([ASTRONOMICAL_DAWN, 90.0])
        ax.set_xlim([_target_time.datetime[0], _target_time.datetime[-1]])
        ax.set_title(f'{_title}')
        ax.set_ylabel(f'Altitude ({OBS_DEGREE})')
        ax.set_xlabel(f'{_time} (UTC)')
        plt.legend(loc='upper left')
        plt.fill_between(_target_time.datetime, ASTRONOMICAL_DAWN*u.deg, 90.0*u.deg,
                         _sun_alt < 0.0*u.deg, color='0.80', zorder=0)
        plt.fill_between(_target_time.datetime, ASTRONOMICAL_DAWN*u.deg, 90.0*u.deg,
                         _sun_alt < CIVIL_DAWN*u.deg, color='0.60', zorder=0)
        plt.fill_between(_target_time.datetime, ASTRONOMICAL_DAWN*u.deg, 90.0*u.deg,
                         _sun_alt < NAUTICAL_DAWN*u.deg, color='0.40', zorder=0)
        plt.fill_between(_target_time.datetime, ASTRONOMICAL_DAWN*u.deg, 90.0*u.deg,
                         _sun_alt < ASTRONOMICAL_DAWN*u.deg, color='0.20', zorder=0)

        # save plot
        _buf = io.BytesIO()
        plt.savefig(_airmass)
        plt.savefig(_buf, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        if _log:
            _log.info(f"exit ...  _airmass={_airmass}")
    db_disconnect(_s)


# +
# main()
# -
if __name__ == '__main__':

    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description='SassyCron Airmass', formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument(f'--folder', default='/var/www/SASSy/src/static/img', help="""Image Folder""")
    _p.add_argument(f'--verbose', default=False, action='store_true', help='if present, produce more verbose output')

    # execute
    args = _p.parse_args()
    _log = UtilsLogger('SassyCronAirmass').logger if bool(args.verbose) else None
    sassy_cron_airmass(_log=_log, _folder=args.folder)
