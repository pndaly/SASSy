#!/usr/bin/env python3


# +
# import(s)
# -
import argparse
import aplpy
import fastavro
import gzip
import io
import numpy as np
import os
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt

from astropy.time import Time
from astropy.io import fits

import warnings
warnings.filterwarnings('ignore', category=matplotlib.cbook.MatplotlibDeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)


# +
# dunder string(s)
# -
__doc__ = """
    % python3 avro_dump.py --help
"""

__author__ = 'Philip N. Daly'
__date__ = '17 January, 2019'
__email__ = 'pndaly@email.arizona.edu'
__institution__ = 'Steward Observatory, 933 N. Cherry Avenue, Tucson AZ 85719'


# +
# constant(s)
# -
AVRO_FILTERS = {1: 'green', 2: 'red', 3: 'blue'}
AVRO_OPTIONS = ['curve', 'cutouts', 'image', 'keyword', 'packet', 'schema', 'table']


# +
# function: make_dataframe()
# -
def make_dataframe(packet=None):

    # check input(s)
    if packet is None or not isinstance(packet, dict):
        raise Exception(f'invalid input, packet={packet}')

    # set variable(s)
    _retval = None

    # create pandas data frame
    if 'candidate' in packet and 'prv_candidates' in packet:
        df_1 = pd.DataFrame(packet['candidate'], index=[0])
        df_2 = pd.DataFrame(packet['prv_candidates'])
        _retval = pd.concat([df_1, df_2], ignore_index=True)

    # return
    return _retval


# +
# function: plot_lightcurve()
# -
def plot_lightcurve(ifile='', iname='', dflc=None, days_ago=True):

    # check input(s)
    if not isinstance(ifile, str) or ifile.strip() == '':
        raise Exception(f'invalid input, ifile={ifile}')
    if not isinstance(iname, str) or iname.strip() == '':
        raise Exception(f'invalid input, iname={iname}')
    if dflc is None:
        raise Exception(f'invalid input, dflc={dflc}')
    if not isinstance(days_ago, bool):
        raise Exception(f'invalid input, days_ago={days_ago}')

    # set variable(s)
    xlabel = 'Days Ago' if days_ago else 'Time (JD)'
    t = (dflc.jd - Time.now().jd) if days_ago else dflc.jd

    # get detections in each filter
    plt.figure()
    for _k, _v in AVRO_FILTERS.items():
        w = (dflc.fid == _k) & ~dflc.magpsf.isnull()
        if np.sum(w):
            plt.errorbar(t[w], dflc.loc[w, 'magpsf'], dflc.loc[w, 'sigmapsf'], fmt='.', color=_v)
        wnodet = (dflc.fid == _k) & dflc.magpsf.isnull()
        if np.sum(wnodet):
            plt.scatter(t[wnodet], dflc.loc[wnodet, 'diffmaglim'], marker='v', color=_v, alpha=0.25)

    # show plot(s)
    plt.gca().invert_yaxis()
    plt.title(f'packet {iname}')
    plt.suptitle(f'{ifile} Light Curve')
    plt.xlabel(xlabel)
    plt.ylabel('Magnitude')
    plt.show()


# +
# function: get_fits_image()
# -
def get_fits_image(fits_data=None, sub_fig=None, sub_plt=None):

    # check input(s)
    if fits_data is None or not isinstance(fits_data, bytes) or fits_data.strip() == r'':
        raise Exception(f'invalid input, fits_data={fits_data}')

    # get fits data
    try:
        with gzip.open(io.BytesIO(fits_data), 'rb') as f:
            with fits.open(io.BytesIO(f.read())) as hdul:
                if sub_fig is None:
                    sub_fig = plt.figure(figsize=(4, 4))
                if sub_plt is None:
                    sub_plt = (1, 1, 1)
                fits_fig = aplpy.FITSFigure(hdul[0], figure=sub_fig, subplot=sub_plt)
    except Exception as e:
        raise Exception(f'failed to read fits_data={fits_data}, error={e}')

    # plot it
    fits_fig.show_colorscale(stretch='arcsinh')
    return fits_fig


