#!/usr/bin/env python3


# +
# import(s)
# -
from src.models.glade_q3c import GladeQ3cRecord
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
    % python3 glade_q3c_read.py --help
"""


# +
# constant(s)
# -
GLADE_Q3C_ALLOWED_HEADERS = ('PGC', 'Gwgc', 'HyperLEDA', 'TwoMass', 'SDSS', 'flag1', 'RA',
                             'Dec', 'Dist', 'Disterr', 'z', 'B', 'B_err', 'B_abs', 'J', 'J_err', 'H',
                             'H_err', 'K', 'K_err', 'flag2', 'flag3')
GLADE_Q3C_CATALOG_FILE = os.path.abspath(os.path.expanduser('glade_q3c.local.csv'))

SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PORT = os.getenv('SASSY_DB_PORT', None)


# +
# function: glade_q3c_read()
# -
# noinspection PyBroadException
def glade_q3c_read(_file=''):

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
    if not (all(_k in _columns for _k in GLADE_Q3C_ALLOWED_HEADERS)):
        raise Exception(f'Failed to get all allowed headers, please check {_file}'
                        f'\nfields expected are {GLADE_Q3C_ALLOWED_HEADERS}')

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
    _glade_q3c = None
    try:
        for _i in range(0, _num):

            # clean data
            _pgc = int(_columns['PGC'][_i]) if (str(_columns['PGC'][_i]).lower() != 'null') else None
            _gwgc = str(_columns['Gwgc'][_i])
            _hyperleda = str(_columns['HyperLEDA'][_i])
            _twomass = str(_columns['TwoMass'][_i])
            _sdss = str(_columns['SDSS'][_i])
            _f1 = _columns['flag1'][_i]
            _ra = float(_columns['RA'][_i]) if (str(_columns['RA'][_i]).lower() != 'null') else None
            _dec = float(_columns['Dec'][_i]) if (str(_columns['Dec'][_i]).lower() != 'null') else None
            _dist = float(_columns['Dist'][_i]) if (str(_columns['Dist'][_i]).lower() != 'null') else None
            _disterr = float(_columns['Disterr'][_i]) if (str(_columns['Disterr'][_i]).lower() != 'null') else None
            _z = float(_columns['z'][_i]) if (str(_columns['z'][_i]).lower() != 'null') else None
            _b = float(_columns['B'][_i]) if (str(_columns['B'][_i]).lower() != 'null') else None
            _b_err = float(_columns['B_err'][_i]) if (str(_columns['B_err'][_i]).lower() != 'null') else None
            _b_abs = float(_columns['B_abs'][_i]) if (str(_columns['B_abs'][_i]).lower() != 'null') else None
            _j = float(_columns['J'][_i]) if (str(_columns['J'][_i]).lower() != 'null') else None
            _j_err = float(_columns['J_err'][_i]) if (str(_columns['J_err'][_i]).lower() != 'null') else None
            _h = float(_columns['H'][_i]) if (str(_columns['H'][_i]).lower() != 'null') else None
            _h_err = float(_columns['H_err'][_i]) if (str(_columns['H_err'][_i]).lower() != 'null') else None
            _k = float(_columns['K'][_i]) if (str(_columns['K'][_i]).lower() != 'null') else None
            _k_err = float(_columns['K_err'][_i]) if (str(_columns['K_err'][_i]).lower() != 'null') else None
            _f2 = int(_columns['flag2'][_i]) if (str(_columns['flag2'][_i]).lower() != 'null') else None
            _f3 = int(_columns['flag3'][_i]) if (str(_columns['flag3'][_i]).lower() != 'null') else None

            # create object for each record
            _glade_q3c = GladeQ3cRecord(pgc=_pgc, gwgc=_gwgc, hyperleda=_hyperleda,
                                        twomass=_twomass, sdss=_sdss, flag1=_f1, ra=_ra, dec=_dec,
                                        dist=_dist, disterr=_disterr, z=_z, b=_b, b_err=_b_err, b_abs=_b_abs,
                                        j=_j, j_err=_j_err, h=_h, h_err=_h_err, k=_k, k_err=_k_err,
                                        flag2=_f2, flag3=_f3)

            # update database with results
            print(f"Committing GladeQ3cRecord(id={_i+1} {_pgc}, {_gwgc}, {_hyperleda}, {_twomass}, "
                  f"{_sdss}, {_f1}, {_ra}, {_dec}, {_dist}, {_disterr}, {_z}, {_b}, {_b_err}, "
                  f"{_b_abs}, {_j}, {_j_err}, {_h}, {_h_err}, {_k}, {_k_err}, {_f2}, {_f3})")
            session.add(_glade_q3c)
            session.commit()
    except Exception as e:
        session.rollback()
        raise Exception(f"Failed to insert object {_glade_q3c} into database, error={e}")


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s)
    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description='Populate GLADE_Q3C database from file',
                                 formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('-f', '--file', default=GLADE_Q3C_CATALOG_FILE, help="""Input file [%(default)s]""")
    args = _p.parse_args()

    # execute
    if args.file:
        glade_q3c_read(args.file.strip())
    else:
        print(f'<<ERROR>> Insufficient command line arguments specified\nUse: python3 {sys.argv[0]} --help')
