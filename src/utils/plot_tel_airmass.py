#!/usr/bin/env python3


# +
# import(s)
# -
from src import *
from src.common import *
from src.utils.utils import *

from astropy import units as u
from astropy.coordinates import AltAz
from astropy.coordinates import EarthLocation
from astropy.coordinates import SkyCoord
from astroplan import FixedTarget
from astroplan import Observer
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
NAUTICAL_DAWN = -12.0
OBS_DEGREE = unicodedata.lookup('DEGREE SIGN')
SOLAR_STYLE = {'linestyle': '--', 'color': 'g'}


# +
# telescope(s)
# -
BOK_ELEVATION = 6795.0 / 3.28083
BOK_LATITUDE = 31.9629
BOK_LONGITUDE = -111.6004
GREENWICH_ELEVATION = 0.0 / 3.28083
GREENWICH_LATITUDE = 51.477754
GREENWICH_LONGITUDE = -0.001138
KUIPER_ELEVATION = 8235.0 / 3.28083
KUIPER_LATITUDE = 32.4165
KUIPER_LONGITUDE = -110.7345
MMT_ELEVATION = 8585.0 / 3.28083
MMT_LATITUDE = 31.6883
MMT_LONGITUDE = -110.8850
STEWARD_ELEVATION = 0.0 / 3.28083
STEWARD_LATITUDE = 32.233184
STEWARD_LONGITUDE = -110.948944
VATT_ELEVATION = 10469.0 / 3.28083
VATT_LATITUDE = 32.7016
VATT_LONGITUDE = -109.8719


# +
# initialize
# -
# noinspection PyBroadException
try:
    import matplotlib as mpl
    mpl.use('Agg')
except Exception:
    pass
import matplotlib.pyplot as plt
import matplotlib.lines as mlines


# +
# function: plot_tel_airmass()
# -
# noinspection PyBroadException,PyUnresolvedReferences
def plot_tel_airmass(_log=None, _ra=math.nan, _dec=math.nan, _oid='', _tel='mmt', _img=''):

    # define observer, observatory, time, frame, sun and moon
    if _tel.lower().strip() == 'bok':
        _observatory = EarthLocation(lat=BOK_LATITUDE*u.deg, lon=BOK_LONGITUDE * u.deg, height=BOK_ELEVATION * u.m)
        _observer = Observer(location=_observatory, name='BOK', timezone='US/Arizona')
    elif _tel.lower().strip() == 'greenwich':
        _observatory = EarthLocation(lat=GREENWICH_LATITUDE*u.deg, lon=GREENWICH_LONGITUDE * u.deg, height=GREENWICH_ELEVATION * u.m)
        _observer = Observer(location=_observatory, name='GREENWICH', timezone='Greenwich')
    elif _tel.lower().strip() == 'kuiper':
        _observatory = EarthLocation(lat=KUIPER_LATITUDE*u.deg, lon=KUIPER_LONGITUDE * u.deg, height=KUIPER_ELEVATION * u.m)
        _observer = Observer(location=_observatory, name='KUIPER', timezone='US/Arizona')
    elif _tel.lower().strip() == 'mmt':
        _observatory = EarthLocation(lat=MMT_LATITUDE*u.deg, lon=MMT_LONGITUDE * u.deg, height=MMT_ELEVATION * u.m)
        _observer = Observer(location=_observatory, name='MMT', timezone='US/Arizona')
    elif _tel.lower().strip() == 'steward':
        _observatory = EarthLocation(lat=STEWARD_LATITUDE*u.deg, lon=STEWARD_LONGITUDE * u.deg, height=STEWARD_ELEVATION * u.m)
        _observer = Observer(location=_observatory, name='STEWARD', timezone='US/Arizona')
    elif _tel.lower().strip() == 'vatt':
        _observatory = EarthLocation(lat=VATT_LATITUDE*u.deg, lon=VATT_LONGITUDE * u.deg, height=VATT_ELEVATION * u.m)
        _observer = Observer(location=_observatory, name='VATT', timezone='US/Arizona')
    else:
        return

    if _log:
        _log.info(f"plot_tel_airmass(_ra={_ra:.3f}, _dec={_dec:.3f}, _oid={_oid}, _tel={_tel}, _img={_img}")

    # get sun, moon etc
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

    # convert
    _oid_s = str(_oid).replace("'", "")
    _ra_hms = ra_to_hms(_ra)
    _dec_dms = dec_to_dms(_dec)
    _dec_dms = f"{_dec_dms}".replace("+", "")
    _sup_title = f"{_oid} Airmass @ {_tel.upper()}"
    _sub_title = f"RA={_ra_hms} ({_ra:.3f}), Dec={_dec_dms} ({_dec:.3f})"

    # get target
    _coords = SkyCoord(ra=_ra*u.deg, dec=_dec*u.deg)
    _target = _coords.transform_to(_frame)
    _target_time = _target.obstime
    _target_alt = _target.alt
    _target_az = _target.az

    # plot data
    _time = str(_target_time[0]).split()[0]
    fig, ax = plt.subplots()
    fig.suptitle(_sup_title.replace("'", "").replace("{", "").replace("}", ""))
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
    ax.set_title(_sub_title)
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
    plt.savefig(_img)
    plt.savefig(_buf, format='png', dpi=100, bbox_inches='tight')
    plt.close()

    # return
    _img = os.path.abspath(os.path.expanduser(_img))
    if os.path.exists(_img):
        if _log:
            _log.debug(f"created {_img}")
        return _img
    else:
        if _log:
            _log.debug(f"created None")
        return


# +
# main()
# -
if __name__ == '__main__':

    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description='Plot Airmass', formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument(f'--image', default='output.png', help="""Output Image""")
    _p.add_argument(f'--dec', default='0.0', help="""Dec (J2k)""")
    _p.add_argument(f'--oid', default='ZTF', help="""Observation ID '%(default)s'""")
    _p.add_argument(f'--ra', default='0.0', help="""RA (J2k)""")
    _p.add_argument(f'--tel', default='mmt', help="""Telescope, defaults to '%(default)s'""")
    _p.add_argument(f'--verbose', default=False, action='store_true', help='if present, produce more verbose output')

    # execute
    args = _p.parse_args()
    plot_tel_airmass(_log=UtilsLogger('PlotAirmass').logger, _ra=float(args.ra), _dec=float(args.dec), _tel=args.tel, _img=args.image)