# +
# function: show_cutouts()
# -
def show_cutouts(packet=None):

    # check input(s)
    if packet is None or not isinstance(packet, dict):
        raise Exception(f'invalid input, packet={packet}')

    # set default(s)
    sub_fig = plt.figure(figsize=(12, 4))
    fits_fig = None
    fits_data = None

    # get fits data
    try:
        for _i, _c in enumerate(['Science', 'Template', 'Difference']):
            fits_data = packet[f'cutout{_c}']['stampData']
            fits_fig = get_fits_image(fits_data, sub_fig=sub_fig, sub_plt=(1, 3, _i + 1))
            plt.title(_c)
    except Exception as e:
        raise Exception(f'failed to read data for cutout, fits_data={fits_data}, error={e}')

    # return plot
    return fits_fig


# +
# function: action()
# -
def action(iargs):

    # check input(s)
    if not isinstance(iargs.file, str) or iargs.file.strip() == '':
        raise Exception(f'invalid input, file={iargs.file}')
    if not isinstance(iargs.show, str) or iargs.show.strip() == '':
        raise Exception(f'invalid input, show={iargs.show}')

    # declare some variable(s) and initialize them
    _packets = []
    _ifile = os.path.abspath(os.path.expanduser(iargs.file.strip()))
    _show = iargs.show.strip()
    if ':' in _show:
        _show, _keyword = _show.split(':')
    else:
        _show, _keyword = _show, ''

    # file does not exist
    if not os.path.isfile(_ifile):
        raise Exception(f'failed to access, file={iargs.file}')
    if _show not in AVRO_OPTIONS:
        raise Exception(f'failed to decode option, show={iargs.show}')

    # noinspection PyBroadException
    try:
        # read the data
        with open(_ifile, 'rb') as _f:
            _reader = fastavro.reader(_f)
            _schema = _reader.schema
            for _packet in _reader:
                _packets.append(_packet)
    except Exception as e:
        raise Exception(f'failed to read, file={_ifile}, error={e}')

    # dump lightcurve
    _show = _show.lower()
    if _show == 'curve':
        for _i in range(len(_packets)):
            plot_lightcurve(f'{_ifile}', f"{_packets[_i]['candid']}", make_dataframe(_packets[_i]))

    # dump image
    elif _show == 'image':
        for _i in range(len(_packets)):
            _im = get_fits_image(_packets[_i]['cutoutScience']['stampData'])
            plt.suptitle('Science Cutout')
            plt.title(_packets[_i]['cutoutScience']['fileName'])
            plt.show(_im)

    # dump keyword
    elif _show == 'keyword':
        for _i in range(len(_packets)):
            if f'{_keyword}' in _packets[_i]:
                print(f"{_keyword} = {_packets[_i][f'{_keyword}']}")
            else:
                print(f'{_keyword} not present in packet')

    # dump packet
    elif _show == 'packet':
        for _i in range(len(_packets)):
            print(f'{_packets[_i]}')

    # dump schema
    elif _show == 'schema':
        for _k, _v in _schema.items():
            print(f"schema['{_k}']={_v}")

    # dump cutouts
    elif _show == 'cutouts':
        for _i in range(len(_packets)):
            _im = show_cutouts(_packets[_i])
            plt.suptitle(f'{_ifile} Cutout Image(s)')
            plt.show(_im)

    # dump table
    elif _show == 'table':
        for _i in range(len(_packets)):
            print(f'{make_dataframe(_packets[_i])}')


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s)
    _p = argparse.ArgumentParser(description='Dump AVRO file',
                                 formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('-f', '--file', default='', help="""Input file""")
    _p.add_argument('-s', '--show', default='table', help=f"""Choose one of {AVRO_OPTIONS}""")
    args = _p.parse_args()

    # execute
    if args.file and args.show:
        action(args)
    else:
        print('<<ERROR>> Insufficient command line arguments specified\nUse: python3 {sys.argv[0]} --help')
