#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# +
# import(s)
# -
from src.common import *
from src.models.sassy_cron import *
from src.utils.Alerce import Alerce
from src.utils.utils import UtilsLogger

import argparse
import matplotlib.pyplot as plt
import numpy as np
import os


# +
# constant(s)
# -
CLASSIFIERS = Alerce().alerce_early_classifier + ['None']
MARKERS = ['o', '*', 'd', 's', '+', 'x']
ORIGIN = 180.0
PROPORTIONAL = '\u221D'
DEGREE = '\u00B0'
UPPER_H = '\u02B0'
SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PORT = os.getenv('SASSY_DB_PORT', None)
TEST_DATA = [[0.0, 30.0, 100.0], [60.0, -45.0, 100.0], [240.0, 15.0, 100.0], [150.0, -75.0, 100.0],
             [90.0, 52.5, 100.0], [315.0, -37.5, 100.0], [180.0, 45.0, 100.0], [270.0, -60.0, 100.0]]


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
# function: munge_data()
# -
# noinspection PyBroadException
def munge_data(_indata=None, _origin=ORIGIN):
    """ extract [[ra1, dec1, p1], [ra2, dec2, p2], [ra3, dec3, p3] ... [ran, decn, pn]]"""
    try:
        # extract [RA, Dec, probability] data from sub-lists
        ra, dec, prob = zip(*_indata)
        # convert to numpy arrays
        ra, dec, prob = np.array(ra), np.array(dec), np.array(prob)
        # coerce RA into range -180.0 to +180.0 for given origin
        ra = np.remainder(ra + 360.0 - _origin, 360.0)
        ind = ra > 180.0
        ra[ind] -= 360.0
        # reverse RA so it increases to the left / east
        ra = -ra
        # return data
        return ra, dec, prob
    except:
        return None, None, None


# +
# function: sassy_cron_mollweide()
# -
# noinspection PyBroadException,PyUnresolvedReferences
def sassy_cron_mollweide(_log=None, _png='', _show=False, _test=False):

    # set default(s)
    _data = [None, {**{_k: [] for _k in CLASSIFIERS}}, {**{_k: [] for _k in CLASSIFIERS}},
             {**{_k: [] for _k in CLASSIFIERS}}]
    _glade = []
    _total = 0

    # get Ra, Dec, probability
    _s = db_connect()
    _query = _s.query(SassyCron)
    for _q in _query.all():
        _glade.append([_q.gra, _q.gdec, 100.0/_q.gdist])
        _data[_q.zfid].get(_q.aetype.strip(), _data[_q.zfid]['None']).append(
            [_q.zra, _q.zdec, 50.0*_q.aeprob if (0.0 <= _q.aeprob <= 1.0) else 25.0])
    db_disconnect(_s)

    # set up plot
    fig = plt.figure(figsize=(10, 8))
    fig.set_tight_layout(True)
    ax = fig.add_subplot(111, projection="mollweide", **{'facecolor': 'LightCyan'})

    # plot test data
    if _test:
        try:
            x, y, z = munge_data(TEST_DATA)
            ax.scatter(np.radians(x), np.radians(y), color='black', s=z, marker='1', label="Test")
        except:
            pass

    # plot glade
    try:
        x, y, z = munge_data(_glade)
        ax.scatter(np.radians(x), np.radians(y), color='black', s=z, alpha=0.25, marker='.', label="Glade")
    except:
        pass

    # plot zfid=1
    try:
        for _i, _v in enumerate(CLASSIFIERS):
            x, y, z = munge_data(_data[1][_v])
            ax.scatter(np.radians(x), np.radians(y), color='green', s=z, alpha=0.25, marker=MARKERS[_i], label=f"{_v}")
            _total += len(x)
    except:
        pass

    # plot zfid=2
    try:
        for _i, _v in enumerate(CLASSIFIERS):
            x, y, z = munge_data(_data[2][_v])
            ax.scatter(np.radians(x), np.radians(y), color='red', s=z, alpha=0.25, marker=MARKERS[_i])
            _total += len(x)
    except:
        pass

    # plot zfid=3
    try:
        for _i, _v in enumerate(CLASSIFIERS):
            x, y, z = munge_data(_data[3][_v])
            ax.scatter(np.radians(x), np.radians(y), color='orange', s=z, alpha=0.25, marker=MARKERS[_i])
            _total += len(x)
    except:
        pass

    # add label(s), legend, title, grid
    tick_labels = np.array([150, 120, 90, 60, 30, 0, 330, 300, 270, 240, 210])
    tick_labels = np.remainder(tick_labels + 360.0 + ORIGIN, 360.0)
    tick_labels = [f'{int(_v/15.0):d}{UPPER_H} \n\n {int(_v):d}{DEGREE}' for _v in tick_labels]
    ax.set_xticklabels(tick_labels, **{'va': 'center'})
    ax.set_xlabel(f'Right Ascension\nMarker symbols apply for all classifiers in all filters')
    ax.set_ylabel(f'Declination')
    ax.grid(True)
    plt.legend(loc='lower center')
    plt.title(f"{_total} SassyCron Target(s), {len(_glade)} Glade Galaxies\n"
              f"(Marker Area {PROPORTIONAL} Classifier Probability, except for 'None')")

    # output(s)
    if _png.strip() != '':
        plt.savefig(fname=_png, format='png', dpi=100, bbox_inches='tight')

    if _show:
        plt.show()


# +
# main()
# -
if __name__ == '__main__':

    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description='Plot SassyCron Mollweide', formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('--png', default='', help="""Output png file""")
    _p.add_argument(f'--show', default=False, action='store_true', help='if present, show plot')
    _p.add_argument(f'--test', default=False, action='store_true', help='if present, show test data')
    _p.add_argument(f'--verbose', default=False, action='store_true', help='if present, produce more verbose output')

    # execute
    args = _p.parse_args()
    _log = UtilsLogger('SassyCronMollweide').logger if bool(args.verbose) else None
    sassy_cron_mollweide(_log=_log, _png=args.png, _show=bool(args.show), _test=bool(args.test))
