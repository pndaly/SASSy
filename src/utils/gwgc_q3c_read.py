#!/usr/bin/env python3


# +
# import(s)
# -
from src.models.gwgc_q3c import GwgcQ3cRecord
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import argparse
import math
import os
import sys


# +
# __doc__ string
# -
__doc__ = """
    % python3 gwgc_q3c_read.py --help
"""


# +
# constant(s)
# -
GWGC_CATALOG_FILE = os.path.abspath(os.path.expanduser('gwgc.dat'))
GWGC_FORMAT = {
    'PGC':    [0,     7,  'int',     'None',    'Identifier from HYPERLEDA'],
    'Name':   [8,    36,  'string',  'None',    'Common name of galaxy or globular'],
    'RAhour': [37,   46,  'float',   'hours',   'J2000 Right Ascension'],
    'DEdeg':  [47,   55,  'float',   'degrees', 'J2000 Declination'],
    'TT':     [56,   60,  'float',   'None',    'Morphological type code'],
    'Bmag':   [61,   66,  'float',   'mag',     'Apparent blue magnitude'],
    'a':      [67,   74,  'float',   'arcmin',  'Major diameter'],
    'e_a':    [75,   82,  'float',   'arcmin',  'Error in major diameter'],
    'b':      [83,   90,  'float',   'arcmin',  'Minor diameter'],
    'e_b':    [91,   98,  'float',   'arcmin',  'Error in minor diameter'],
    'b/a':    [99,  104,  'float',   'None',    'Ratio of minor to major diameters'],
    'e_b/a':  [105, 110,  'float',   'None',    'Error in ratio of minor to major diameters'],
    'PA':     [111, 116,  'float',   'degrees', 'Position angle of galaxy'],
    'BMAG':   [117, 123,  'float',   'mag',     'Absolute blue magnitude'],
    'Dist':   [124, 131,  'float',   'Mpc',     'Distance'],
    'e_Dist': [132, 138,  'float',   'Mpc',     'Error in Distance'],
    'e_Bmag': [139, 143,  'float',   'mag',     'Error in apparent blue magnitude'],
    'e_BMAG': [144, 148,  'float',   'mag'      'Error in absolute blue magnitude']
}

SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PORT = os.getenv('SASSY_DB_PORT', None)


# +
# function: read_gwgc_q3c_read()
# -
def gwgc_q3c_read(_file=''):

    # check input(s)
    _file = os.path.abspath(os.path.expanduser(_file))
    if not isinstance(_file, str) or not os.path.exists(_file):
        raise Exception(f'invalid input, _file={_file}')

    # read contents
    with open(os.path.abspath(os.path.expanduser(_file)), 'r') as _fd:
        _lines = set(_fd.readlines())

    # get results
    _all_results = []
    for _i, _e in enumerate(_lines):
        _this_result = {}
        for _l in GWGC_FORMAT:
            _xoffset, _yoffset = GWGC_FORMAT[_l][0], GWGC_FORMAT[_l][1]
            _value = _e[_xoffset:_yoffset].strip()
            if GWGC_FORMAT[_l][2].strip().lower() == 'int':
                _this_result[_l] = -1 if _value == '' else int(_value)
            elif GWGC_FORMAT[_l][2].strip().lower() == 'float':
                _this_result[_l] = float(math.nan) if _value == '' else float(_value)
            else:
                _this_result[_l] = _value
            _this_result['id'] = int(_i)
        _all_results.append(_this_result)

    # noinspection PyBroadException
    try:
        # connect to database
        print(f'connection string = postgresql+psycopg2://{SASSY_DB_USER}:{SASSY_DB_PASS}@'
              f'{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}')
        engine = create_engine(f'postgresql+psycopg2://{SASSY_DB_USER}:{SASSY_DB_PASS}@'
                               f'{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}')
        get_session = sessionmaker(bind=engine)
        session = get_session()
    except Exception as e:
        raise Exception(f'Failed to connect to database, error={e}')

    # noinspection PyBroadException
    _record = None
    try:
        # loop around records
        for _record in _all_results:
            # create object for each record
            _gwgc_q3c = GwgcQ3cRecord(
                    id=_record['id'], 
                    pgc=_record['PGC'], 
                    name=_record['Name'],
                    ra=_record['RAhour'], 
                    dec=_record['DEdeg'], 
                    tt=_record['TT'],
                    b_app=_record['Bmag'], 
                    a=_record['a'], 
                    e_a=_record['e_a'], 
                    b=_record['b'],
                    e_b=_record['e_b'], 
                    b_div_a=_record['b/a'], 
                    e_b_div_a=_record['e_b/a'], 
                    pa=_record['PA'],
                    b_abs=_record['BMAG'], 
                    dist=_record['Dist'], 
                    e_dist=_record['e_Dist'],
                    e_b_app=_record['e_Bmag'], 
                    e_b_abs=_record['e_BMAG'])
            print(f'{_gwgc_q3c.serialized()}')
            # update database with results
            print(f"Inserting object {_record['Name']} database")
            session.add(_gwgc_q3c)
            session.commit()
            print(f"Inserted object {_record['Name']} database")
    except Exception as e:
        session.rollback()
        raise Exception(f"Failed to insert object {_record['Name']} database, error={e}")


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s)
    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description='Populate GWGC_Q3C database from file',
                                 formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('-f', '--file', default=GWGC_CATALOG_FILE, help="""Input file [%(default)s]""")
    args = _p.parse_args()

    # execute
    if args.file:
        gwgc_q3c_read(args.file.strip())
    else:
        print(f'<<ERROR>> Insufficient command line arguments specified\nUse: python3 {sys.argv[0]} --help')
