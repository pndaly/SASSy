#!/usr/bin/env python3


# +
# import(s)
# -
from astropy.time import Time

import argparse
import fastavro
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')


# +
# dunder string(s)
# -
__doc__ = """
    % python3 avro_lightcurve.py --help
"""


# +
# constant(s)
# -
AVRO_FILTERS = {1: 'green', 2: 'red', 3: 'blue'}
AVRO_DATES = ['ago', 'iso', 'jd']


# +
# (hidden) function: _jd_to_iso()
# -
# noinspection PyBroadException
def _jd_to_iso(_jd=0.0):
    try:
        return Time(_jd, format='jd', precision=6).isot
    except Exception:
        return ''


# +
# (hidden) function: _pandify_data()
# -
# noinspection PyBroadException
def _pandify_data(packet=None):
    try:
        if 'candidate' in packet and 'prv_candidates' in packet:
            df_1 = pd.DataFrame(packet['candidate'], index=[0])
            df_2 = pd.DataFrame(packet['prv_candidates'])
            return pd.concat([df_1, df_2], ignore_index=True)
        return None
    except Exception:
        return None


# +
# function: plot_lightcurve()
# -
def plot_lightcurve(_file='', _name='xXx', _data=None, _date_ref=AVRO_DATES[0]):

    # check input(s)
    _file = os.path.abspath(os.path.expanduser(_file.strip()))
    if not isinstance(_file, str) or _file == '' or not os.path.exists(_file):
        return None
    if not isinstance(_name, str) or _name.strip() == '':
        return None
    if _data is None:
        return None
    _date_ref = _date_ref.strip().lower()
    if not isinstance(_date_ref, str) or _date_ref == '' or _date_ref not in AVRO_DATES:
        return None

    # set variable(s)
    _x = ''
    _t = None
    if _date_ref == 'ago':
        _x = 'Days Ago'
        _t = (_data.jd - Time.now().jd)
    elif _date_ref == 'iso':
        _x = 'Date'
        _t = _data.jd
    elif _date_ref == 'jd':
        _x = 'Time (JD)'
        _t = _jd_to_iso(_data.jd)

    # get detections in each filter
    plt.figure()
    for _k, _v in AVRO_FILTERS.items():
        wdet = (_data.fid == _k) & ~_data.magpsf.isnull()
        if np.sum(wdet):
            plt.errorbar(_t[wdet], _data.loc[wdet, 'magpsf'], _data.loc[wdet, 'sigmapsf'], fmt='.', color=_v)
        wnodet = (_data.fid == _k) & _data.magpsf.isnull()
        if np.sum(wnodet):
            plt.scatter(_t[wnodet], _data.loc[wnodet, 'diffmaglim'], marker='v', color=_v, alpha=0.25)

    # show plot(s)
    plt.gca().invert_yaxis()
    plt.title(f'packet {_name}')
    plt.suptitle(f'{_file}')
    plt.xlabel(_x)
    plt.ylabel('Magnitude')
    plt.show()


# +
# function: avro_lightcurve()
# -
# noinspection PyBroadException
def avro_lightcurve(_in='', _out='', _plot=False):

    # check input(s)
    _in = os.path.abspath(os.path.expanduser(_in.strip()))
    _out = os.path.abspath(os.path.expanduser(_out.strip()))
    if not isinstance(_in, str) or _in == '' or not os.path.exists(_in):
        return
    if not isinstance(_out, str) or _out == '':
        return
    _plot = bool(_plot) if isinstance(_plot, bool) else False

    # read the data
    _packets = []
    try:
        with open(_in, 'rb') as _f:
            for _pk in fastavro.reader(_f):
                _packets.append(_pk)
    except Exception as _e:
        return

    # dump lightcurve
    for _i in range(len(_packets)):

        # pandify
        _mda = _pandify_data(_packets[_i])
        _jda = _mda.jd

        # output data
        print(f"#filter,date,magpsf,sigmagpsf,diffmaglim")
        for _k, _v in AVRO_FILTERS.items():
            wdet = (_mda.fid == _k) & ~_mda.magpsf.isnull()
            if np.sum(wdet):
                _filter = f'{AVRO_FILTERS[_k]}'
                print(f'_filter={_filter}')
                _date = _jda[wdet]
                print(f'_date={_date}')
                _magpsf = _mda.loc[wdet, 'magpsf']
                print(f'_magpsf={_magpsf}')
                _sigmagpsf = _mda.loc[wdet, 'sigmapsf']
                print(f'_sigmagpsf={_sigmagpsf}')
            wnodet = (_mda.fid == _k) & _mda.magpsf.isnull()
            if np.sum(wnodet):
                _filter = f'{AVRO_FILTERS[_k]}'
                print(f'_filter={_filter}')
                _date = _jda[wnodet]
                print(f'_date={_date}')
                _diffmaglim = _mda.loc[wnodet, 'diffmaglim']
                print(f'_diffmaglim={_diffmaglim}')

        # plot the data
        if _plot:
            plot_lightcurve(f'{_in}', f"{_packets[_i]['candid']}", _mda)


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s)
    _p = argparse.ArgumentParser(description='Dump AVRO lightcurve', formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('-i', '--input', default='', help="""Input file""")
    _p.add_argument('-o', '--output', default='avro.csv', help="""Output file""")
    _p.add_argument('-p', '--plot', default=False, action='store_true', help='if present, plot data')
    args = _p.parse_args()

    # execute
    avro_lightcurve(args.input, args.output, bool(args.plot))
