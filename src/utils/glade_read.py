#!/usr/bin/env python3


# +
# import(s)
# -
from src.models.glade import GladeRecord
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import argparse
import csv
import os
import sys


# +
# __doc__ string
# -
__doc__ = """
    % python3 glade_read.py --help
"""


# +
# constant(s)
# -
GLADE_ALLOWED_HEADERS = ('PGC', 'Gwgc_Name', 'HyperLEDA_Name', '2MASS_Name', 'SDSS-DR12_Name', 'flag1', 'RA',
                         'Dec', 'Dist', 'Dist_err', 'z', 'B_mag', 'B_err', 'B_abs', 'J_mag', 'J_err', 'H_mag',
                         'H_err', 'K_mag', 'K_err', 'flag2', 'flag3')
GLADE_CATALOG_FILE = os.path.abspath(os.path.expanduser('glade.local.csv'))

SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PORT = os.getenv('SASSY_DB_PORT', None)


# +
# function: glade_read()
# -
# noinspection PyBroadException
def glade_read(_file=''):

    # check input(s)
    _file = os.path.abspath(os.path.expanduser(_file))
    if not isinstance(_file, str) or not os.path.exists(_file):
        raise Exception(f'invalid input, _file={_file}')

    # get number of lines in file
    _num = 0
    with open(_file, 'r') as _fd:
        _num = sum(1 for _l in _fd if (_l.strip() != '' and _l.strip()[0] not in r'#%!<>+\/'))

    # check file type is supported
    _delimiter = ''
    if _file.lower().endswith('csv'):
        print(f'Detected a CSV file format with {_num} lines')
        _delimiter = ','
    elif _file.lower().endswith('tsv'):
        print(f'Detected a TSV file format with {_num} lines')
        _delimiter = '\t'
    else:
        raise Exception(f'Unsupported file type (not .csv, .tsv)')

    # read the file
    _columns = {}
    with open(_file, 'r') as _fd:
        _r = csv.reader(_fd, delimiter=_delimiter)
        _headers = next(_r, None)

        # separate header line into column headings
        for _h in _headers:
            _columns[_h] = []

        # read rest of file into lists associated with each column heading
        for _row in _r:
            for _h, _v in zip(_headers, _row):
                _columns[_h].append(_v.strip())

    # sanity check
    print(f'Checking data global row/column match')
    if len(_columns)*_num != sum([len(_v) for _v in _columns.values()]):
        raise Exception(f'Irregular number of elements in {_file}, please check {_file}')

    # change the dictionary keys to remove unwanted characters
    print(f'Cleaning up column headers')
    for _k in list(_columns.keys()):
        _columns[_k.translate({ord(i): None for i in ' !@#$'})] = _columns.pop(_k)

    # check we got all the allowed headers
    print(f'Checking we have all the data')
    if not (all(_k in _columns for _k in GLADE_ALLOWED_HEADERS)):
        raise Exception(f'Failed to get all allowed headers, please check {_file}'
                        f'\nfields expected are {GLADE_ALLOWED_HEADERS}')

    # connect to database
    try:
        print(f'connection string = postgresql+psycopg2://{SASSY_DB_USER}:{SASSY_DB_PASS}@'
              f'{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}')
        engine = create_engine(f'postgresql+psycopg2://{SASSY_DB_USER}:{SASSY_DB_PASS}@'
                               f'{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}')
        get_session = sessionmaker(bind=engine)
        session = get_session()
    except Exception as e:
        raise Exception(f'Failed to connect to database, error={e}')

    # loop around records
    _glade = None
    try:
        for _i in range(0, _num):

            # clean data
            _pgc = int(_columns['PGC'][_i]) if (str(_columns['PGC'][_i]).lower() != 'null') else None
            _gwgc_name = str(_columns['Gwgc_Name'][_i])
            _hyperleda_name = str(_columns['HyperLEDA_Name'][_i])
            _2mass_name = str(_columns['2MASS_Name'][_i])
            _sdss_dr12_name = str(_columns['SDSS-DR12_Name'][_i])
            _f1 = _columns['flag1'][_i]
            _ra = float(_columns['RA'][_i]) if (str(_columns['RA'][_i]).lower() != 'null') else None
            _dec = float(_columns['Dec'][_i]) if (str(_columns['Dec'][_i]).lower() != 'null') else None
            _dist = float(_columns['Dist'][_i]) if (str(_columns['Dist'][_i]).lower() != 'null') else None
            _dist_err = float(_columns['Dist_err'][_i]) if (str(_columns['Dist_err'][_i]).lower() != 'null') else None
            _z = float(_columns['z'][_i]) if (str(_columns['z'][_i]).lower() != 'null') else None
            _b_mag = float(_columns['B_mag'][_i]) if (str(_columns['B_mag'][_i]).lower() != 'null') else None
            _b_err = float(_columns['B_err'][_i]) if (str(_columns['B_err'][_i]).lower() != 'null') else None
            _b_abs = float(_columns['B_abs'][_i]) if (str(_columns['B_abs'][_i]).lower() != 'null') else None
            _j_mag = float(_columns['J_mag'][_i]) if (str(_columns['J_mag'][_i]).lower() != 'null') else None
            _j_err = float(_columns['J_err'][_i]) if (str(_columns['J_err'][_i]).lower() != 'null') else None
            _h_mag = float(_columns['H_mag'][_i]) if (str(_columns['H_mag'][_i]).lower() != 'null') else None
            _h_err = float(_columns['H_err'][_i]) if (str(_columns['H_err'][_i]).lower() != 'null') else None
            _k_mag = float(_columns['K_mag'][_i]) if (str(_columns['K_mag'][_i]).lower() != 'null') else None
            _k_err = float(_columns['K_err'][_i]) if (str(_columns['K_err'][_i]).lower() != 'null') else None
            _f2 = int(_columns['flag2'][_i]) if (str(_columns['flag2'][_i]).lower() != 'null') else None
            _f3 = int(_columns['flag3'][_i]) if (str(_columns['flag3'][_i]).lower() != 'null') else None

            # create object for each record
            _glade = GladeRecord(pgc=_pgc, gwgc_name=_gwgc_name, hyperleda_name=_hyperleda_name,
                                 two_mass_name=_2mass_name, sdss_dr12_name=_sdss_dr12_name, flag1=_f1, ra=_ra, dec=_dec,
                                 dist=_dist, dist_err=_dist_err, z=_z, b_mag=_b_mag, b_err=_b_err, b_abs=_b_abs,
                                 j_mag=_j_mag, j_err=_j_err, h_mag=_h_mag, h_err=_h_err, k_mag=_k_mag, k_err=_k_err,
                                 flag2=_f2, flag3=_f3)

            # update database with results
            print(f"Committing GladeRecord(id={_i+1} {_pgc}, {_gwgc_name}, {_hyperleda_name}, {_2mass_name}, "
                  f"{_sdss_dr12_name}, {_f1}, {_ra}, {_dec}, {_dist}, {_dist_err}, {_z}, {_b_mag}, {_b_err}, "
                  f"{_b_abs}, {_j_mag}, {_j_err}, {_h_mag}, {_h_err}, {_k_mag}, {_k_err}, {_f2}, {_f3})")
            session.add(_glade)
            session.commit()
    except Exception as e:
        session.rollback()
        raise Exception(f"Failed to insert object {_glade} into database, error={e}")


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s)
    _p = argparse.ArgumentParser(description='Populate GLADE database from file',
                                 formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('-f', '--file', default=GLADE_CATALOG_FILE, help="""Input file [%(default)s]""")
    args = _p.parse_args()

    # execute
    if args.file:
        glade_read(args.file.strip())
    else:
        print(f'<<ERROR>> Insufficient command line arguments specified\nUse: python3 {sys.argv[0]} --help')
