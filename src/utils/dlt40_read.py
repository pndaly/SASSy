#!/usr/bin/env python3.7


# +
# import(s)
# -
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.dlt40 import Dlt40Record

import argparse
import csv
import os
import math
import sys


# +
# __doc__ string
# -
__doc__ = """
    % python3.7 dlt40_read.py --help
"""


# +
# constant(s)
# -
DLT40_ALLOWED_HEADERS = ('id', 'hostName', 'discoverer', 'prefix', 'objectname', 'redshift', 'discMag',
                         'ra', 'dec', 'sourceGroup', 'discMagFilter', 'discDate', 'classType', 'hostRedshift',
                         'cx', 'cy', 'cz', 'htm16ID')
DLT40_CATALOG_FILE = os.path.abspath(os.path.expanduser('TNS_DLT40.csv'))

SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PORT = os.getenv('SASSY_DB_PORT', None)


# +
# function: dlt40_read()
# -
# noinspection PyBroadException
def dlt40_read(_file=''):

    # check input(s)
    try:
        _file = os.path.abspath(os.path.expanduser(_file))
        if not os.path.exists(_file):
            raise Exception(f'no such file, _file={_file}')
    except Exception as _e:
        raise Exception(f'invalid input, _file={_file}, error={_e}')

    # set default(s)
    _num = 0
    _delimiter = ''
    _columns = None

    # get number of lines in file
    with open(_file, 'r') as _fd:
        _num = sum(1 for _l in _fd if (_l.strip() != '' and _l.strip()[0] not in r'#%!<>+\/'))
    if _num <= 0:
        raise Exception(f'file has no valid input lines, _file={_file}')

    # check file type is supported
    if _file.lower().endswith('csv'):
        print(f'Detected a CSV file format with {_num} lines')
        _delimiter = ','
    elif _file.lower().endswith('tsv'):
        print(f'Detected a TSV file format with {_num} lines')
        _delimiter = '\t'
    else:
        raise Exception(f'Unsupported file type (not .csv, .tsv)')

    # read the file
    with open(_file, 'r') as _fd:
        _r = csv.reader(_fd, delimiter=_delimiter)
        _headers = next(_r, None)

        # separate header line into column headings
        _headers = [_l if _l.strip()[0] not in r'#%!<>+\/' else _l[1:] for _l in _headers]
        _columns = {_h: [] for _h in _headers}

        # read rest of file into lists associated with each column heading
        for _row in _r:
            for _h, _v in zip(_headers, _row):
                _columns[_h].append(_v.strip())

    # sanity check
    print(f'Sanity checking data row/column match')
    if len(_columns)*_num != sum([len(_v) for _v in _columns.values()]):
        raise Exception(f'Failed sanity check data row/column match, please check {_file}')
    else:
        print(f'Sanity checked data row/column OK')

    # check we got all the allowed headers
    print(f'Checking the data')
    if not (all(_k in _columns for _k in DLT40_ALLOWED_HEADERS)):
        raise Exception(f'Failed to check the data, please check {_file}'
                        f'\nfields expected are {DLT40_ALLOWED_HEADERS}')
    else:
        print(f'Checked the data OK')

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
    _dlt40 = None
    for _i in range(0, _num):

        # read data and clean it up
        try:
            _id = int(_columns['id'][_i]) if (str(_columns['id'][_i]).lower() != 'null') else None
            _hostName = f"{_columns['hostName'][_i]}" \
                if (f"{_columns['hostName'][_i]}" != '' and f"{_columns['hostName'][_i].lower()}" != 'null') else ''
            _discoverer = f"{_columns['discoverer'][_i]}" \
                if (f"{_columns['discoverer'][_i]}" != '' and f"{_columns['discoverer'][_i].lower()}" != 'null') else ''
            _prefix = f"{_columns['prefix'][_i]}" \
                if (f"{_columns['prefix'][_i]}" != '' and f"{_columns['prefix'][_i].lower()}" != 'null') else ''
            _objectname = f"{_columns['objectname'][_i]}" \
                if (f"{_columns['objectname'][_i]}" != '' and f"{_columns['objectname'][_i].lower()}" != 'null') else ''
            _redshift = float(_columns['redshift'][_i]) \
                if (str(_columns['redshift'][_i]).lower() != 'null') else float(math.nan)
            _discMag = float(_columns['discMag'][_i]) \
                if (str(_columns['discMag'][_i]).lower() != 'null') else float(math.nan)
            _ra = float(_columns['ra'][_i]) if (str(_columns['ra'][_i]).lower() != 'null') else float(math.nan)
            _dec = float(_columns['dec'][_i]) if (str(_columns['dec'][_i]).lower() != 'null') else float(math.nan)
            _sourceGroup = f"{_columns['sourceGroup'][_i]}" \
                if (f"{_columns['sourceGroup'][_i]}" != '' and f"{_columns['sourceGroup'][_i].lower()}" != 'null') \
                else ''
            _discMagFilter = f"{_columns['discMagFilter'][_i]}" \
                if (f"{_columns['discMagFilter'][_i]}" != '' and f"{_columns['discMagFilter'][_i].lower()}" != 'null') \
                else ''
            _discDate = f"{_columns['discDate'][_i]}" \
                if (f"{_columns['discDate'][_i]}" != '' and f"{_columns['discDate'][_i].lower()}" != 'null') else ''
            _classType = f"{_columns['classType'][_i]}" \
                if (f"{_columns['classType'][_i]}" != '' and f"{_columns['classType'][_i].lower()}" != 'null') else ''
            _hostRedshift = float(_columns['hostRedshift'][_i]) \
                if (str(_columns['hostRedshift'][_i]).lower() != 'null') else float(math.nan)
            _cx = float(_columns['cx'][_i]) if (str(_columns['cx'][_i]).lower() != 'null') else float(math.nan)
            _cy = float(_columns['cy'][_i]) if (str(_columns['cy'][_i]).lower() != 'null') else float(math.nan)
            _cz = float(_columns['cz'][_i]) if (str(_columns['cz'][_i]).lower() != 'null') else float(math.nan)
            _htm16ID = int(_columns['htm16ID'][_i]) if (str(_columns['htm16ID'][_i]).lower() != 'null') else -1
        except Exception as e:
            raise Exception(f"Failed to decode object {_dlt40}, error={e}")

        # insert data
        try:
            _dlt40 = Dlt40Record(hostName=_hostName, discoverer=_discoverer,
                                 prefix=_prefix, objectname=_objectname, redshift=_redshift, discMag=_discMag,
                                 ra=_ra, dec=_dec, sourceGroup=_sourceGroup, discMagFilter=_discMagFilter,
                                 discDate=_discDate, classType=_classType, hostRedshift=_hostRedshift,
                                 cx=_cx, cy=_cy, cz=_cz, htm16ID=_htm16ID)
            print(f"Committing Dlt40Record('{_hostName}', '{_discoverer}', '{_prefix}', '{_objectname}', "
                  f"{_redshift}, {_discMag}, {_ra}, {_dec}, '{_sourceGroup}', '{_discMagFilter}', '{_discDate}', "
                  f"'{_classType}', {_hostRedshift}, {_cx}, {_cy}, {_cz}, {_htm16ID})")
            session.add(_dlt40)
            session.commit()
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to insert object {_dlt40} into database, error={e}")


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s)
    _p = argparse.ArgumentParser(description='Populate DLT40 database from file',
                                 formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('-f', '--file', default=DLT40_CATALOG_FILE, help="""Input file [%(default)s]""")
    args = _p.parse_args()

    # execute
    if args.file:
        dlt40_read(args.file.strip())
    else:
        print(f'<<ERROR>> Insufficient command line arguments specified\nUse: python3 {sys.argv[0]} --help')
