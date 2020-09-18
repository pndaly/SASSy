#!/usr/bin/env python3


# +
# import(s)
# -
from src import *
from src.models.ztf import NonDetection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


import argparse
import fastavro
import glob
import os
import psycopg2
import psycopg2.extras
import sys


# +
# __doc__ string
# -
__doc__ = """
    % python3 nondetection_read.py --help
"""


# +
# constant(s)
# -
DEF_NELMS = 100000
SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PORT = os.getenv('SASSY_DB_PORT', None)


# +
# function: db_get_valid()
# -
def db_get_valid(_session=None, _ilist=None):

    # check input(s)
    if _session is None or _ilist is None or not isinstance(_ilist, list) or _ilist is []:
        return

    # count record(s)
    _valid = []
    for _elem in _ilist:
        try:
            if _session.query(NonDetection).filter(NonDetection.objectid == _elem['objectid']).filter(
                    NonDetection.jd == _elem['jd']).count() == 0:
                _valid.append((_elem['diffmaglim'], _elem['objectid'], _elem['jd'], _elem['fid']))
        except Exception as _e:
            _session.rollback()
            raise Exception(f'Failed to insert values into database, error={_e}')

    # return valid entries
    return _valid


# +
# db_bulk_insert()
# -
def db_bulk_insert(_connection=None, _cursor=None, _ivalid=None):

    # check input(s)
    if _connection is None or _cursor is None or _ivalid is None or not isinstance(_ivalid, list) or _ivalid is []:
        return

    # bulk ingest
    try:
        psycopg2.extras.execute_values(
            _cursor,
            """INSERT INTO nondetection (diffmaglim, objectid, jd, fid) VALUES %s""", _ivalid, page_size=100)
        _connection.commit()
    except Exception as _e:
        _cursor.execute("rollback;")
        raise Exception(f'Failed to insert values into database, error={_e}')


# +
# function: nondetection_read()
# -
# noinspection PyBroadException
def nondetection_read(_file='', _dir='', _nelms=DEF_NELMS):

    # check input(s)
    if not isinstance(_file, str):
        raise Exception(f'invalid input, _file={_file}')
    if not isinstance(_dir, str):
        raise Exception(f'invalid input, _dir={_dir}')
    if not isinstance(_nelms, int) or _nelms <= 0:
        _nelms = DEF_NELMS

    # set default(s)
    _files, _non_detections, _total, _fc, _ic = [], [], 0, 0, 0

    # get all files
    if _dir != '':
        _dir = os.path.abspath(os.path.expanduser(_dir))
        if os.path.isdir(_dir):
            _files = glob.glob(f"{_dir}/*.avro")

    if _file != '':
        _file = os.path.abspath(os.path.expanduser(_file))
        if os.path.exists(_file):
            _files.append(_file)

    # proceed if we have files to process
    _total = len(_files)
    if _total == 0:
        print(f'{get_isot()}> No files to process')
        return
    else:
        print(f'{get_isot()}> Processing {_total} files')

    # connect to database (method 1)
    try:
        engine = create_engine(f'postgresql+psycopg2://{SASSY_DB_USER}:{SASSY_DB_PASS}@'
                               f'{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}')
        get_session = sessionmaker(bind=engine)
        session = get_session()
    except Exception as _e1:
        raise Exception(f'Failed to connect to database, error={_e1}')

    # connect to database (method 2)
    try:
        connection = psycopg2.connect(host=SASSY_DB_HOST, database=SASSY_DB_NAME,
                                      user=SASSY_DB_USER, password=SASSY_DB_PASS, port=int(SASSY_DB_PORT))
        connection.autocommit = True
        cursor = connection.cursor()
    except Exception as _e2:
        raise Exception(f"Failed to connect to database, error={_e2}")

    # process files
    for _fe in _files:

        # (re)set variable(s)
        _oid, _packets = '', []

        # read the data
        try:
            with open(_fe, 'rb') as _f:
                _reader = fastavro.reader(_f)
                _schema = _reader.writer_schema
                for _packet in _reader:
                    _packets.append(_packet)
                _fc += 1
        except Exception as _e3:
            raise Exception(f'Failed to read data from {_fe}, error={_e3}')

        # process the data
        for _i in range(len(_packets)):
            if 'objectId' in _packets[_i] and 'prv_candidates' in _packets[_i]:
                _oid = _packets[_i]['objectId']
                _prv = _packets[_i]['prv_candidates']
                if _prv is not None:
                    _prv = sorted(_prv, key=lambda x: x['jd'], reverse=True)
                    for _cand in _prv:
                        if all(_cand[_k1] is None for _k1 in
                               ('candid', 'isdiffpos', 'ra', 'dec', 'magpsf', 'sigmapsf', 'ranr', 'decnr')) and \
                                all(_cand[_k2] is not None for _k2 in ('diffmaglim', 'jd', 'fid')):
                            _non_detections.append({'objectid': _oid, 'diffmaglim': float(_cand['diffmaglim']),
                                                    'jd': float(_cand['jd']), 'fid': int(_cand['fid'])})
                            _ic += 1

        # submit after _nelms records have been found
        if _ic > _nelms and len(_non_detections) > 0:
            print(f"{get_isot()}> Inserting {len(_non_detections)} record(s) into database "
                  f"({_fc*100.0/_total:.2f}% complete)")
            _valid = db_get_valid(_session=session, _ilist=_non_detections)
            if _valid:
                db_bulk_insert(_connection=connection, _cursor=cursor, _ivalid=_valid)
            print(f"{get_isot()}> Inserted {len(_valid)} valid record(s), rejected {_nelms-len(_valid)} duplicate(s)")
            # reset
            _ic, _non_detections = 0, []

    # tidy up stragglers
    if len(_non_detections) > 0:
        print(f"{get_isot()}> Inserting {len(_non_detections)} straggler(s) into database "
              f"({_fc*100.0/_total:.2f}% complete)")
        _valid = db_get_valid(_session=session, _ilist=_non_detections)
        if _valid:
            db_bulk_insert(_connection=connection, _cursor=cursor, _ivalid=_valid)
        print(f"{get_isot()}> Inserted {len(_valid)} valid straggler(s), rejected {_nelms-len(_valid)} duplicate(s)")

    # close
    cursor.close()
    connection.close()
    session.close()


# +
# main()
# -
if __name__ == '__main__':

    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description='Populate NonDetection Table',
                                 formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('--file', default='', help="""Input file [%(default)s]""")
    _p.add_argument('--directory', default='', help="""Input directory [%(default)s]""")
    _p.add_argument('--nelms', default=DEF_NELMS, help="""Number of elements between screen updates [%(default)s]""")
    args = _p.parse_args()

    # execute
    if args.file or args.directory:
        nondetection_read(
            _file=args.file.strip(), _dir=args.directory.strip(), _nelms=int(args.nelms))
    else:
        print(f'<<ERROR>> Insufficient command line arguments specified\nUse: python3 {sys.argv[0]} --help')
