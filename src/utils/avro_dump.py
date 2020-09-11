#!/usr/bin/env python3


# +
# import(s)
# -
import argparse
import aplpy
import fastavro
import gzip
import io
import math
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


# +
# constant(s)
# -
FILTERS = {1: 'g', 2: 'r', 3: 'i'}
OPTIONS = ['csv', 'curve', 'cutouts', 'image', 'keyword', 'non_detections', 'packet', 'photometry', 'schema', 'table']


# +
# function: jd_to_isot()
# -
# noinspection PyBroadException
def jd_to_isot(jd=math.nan):
    """ return isot from jd """
    try:
        return Time(jd, format='jd', precision=6).isot
    except:
        return None


# +
# function: make_dataframe()
# -
# noinspection PyBroadException
def make_dataframe(packet=None):

    # check input(s)
    if packet is None or not isinstance(packet, dict):
        raise Exception(f'invalid input, packet={packet}')

    # create pandas data frame
    try:
        if 'candidate' in packet and 'prv_candidates' in packet:
            df_1 = pd.DataFrame(packet['candidate'], index=[0])
            df_2 = pd.DataFrame(packet['prv_candidates'])
            return pd.concat([df_1, df_2], ignore_index=True)
        else:
            return None
    except Exception:
        return None


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
    for _k, _v in FILTERS.items():
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
# function: avro_dump()
# -
# noinspection PyBroadException
def avro_dump(_file='', _show=''):

    # check input(s)
    if not isinstance(_file, str) or _file.strip() == '':
        raise Exception(f'invalid input, _file={_file}')
    if not isinstance(_show, str) or _show.strip().lower() not in OPTIONS:
        raise Exception(f'invalid input, _show={_show}')

    # validate input(s)
    _file = os.path.abspath(os.path.expanduser(_file.strip()))
    if not os.path.exists(_file):
        raise Exception(f'failed to access, _file={_file}')
    _show = _show.strip().lower()
    if ':' in _show:
        _show, _keyword = _show.split(':')
    else:
        _show, _keyword = _show, ''

    # set default(s)
    _dirname = os.path.dirname(_file)
    _basename = os.path.basename(_file)
    _csv = os.path.join(_dirname, _basename.replace('.avro', '.csv')) if os.access(_dirname, os.W_OK) \
        else _basename.replace('.avro', '.csv')
    _non_detections = []
    _packets = []
    _photometry = []

    # read the data
    try:
        with open(_file, 'rb') as _f:
            _reader = fastavro.reader(_f)
            _schema = _reader.writer_schema
            for _packet in _reader:
                _packets.append(_packet)
    except Exception as _e1:
        raise Exception(f'failed to read data from {_file}, error={_e1}')

    # ['<<csv>>', 'curve', 'cutouts', 'image', 'keyword', 'non_detections', 'packet', 'photometry', 'schema', 'table']
    if _show == 'csv':
        try:
            _total = pd.DataFrame()
            for _i in range(len(_packets)):
                _df = make_dataframe(_packets[_i])
                _df.rename(columns={'fid': 'filter'}, inplace=True)
                _df['filter'] = _df['filter'].map(FILTERS)
                _total = pd.concat([_total, _df])
            _total.to_csv(f"{_csv}", index=False, columns=['jd', 'filter', 'diffmaglim', 'magpsf', 'sigmapsf'],
                          header=['#jd', 'filter', 'diffmaglim', 'magpsf', 'sigmapsf'])
            print(f'Created {_csv}')
        except Exception as _e2:
            print(f'Failed to create {_csv}, error={_e2}')

    # ['csv', '<<curve>>', 'cutouts', 'image', 'keyword', 'non_detections', 'packet', 'photometry', 'schema', 'table']
    elif _show == 'curve':
        try:
            for _i in range(len(_packets)):
                plot_lightcurve(f'{_file}', f"{_packets[_i]['candid']}", make_dataframe(_packets[_i]))
        except Exception as _e3:
            print(f'Failed to plot lightcurve for {_file}, error={_e3}')

    # ['csv', 'curve', '<<cutouts>>', 'image', 'keyword', 'non_detections', 'packet', 'photometry', 'schema', 'table']
    elif _show == 'cutouts':
        try:
            for _i in range(len(_packets)):
                _im = show_cutouts(_packets[_i])
                plt.suptitle(f'{_file} Cutout Image(s)')
                plt.show(_im)
        except Exception as _e4:
            print(f'Failed to plot cutouts for {_file}, error={_e4}')

    # ['csv', 'curve', 'cutouts', '<<image>>', 'keyword', 'non_detections', 'packet', 'photometry', 'schema', 'table']
    elif _show == 'image':
        try:
            for _i in range(len(_packets)):
                _im = get_fits_image(_packets[_i]['cutoutScience']['stampData'])
                plt.suptitle('Science Cutout')
                plt.title(_packets[_i]['cutoutScience']['fileName'])
                plt.show(_im)
        except Exception as _e5:
            print(f'Failed to plot image for {_file}, error={_e5}')

    # ['csv', 'curve', 'cutouts', 'image', '<<keyword>>', 'non_detections', 'packet', 'photometry', 'schema', 'table']
    elif _show == 'keyword':
        try:
            for _i in range(len(_packets)):
                if f'{_keyword}' in _packets[_i]:
                    print(f"{_keyword} = {_packets[_i][f'{_keyword}']}")
                else:
                    print(f'{_keyword} not present in packet')
        except Exception as _e6:
            print(f'Failed to show keyword for {_file}, error={_e6}')

    # ['csv', 'curve', 'cutouts', 'image', 'keyword', '<<non_detections>>', 'packet', 'photometry', 'schema', 'table']
    elif _show == 'non_detections':
        try:
            for _i in range(len(_packets)):
                if 'prv_candidates' in _packets[_i]:
                    _prv = _packets[_i]['prv_candidates']
                    for _j in range(len(_prv)):
                        if 'candid' in _prv[_j] and _prv[_j]['candid'] is None:
                            if all(_k in _prv[_j] for _k in ['diffmaglim', 'jd', 'fid']):
                                _non_detections.append({'diffmaglim': float(_prv[_j]['diffmaglim']),
                                                        'jd': float(_prv[_j]['jd']),
                                                        'filter': FILTERS.get(_prv[_j]['fid']),
                                                        'isot': jd_to_isot(_prv[_j]['jd'])})
            print(f"{_non_detections}")
        except Exception as _e7:
            print(f'Failed to show non_detections for {_file}, error={_e7}')

    # ['csv', 'curve', 'cutouts', 'image', 'keyword', 'non_detections', '<<packet>>', 'photometry', 'schema', 'table']
    elif _show == 'packet':
        try:
            for _i in range(len(_packets)):
                print(f'{_packets[_i]}')
        except Exception as _e8:
            print(f'Failed to show packets for {_file}, error={_e8}')

    # ['csv', 'curve', 'cutouts', 'image', 'keyword', 'non_detections', 'packet', '<<photometry>>', 'schema', 'table']
    elif _show == 'photometry':
        try:
            for _i in range(len(_packets)):
                if 'candidate' in _packets[_i]:
                    _cand = _packets[_i]['candidate']
                    if all(_k in _cand for _k in ['magpsf', 'sigmapsf', 'diffmaglim', 'jd', 'fid']):
                        _photometry.append({'magpsf': float(_cand['magpsf']), 'sigmapsf': float(_cand['sigmapsf']),
                                            'diffmaglim': float(_cand['diffmaglim']), 'jd': float(_cand['jd']),
                                            'filter': FILTERS.get(_cand['fid']), 'isot': jd_to_isot(_cand['jd'])})
                if 'prv_candidates' in _packets[_i]:
                    _prv = _packets[_i]['prv_candidates']
                    if all(_k in _prv for _k in ['magpsf', 'sigmapsf', 'diffmaglim', 'jd', 'fid']):
                        _photometry.append({'magpsf': float(_prv['magpsf']), 'sigmapsf': float(_prv['sigmapsf']),
                                            'diffmaglim': float(_prv['diffmaglim']), 'jd': float(_prv['jd']),
                                            'filter': FILTERS.get(_prv['fid']), 'isot': jd_to_isot(_prv['jd'])})
            print(f"{_photometry}")
        except Exception as _e9:
            print(f'Failed to show photometry for {_file}, error={_e9}')

    # ['csv', 'curve', 'cutouts', 'image', 'keyword', 'non_detections', 'packet', 'photometry', '<<schema>>', 'table']
    elif _show == 'schema':
        try:
            for _k, _v in _schema.items():
                print(f"schema['{_k}']={_v}")
        except Exception as _e10:
            print(f'Failed to show schema for {_file}, error={_e10}')

    # ['csv', 'curve', 'cutouts', 'image', 'keyword', 'non_detections', 'packet', 'photometry', 'schema', '<<table>>']
    elif _show == 'table':
        try:
            for _i in range(len(_packets)):
                print(f'{make_dataframe(_packets[_i])}')
        except Exception as _e11:
            print(f'Failed to show table for {_file}, error={_e11}')


# +
# main()
# -
if __name__ == '__main__':

    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description='Dump AVRO file', formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('-f', '--file', default='', help="""Input file""")
    _p.add_argument('-s', '--show', default='table', help=f"""Choose one of {OPTIONS}""")
    args = _p.parse_args()

    # execute
    avro_dump(_file=args.file, _show=args.show)
