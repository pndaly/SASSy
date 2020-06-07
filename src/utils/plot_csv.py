#!/usr/bin/env python3


# +
# import(s)
# -
import argparse
import os
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio


# +
# doc
# -
__doc__ = """
    % python3 plot_csv.py --help
"""


# +
# function: plot_csv()
# -
# noinspection PyBroadException
def plot_csv(_file=''):

    # check input(s)
    try:
        _file = os.path.abspath(os.path.expanduser(_file))
        if not os.path.exists(_file):
            raise Exception(f'invalid input, _file={_file}')
    except:
        raise Exception(f'invalid input, _file={_file}')

    # get data
    _sid = f"{os.path.basename(_file).split('.')[0]}"
    _df = pd.read_csv(f'{_file}')

    # separate data by filter
    _red = _df[_df['filter'] == 'r']
    _green = _df[_df['filter'] == 'g']
    _indigo = _df[_df['filter'] == 'i']

    # create plot(s)
    plot_r = go.Scatter(x=_red.isot, y=_red.magpsf, mode='markers', name='r',
                        marker=dict(color='rgba(255, 0, 0, 0.8)'), text='r (magpsf, sigmapsf)',
                        error_y=dict(type='data', array=_red.sigmapsf, visible=True))
    plot_r_lim = go.Scatter(x=_red.isot, y=_red.diffmaglim, mode='markers', name='r (nd)',
                            marker=dict(symbol=106, color='rgba(255, 0, 0, 0.8)'), text='r (diffmaglim)')

    plot_g = go.Scatter(x=_green.isot, y=_green.magpsf, mode='markers', name='g',
                        marker=dict(color='rgba(0, 255, 0, 0.8)'), text='g (magpsf, sigmapsf)',
                        error_y=dict(type='data', array=_green.sigmapsf, visible=True))
    plot_g_lim = go.Scatter(x=_green.isot, y=_green.diffmaglim, mode='markers', name='g (nd)',
                            marker=dict(symbol=106, color='rgba(0, 255, 0, 0.8)'), text='g (diffmaglim)')

    plot_i = go.Scatter(x=_indigo.isot, y=_indigo.magpsf, mode='markers', name='i',
                        marker=dict(color='rgba(0, 0, 255, 0.8)'), text='i (magpsf, sigmapsf)',
                        error_y=dict(type='data', array=_indigo.sigmapsf, visible=True))
    plot_i_lim = go.Scatter(x=_indigo.isot, y=_indigo.diffmaglim, mode='markers', name='i (nd)',
                            marker=dict(symbol=106, color='rgba(0, 0, 255, 0.8)'), text='i (diffmaglim)')

    # define layout and show plot(s)
    data = [plot_r, plot_g, plot_i, plot_r_lim, plot_g_lim, plot_i_lim]
    layout = dict(title=f'Light Curve for {_sid} (csvfile={_file})', title_x=0.5,
                  xaxis=dict(title='Date', ticklen=5, zeroline=False), 
                  yaxis=dict(title='Magnitude', autorange='reversed'))
    pio.show(dict(data=data, layout=layout))


# +
# main()
# -
if __name__ == '__main__':

    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description='Plot ZTF LightCurve from CSV',
                                 formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('--file', default='', help="""Input CSV file""")
    _a = _p.parse_args()

    # execute
    plot_csv(_file=_a.file)
