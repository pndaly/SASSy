#!/usr/bin/env python3


# +
# import(s)
# -
from src.models.ztf import NonDetection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import argparse
import fastavro
import glob
import os
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
SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PORT = os.getenv('SASSY_DB_PORT', None)


# +
# function: nondetection_read()
# -
# noinspection PyBroadException
def nondetection_read(_file='', _dir=''):

    # check input(s)
    if not isinstance(_file, str):
        raise Exception(f'invalid input, _file={_file}')
    if not isinstance(_dir, str):
        raise Exception(f'invalid input, _dir={_dir}')

    # set default(s)
    _file_list = []

    # get all data
    if _file != '':
        _file = os.path.abspath(os.path.expanduser(_file))
        if os.path.exists(_file):
            print(f"Appending {_file}")
            _file_list.append(_file)

    if _dir != '':
        _dir = os.path.abspath(os.path.expanduser(_dir))
        if os.path.isdir(_dir):
            _files = glob.glob(f"{_dir}/*.avro")
            if not _files:
                print(f"Appending {_files}")
                _file_list.append(_files)

    # proceed if we have files to process
    if not _file_list:
        print(f'No files to process')
        return
    print(f"Processing files {_file_list}")

    # connect to database
    try:
        print(f'connection string = postgresql+psycopg2://{SASSY_DB_USER}:{SASSY_DB_PASS}@'
              f'{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}')
        engine = create_engine(f'postgresql+psycopg2://{SASSY_DB_USER}:{SASSY_DB_PASS}@'
                               f'{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}')
        get_session = sessionmaker(bind=engine)
        session = get_session()
    except Exception as _e0:
        raise Exception(f'Failed to connect to database, error={_e0}')

    # process files
    for _fe in _file_list:
        _oid = ''
        _non_detections = []
        _packets = []

        # read the data
        try:
            with open(_fe, 'rb') as _f:
                _reader = fastavro.reader(_f)
                _schema = _reader.writer_schema
                for _packet in _reader:
                    _packets.append(_packet)
        except Exception as _e1:
            raise Exception(f'failed to read data from {_fe}, error={_e1}')

        # process the data
        for _i in range(len(_packets)):
            if 'objectId' in _packets[_i] and 'prv_candidates' in _packets[_i]:
                _oid = _packets[_i]['objectId']
                _prv = _packets[_i]['prv_candidates']
                for _j in range(len(_prv)):
                    if 'candid' in _prv[_j] and _prv[_j]['candid'] is None:
                        if all(_k in _prv[_j] for _k in ['diffmaglim', 'jd', 'fid']):
                            _nd = NonDetection(diffmaglim=float(_prv[_j]['diffmaglim']), jd=float(_prv[_j]['jd']),
                                               fid=_prv[_j]['fid'], objectid=_oid)
                            try:
                                print(f"Inserting object {_oid} into database")
                                session.add(_nd)
                                session.commit()
                                print(f"Inserted object {_oid} into database")
                            except Exception as _e3:
                                session.rollback()
                                print(f"Failed inserting object {_oid} into database, error={_e3}")


# +
# main()
# -
if __name__ == '__main__':

    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description='Populate GWGC database from file',
                                 formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('-f', '--file', default='', help="""Input file [%(default)s]""")
    _p.add_argument('-d', '--directory', default='', help="""Input directory [%(default)s]""")
    args = _p.parse_args()

    # execute
    if args.file:
        nondetection_read(args.file.strip(), args.directory.strip())
    else:
        print(f'<<ERROR>> Insufficient command line arguments specified\nUse: python3 {sys.argv[0]} --help')
