#!/usr/bin/env python3


# +
# import(s)
# -
from astropy.table import Table

import argparse
import astropy.coordinates as coord
import astropy.units as u
import matplotlib.pyplot as plt
import os
import sys


# +
# function: xephem_plot_catalog()
# -
# noinspection PyUnresolvedReferences
def xephem_plot_catalog(_file='', _catalog=''):

    # check input(s)
    if not os.path.isfile(os.path.abspath(os.path.expanduser(_file))):
        raise Exception(f'ERROR: invalid input, _file={_file}')
    if not os.path.isfile(os.path.abspath(os.path.expanduser(_catalog))):
        raise Exception(f'ERROR: invalid input, _catalog={_catalog}')

    # read data
    _t = Table.read(_file, format='csv')
    print(f"name={_t['objectId'][1]}, RA={_t['ra'][1]}, Dec={_t['dec'][1]}, mag={_t['magpsf'][1]}")
    print(f"name={_t['objectId'][-1]}, RA={_t['ra'][-1]}, Dec={_t['dec'][-1]}, mag={_t['magpsf'][-1]}")

    # plot RA vs. Dec
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, aspect='equal')
    ax.scatter(_t['ra'][1:], _t['dec'][1:], s=1, color='red')
    ax.set_title(f'{_file}\n{_catalog}', fontsize=12)
    ax.set_xlabel('RA (J2000)', fontsize=10)
    ax.set_ylabel('Dec (J2000)', fontsize=10)
    fig.show()
    plt.show()

    # plot aitoff
    ra = coord.Angle(_t['ra']*u.degree)
    ra = ra.wrap_at(180*u.degree)
    dec = coord.Angle(_t['dec']*u.degree)
    fig = plt.figure(figsize=(8, 6))
    bx = fig.add_subplot(111, projection="aitoff")
    bx.scatter(ra.radian, dec.radian, color='red')
    bx.set_title(f'{_file}', fontsize=12)
    bx.set_xlabel(f'{_catalog}', fontsize=9)
    bx.set_ylabel('Aitoff Projection', fontsize=7)
    bx.grid(True)
    fig.show()
    plt.show()


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s)
    # noinspection PyTypeChecker
    _parser = argparse.ArgumentParser(description='Plot Data and Catalog',
                                      formatter_class=argparse.RawTextHelpFormatter)
    _parser.add_argument('-f', '--file', default='', help="""Input CSV file""")
    _parser.add_argument('-c', '--catalog', default='', help="""Input EDB catalog""")
    args = _parser.parse_args()

    # execute
    if os.path.isfile(os.path.abspath(os.path.expanduser(args.file))) and \
            os.path.isfile(os.path.abspath(os.path.expanduser(args.catalog))):
        xephem_plot_catalog(os.path.abspath(os.path.expanduser(args.file)),
                            os.path.abspath(os.path.expanduser(args.catalog)))
    else:
        print(f'<<ERROR>> Insufficient command line arguments specified\nUse: python3 {sys.argv[0]} --help')
