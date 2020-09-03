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
import matplotlib.cm as cm
import matplotlib.pyplot as plt


# +
# constant(s)
# -
COLOUR_MAPS = [_map for _map in cm.datad]
CUTOUTS = ['difference', 'science', 'template']
PNG_OUTPUT = 'test.png'


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
def avro_plot_cutout(_avro_file='', _cutout='', _oid='', _candid=0, _log=None):

    # check input(s)
    if not isinstance(_avro_file, str) or _avro_file.strip() == '':
        raise Exception(f'invalid input, _avro_file={_avro_file}')
    if not isinstance(_cutout, str) or _cutout.strip().lower() not in CUTOUTS:
        raise Exception(f'invalid input, _cutout={_cutout}')
    if not isinstance(_oid, str) or _oid.strip() == '':
        raise Exception(f'invalid input, _oid={_oid}')
    if not isinstance(_candid, int) or _candid < 0:
        raise Exception(f'invalid input, _candid={_candid}')

    _file = os.path.abspath(os.path.expanduser(_avro_file.strip()))
    if not os.path.exists(_file):
        return
    if _candid == 0:
        _candid = os.path.basename(_file).split('.')[0]
    if _log is not None:
        _log.debug(f'_avro_file={_avro_file}')
        _log.debug(f'_cutout={_cutout}')
        _log.debug(f'_oid={_oid}')
        _log.debug(f'_candid={_candid}')
        _log.debug(f'_log={_log}, type={type(_log)}')
        _log.debug(f'_file={_file}')

    # set default(s)
    _dif = True if _cutout.strip().lower() == 'difference' else False
    _sci = True if _cutout.strip().lower() == 'science' else False
    _tmp = True if _cutout.strip().lower() == 'template' else False
    _packets = []

    if _log is not None:
        _log.debug(f'_dif={_dif}')
        _log.debug(f'_sci={_sci}')
        _log.debug(f'_tmp={_tmp}')

    # read the packet(s)
    try:
        with open(_file, 'rb') as _f:
            for _pk in fastavro.reader(_f):
                _packets.append(_pk)
    except Exception as _e:
        raise Exception(f'failed to open {_file}, error={_e}')

    # plot data
    for _i in range(len(_packets)):

        # get data
        _col, _data, _output = '', None, ''
        if _dif:
            _col = 'viridis' if 'viridis' in COLOUR_MAPS else random.choice(COLOUR_MAPS)
            _data = _get_fits_data(_packets[_i][f'cutoutDifference']['stampData'])
            _output = os.path.abspath(os.path.expanduser(f'{_oid.strip()}_{_candid}_{_i}_difference.png'))
        elif _sci:
            _col = 'coolwarm' if 'coolwarm' in COLOUR_MAPS else random.choice(COLOUR_MAPS)
            _data = _get_fits_data(_packets[_i][f'cutoutScience']['stampData'])
            _output = os.path.abspath(os.path.expanduser(f'{_oid.strip()}_{_candid}_{_i}_science.png'))
        elif _tmp:
            _col = 'heat' if 'heat' in COLOUR_MAPS else random.choice(COLOUR_MAPS)
            _data = _get_fits_data(_packets[_i][f'cutoutTemplate']['stampData'])
            _output = os.path.abspath(os.path.expanduser(f'{_oid.strip()}_{_candid}_{_i}_template.png'))

        # plot it
        try:
            _fig = plt.figure()
            _fig.add_subplot(1, 1, 1)
            plt.imshow(_data, cmap=_col, origin='lower')
            if _dif:
                plt.title(f'Difference')
            if _sci:
                plt.title(f'Science')
            if _tmp:
                plt.title(f'Template')
            _buf = io.BytesIO()
            plt.savefig(_output)
            plt.savefig(_buf, format='png', dpi=100, bbox_inches='tight')
            plt.close()
        except Exception:
            pass


# +
# main()
# -
if __name__ == '__main__':

    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description='Plot AVRO file FITS data', formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('--file', default='', help="""AVRO input file""")
    _p.add_argument('--cutout', default=CUTOUTS[1], help=f"""AVRO cutout, default '%(default)s', choice of {CUTOUTS}""")
    _p.add_argument('--oid', default=f"ZTF20{get_hash()[:8]}", help="""ZTF Object Id""")
    _p.add_argument('--candid', default=0, help="""ZTF Candidate Id""")

    # execute
    args = _p.parse_args()
    avro_plot_cutout(_avro_file=args.file, _cutout=args.cutout, _oid=args.oid,
                     _candid=int(args.candid), _log=UtilsLogger('AvroPlot2').logger)
