#!/usr/bin/env python3


# +
# import(s)
# -
from astropy.time import Time

import argparse
import glob
import matplotlib.pyplot as plt
import os
import pandas
import re
import sys


# +
# dunder string(s)
# -
__doc__ = """Reads the SASSY_AVRO directories for file counts and plots them"""
__author__ = 'Philip N. Daly'
__date__ = '1 November, 2018'
__email__ = 'pndaly@email.arizona.edu'
__institution__ = 'Steward Observatory, 933 N. Cherry Avenue, Tucson AZ 85719'


# +
# (helper) function(s)
# -
def iso_today():
    """ return ISO for today """
    # noinspection PyBroadException
    try:
        return f'{Time.now().iso}'
    except Exception:
        return ''


def mjd_today():
    """ return MJD for today """
    # noinspection PyBroadException
    try:
        return iso_to_mjd(iso_today())
    except Exception:
        return -1.0


def iso_to_mjd(iso=''):
    """ return MJD or -1.0 """
    # noinspection PyBroadException
    try:
        return float(Time(iso).mjd)
    except Exception:
        return -1.0


def mjd_toiso(mjd=0.0):
    """ return ISO or '' """
    # noinspection PyBroadException
    try:
        return Time(mjd+2400000.5, format='jd', precision=3).iso
    except Exception:
        return ''


# +
# default(s)
# -
DIRECTORY_NOT_FOUND = -1
VALID_DATE_PATTERN = '[0-9]{4}-[0-9]{2}-[0-9]{2}'
VALID_PLOT_STYLES = plt.style.available

DEFAULT_AVRO_BEGIN = '2018-06-01'
DEFAULT_AVRO_DIR = os.path.abspath(os.path.expanduser(os.getenv('SASSY_AVRO', '.')))
DEFAULT_AVRO_END = iso_today().split()[0]
DEFAULT_AVRO_PLOT_STYLE = VALID_PLOT_STYLES[0]


# +
# function( action()
# -
def action(_dir=DEFAULT_AVRO_DIR, _begin=DEFAULT_AVRO_BEGIN, _end=DEFAULT_AVRO_END, _style='', verbose=False):

    # check input(s)
    if not isinstance(_dir, str) or _dir.strip() == '' or not os.path.isdir(os.path.abspath(os.path.expanduser(_dir))):
        raise Exception(f'Invalid input directory ({_dir}) ... exiting')
    if not isinstance(_begin, str) or _begin.strip() == '' or not re.search(VALID_DATE_PATTERN, _begin):
        raise Exception(f'Invalid begin date ({_begin}) ... exiting')
    if not isinstance(_end, str) or _dir.strip() == '' or not re.search(VALID_DATE_PATTERN, _end):
        raise Exception(f'Invalid end date ({_end}) ... exiting')
    if not isinstance(_style, str) or _style.strip() == '' or _style.lower() not in VALID_PLOT_STYLES:
        _style = DEFAULT_AVRO_PLOT_STYLE

    # convert date(s) and swap them if they were entered the wrong way around
    begin_mjd = iso_to_mjd(f'{_begin} 00:00:00.000')
    end_mjd = iso_to_mjd(f'{_end} 00:00:00.000')
    if end_mjd - begin_mjd <= 0.0:
        begin_mjd, end_mjd = end_mjd, begin_mjd
        _begin, _end = _end, _begin
    if verbose:
        print(f'Checking data between {_begin} and {_end}, a total of {int(end_mjd - begin_mjd) + 1} nights')

    # set default(s)
    result = {'iso': [], 'mjd': [], 'value': [], 'total': []}
    total = 0

    # get data
    for _mjd in range(int(begin_mjd), int(end_mjd+1), 1):

        iso = mjd_toiso(float(_mjd)).split()[0].replace('-', '/')
        if os.path.isdir(os.path.abspath(os.path.expanduser(f'{_dir}/{iso}'))):
            value = len(glob.glob(f'{_dir}/{iso}/*.avro'))
            total += value
        else:
            value = DIRECTORY_NOT_FOUND

        result['iso'].append(iso)
        result['mjd'].append(_mjd)
        result['value'].append(value)
        result['total'].append(total)

        if verbose:
            print(f"{_dir}/{iso} contains {value} avro files, cumulative total = {total}")

    # convert it
    pdata = pandas.DataFrame(result)
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))

    pdata.plot(x='mjd', y='value', kind='bar', ax=axes[0])
    axes[0].set_title('Alerts / Night')
    axes[0].set_xlabel('MJD')
    axes[0].set_ylabel('Count(s)')
    axes[0].yaxis.tick_left()
    axes[0].legend().set_visible(False)
    axes[0].grid(True)

    pdata.plot(x='mjd', y='total', kind='line', linestyle='-', marker='o', color='blue', ax=axes[1]) 
    axes[1].set_title('Cumulative Alerts')
    axes[1].set_xlabel('MJD')
    axes[1].set_ylabel('Total(s)')
    axes[1].yaxis.tick_right()
    axes[1].legend().set_visible(False)
    axes[1].grid(True)

    fig.suptitle(f'ZTF Alerts\n{_begin} through {_end}', fontsize=10, fontweight='bold')
    plt.xticks(rotation=90.0)
    plt.style.use(_style)
    plt.show()


# +
# entrypoint
# -
if __name__ == '__main__':

    # get command line argument(s)
    pstyle = str(VALID_PLOT_STYLES).replace("'", '').replace('[', '').replace(']', '').replace(', ', '\n')
    # noinspection PyTypeChecker
    _parser = argparse.ArgumentParser(description='Show AVRO file counts for given year and/or month',
                                      formatter_class=argparse.RawTextHelpFormatter)
    _parser.add_argument(f'-d', f'--directory', default=DEFAULT_AVRO_DIR,
                         help="""directory\n[default=%(default)s]""")
    _parser.add_argument(f'-b', f'--begin', default=DEFAULT_AVRO_BEGIN,
                         help="""begin date\n[default=%(default)s]""")
    _parser.add_argument(f'-e', f'--end', default=DEFAULT_AVRO_END,
                         help="""end date\n[default=%(default)s]""")
    _parser.add_argument(f'-s', f'--style', default=pstyle,
                         help="""plot style, choose one:\n%(default)s""")
    _parser.add_argument(f'-v', f'--verbose', default=False, action='store_true',
                         help=f'if present, produce more verbose output')
    args = _parser.parse_args()

    # execute
    if args.directory and args.begin and args.end:
        action(args.directory, args.begin, args.end, str(args.style), args.verbose)
    else:
        raise Exception(f'Insufficient command line arguments specified\nUse: python3 {sys.argv[0]} --help')
