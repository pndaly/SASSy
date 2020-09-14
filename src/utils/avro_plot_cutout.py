#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# +
# import(s)
# -
from astropy.io import fits
from src import *
from src.utils.utils import UtilsLogger

import argparse
import fastavro
import gzip
import io
import os


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


# +
# constant(s)
# -
COLOUR_MAPS = [_map for _map in cm.datad]
CUTOUTS = ['difference', 'science', 'template']


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
# function: avro_plot_cutout()
# -
# noinspection PyBroadException,PyUnresolvedReferences
def avro_plot_cutout(_avro_file='', _cutout='', _oid='', _jd=0.0, _gid=0, _log=None):

    # check input(s)
    if not isinstance(_avro_file, str) or _avro_file.strip() == '':
        raise Exception(f'invalid input, _avro_file={_avro_file}')
    if not isinstance(_cutout, str) or _cutout.strip().lower() not in CUTOUTS:
        raise Exception(f'invalid input, _cutout={_cutout}')
    if not isinstance(_oid, str) or _oid.strip() == '':
        raise Exception(f'invalid input, _oid={_oid}')
    if not isinstance(_jd, float) or _jd < 0.0:
        raise Exception(f'invalid input, _jd={_jd}')
    if not isinstance(_gid, int) or _gid < 0:
        raise Exception(f'invalid input, _gid={_gid}')

    _file = os.path.abspath(os.path.expanduser(_avro_file.strip()))
    if not os.path.exists(_file):
        return
    if _log is not None:
        _log.debug(f"avro_plot_cutout(_avro_file='{_avro_file}', _cutout='{_cutout}', _oid='{_oid}', _jd={_jd}, _gid={_gid}, _log={_log}) ... entry")

    # set default(s)
    _sjd = str(_jd).strip().replace('.', '')
    _dif = True if _cutout.strip().lower() == 'difference' else False
    _sci = True if _cutout.strip().lower() == 'science' else False
    _tmp = True if _cutout.strip().lower() == 'template' else False
    _packets, _png_files, _title = [], [], ''

    # read the packet(s)
    try:
        with open(_file, 'rb') as _f:
            for _pk in fastavro.reader(_f):
                _packets.append(_pk)
    except Exception as _e:
        if _log is not None:
            _log.error(f"failed to open {_file}, error={_e}")
        pass

    # plot data
    for _i in range(len(_packets)):

        # get data
        _cmap, _data, _output = 'gray', None, ''
        if _dif:
            # _cmap = 'gray' if 'gray' in COLOUR_MAPS else random.choice(COLOUR_MAPS)
            _data = _get_fits_data(_packets[_i][f'cutoutDifference']['stampData'])
            _output = f'{_oid.strip()}_{_sjd}_{_gid}_{_i}_difference.png'
            _title = f'Difference ({_cmap})'
        elif _sci:
            # _cmap = 'gray' if 'gray' in COLOUR_MAPS else random.choice(COLOUR_MAPS)
            _data = _get_fits_data(_packets[_i][f'cutoutScience']['stampData'])
            _output = f'{_oid.strip()}_{_sjd}_{_gid}_{_i}_science.png'
            _title = f'Science ({_cmap})'
        elif _tmp:
            # _cmap = 'gray' if 'gray' in COLOUR_MAPS else random.choice(COLOUR_MAPS)
            _data = _get_fits_data(_packets[_i][f'cutoutTemplate']['stampData'])
            _output = f'{_oid.strip()}_{_sjd}_{_gid}_{_i}_template.png'
            _title = f'Template ({_cmap})'
        _png_files.append(_output)

        # plot it
        try:
            _fig = plt.figure()
            _fig.add_subplot(1, 1, 1)
            plt.imshow(_data, cmap=_cmap, origin='lower')
            plt.title(_title)
            _buf = io.BytesIO()
            plt.savefig(_output)
            plt.savefig(_buf, format='png', dpi=100, bbox_inches='tight')
            plt.close()
        except Exception as _f:
            if _log is not None:
                _log.error(f'failed to plot cutout, error={_f}')
            pass

    # return filename
    _of = _png_files[0] if len(_png_files) > 0 else ''
    if _log is not None:
        _log.debug(f"avro_plot_cutout() ... exit ... _png_file={_png_files}, _of={_of}")
    return _of


# +
# main()
# -
if __name__ == '__main__':

    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description='Plot AVRO file FITS data', formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('--file', default='', help="""AVRO input file""")
    _p.add_argument('--cutout', default=CUTOUTS[1], help=f"""AVRO cutout, default '%(default)s', choice of {CUTOUTS}""")
    _p.add_argument('--oid', default=f"ZTF20{get_hash()[:8]}", help="""ZTF Object Id""")
    _p.add_argument('--jd', default=0.0, help="""ZTF Julian Day""")
    _p.add_argument('--gid', default=0, help="""Glade Id""")

    # execute
    args = _p.parse_args()
    avro_plot_cutout(_avro_file=args.file, _cutout=args.cutout, _oid=args.oid,
                     _jd=float(args.jd), _gid=int(args.gid), _log=UtilsLogger('AvroPlot2').logger)
