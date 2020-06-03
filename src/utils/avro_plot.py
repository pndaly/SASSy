#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# +
# import(s)
# -
from astropy.io import fits

import argparse
import base64
import fastavro
import gzip
import io
import os
import random


# +
# initialize
# -
# noinspection PyBroadException
try:
    import matplotlib as mpl
    mpl.use('Agg')
except Exception:
    pass
import matplotlib.cm as cm
import matplotlib.pyplot as plt
random.seed(os.getpid())


# +
# constant(s)
# -
COLOUR_MAPS = [_map for _map in cm.datad]


# +
# (hidden) function: _get_fits_data()
# -
def _get_fits_data(_s=None):
    try:
        with gzip.open(io.BytesIO(_s), 'rb') as _f:
            with fits.open(io.BytesIO(_f.read())) as _hdu:
                return _hdu[0].data
    except Exception:
        raise None


# +
# function: avro_plot()
# -
# noinspection PyBroadException
def avro_plot(_file='', _www=False):

    # check input(s)
    _file = os.path.abspath(os.path.expanduser(_file.strip()))
    if not isinstance(_file, str) or _file == '' or not os.path.exists(_file):
        return
    _www = bool(_www) if isinstance(_www, bool) else False

    # set default(s)
    _packets = []
    _png_data = []
    _dif, _sci, _tem = None, None, None

    # read the packets
    try:
        with open(_file, 'rb') as _f:
            for _pk in fastavro.reader(_f):
                _packets.append(_pk)
    except Exception as _e:
        return

    # plot data
    for _i in range(len(_packets)):

        # get data
        try:
            _sci = _get_fits_data(_packets[_i][f'cutoutScience']['stampData'])
            _tem = _get_fits_data(_packets[_i][f'cutoutTemplate']['stampData'])
            _dif = _get_fits_data(_packets[_i][f'cutoutDifference']['stampData'])
        except Exception:
            return

        # plot it
        try:
            _fig = plt.figure()
            if _sci is not None:
                _fig.add_subplot(1, 3, 1)
                if 'coolwarm' in COLOUR_MAPS:
                    _col = 'coolwarm'
                else:
                    _col = random.choice(COLOUR_MAPS)
                plt.imshow(_sci, cmap=_col, origin='lower')
                # plt.title(f'color map: {_col}')
                plt.title(f'Science')
            if _tem is not None:
                _fig.add_subplot(1, 3, 2)
                if 'coolwarm_r' in COLOUR_MAPS:
                    _col = 'coolwarm_r'
                else:
                    _col = random.choice(COLOUR_MAPS)
                plt.imshow(_tem, cmap=_col, origin='lower')
                # plt.title(f'color map: {_col}')
                plt.title(f'Template')
            if _dif is not None:
                _fig.add_subplot(1, 3, 3)
                if 'Spectral' in COLOUR_MAPS:
                    _col = 'Spectral'
                else:
                    _col = random.choice(COLOUR_MAPS)
                plt.imshow(_dif, cmap=_col, origin='lower')
                # plt.title(f'color map: {_col}')
                plt.title(f'Difference')
            if not _www:
                plt.suptitle(f'{_file}')
                plt.show(block=True)
            else:
                _buf = io.BytesIO()
                plt.savefig(_buf, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                _png_data.append(f'data:image/png;base64,{base64.b64encode(_buf.getvalue()).decode()}')
        except Exception:
            return

    # return png data, if required
    if _www:
        return _png_data


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s)
    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description='Plot AVRO file FITS data', formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('--file', default='', help="""AVRO file""")
    _p.add_argument(f'--www', default=False, action='store_true', help='if present, produce www output')

    # execute
    args = _p.parse_args()
    avro_plot(args.file, bool(args.www))
