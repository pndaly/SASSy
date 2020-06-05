#!/usr/bin/env python3


# +
# import(s)
# -
import argparse
import json
import os
import pandas as pd
import plotly.express as px


# +
# constant(s)
# -
COLUMNS = ['jd', 'filter', 'magpsf', 'sigmapsf', 'diffmaglim']
HEADERS = ['jd', 'filter', 'magpsf', 'sigmapsf', 'diffmaglim']


# +
# get_csv()
# -
# noinspection PyBroadException
def get_csv(_file='', _plot=False):

    # check input(s)
    if not isinstance(_file, str) or _file.strip() == '':
        raise Exception(f'invalid input, _if={_file}')
    _file = os.path.abspath(os.path.expanduser(_file))
    if not os.path.exists(_file):
        raise Exception(f'invalid input, _if={_file}')
    _plot = _plot if isinstance(_plot, bool) else False

    # load the data
    with open(_file, 'r') as _f:
        _dict = json.load(_f)

    # get this candidates data
    _data = []
    if 'candidate' in _dict.keys() and all(_k in _dict['candidate'] for _k in COLUMNS):
        _data.append({
            'jd': _dict['candidate']['jd'],
            'filter': _dict['candidate']['filter'],
            'magpsf': _dict['candidate']['magpsf'],
            'sigmapsf': _dict['candidate']['sigmapsf'],
            # 'diffmaglim': _dict['candidate']['diffmaglim']
        })

    # get some meta-data
    try:
        _title = f"ObjectId: {_dict['objectId']} Candid: {_dict['candid']} " \
                 f"RA: {_dict['candidate']['ra']:.3f}\u00B0 Dec: {_dict['candidate']['dec']:.3f}\u00B0"
    except Exception:
        _title = ''

    # get previous candidate data    
    if 'prv_candidate' in _dict.keys():
        for _e in _dict['prv_candidate']:
            if 'candidate' in _e and all(_k in _e['candidate'] for _k in COLUMNS):
                _data.append({
                    'jd': _e['candidate']['jd'],
                    'filter': _e['candidate']['filter'],
                    'magpsf': _e['candidate']['magpsf'],
                    'sigmapsf': _e['candidate']['sigmapsf'],
                    'diffmaglim': _e['candidate']['diffmaglim']
                })

    # create pandas dataframe
    _of = f"{os.path.basename(_file).split('.')[0]}.csv"
    _of = os.path.abspath(os.path.expanduser(_of))
    _df = pd.DataFrame(_data)
    _df.to_csv(f"{_of}", index=False, columns=COLUMNS, header=HEADERS)

    # read it back and plot it
    if _plot:
        _fig = px.scatter(_df, x='jd', y='magpsf', error_y='sigmapsf', color='filter')
        _fig.update_yaxes(autorange="reversed")
        if _fig.data[0]['name'] == 'r':
            _fig.data[0]['marker'].update(color='#ff0000')  # red
        elif _fig.data[0]['name'] == 'g':
            _fig.data[0]['marker'].update(color='#00ff00')  # green
        elif _fig.data[0]['name'] == 'i':
            _fig.data[0]['marker'].update(color='#0000ff')  # blue
        if _fig.data[1]['name'] == 'r':
            _fig.data[1]['marker'].update(color='#ff0000')  # red
        elif _fig.data[1]['name'] == 'g':
            _fig.data[1]['marker'].update(color='#00ff00')  # green
        elif _fig.data[1]['name'] == 'i':
            _fig.data[1]['marker'].update(color='#0000ff')  # blue
        _fig.update_layout(xaxis_title="Date", yaxis_title="Magnitude")
        _fig.update_layout(title={'text': _title, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'})

        _fig2 = px.scatter(_df, x='jd', y='diffmaglim', color='filter')
        _fig2['data'][0]['marker']['symbol'] = 'triangle-down-open'
        _fig2.update_yaxes(autorange="reversed")
        if _fig2.data[0]['name'] == 'r':
            _fig2.data[0]['marker'].update(color='#ff0000')  # red
        elif _fig2.data[0]['name'] == 'g':
            _fig2.data[0]['marker'].update(color='#00ff00')  # green
        elif _fig2.data[0]['name'] == 'i':
            _fig2.data[0]['marker'].update(color='#0000ff')  # blue
        if _fig2.data[1]['name'] == 'r':
            _fig2.data[1]['marker'].update(color='#ff0000')  # red
        elif _fig2.data[1]['name'] == 'g':
            _fig2.data[1]['marker'].update(color='#00ff00')  # green
        elif _fig2.data[1]['name'] == 'i':
            _fig2.data[1]['marker'].update(color='#0000ff')  # blue
        _fig.add_trace(_fig2.data[0])

        _fig.show()


# +
# main()
# -
if __name__ == '__main__':

    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description='Alert Lightcurve', formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('--file', default='', help="""Input file""")
    _p.add_argument('--plot', default=False, action='store_true', help="""if present, plot the data""")
    _a = _p.parse_args()

    # execute
    get_csv(_file=_a.file, _plot=bool(_a.plot))
