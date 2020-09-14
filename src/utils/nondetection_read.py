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
    _files = []

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
    if len(_files) == 0:
        print(f'No files to process')
        return
    else:
        print(f'Processing {len(_files)} files')

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
    for _fe in _files:
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
                if _prv is not None:
                    for _j in range(len(_prv)):
                        if 'candid' in _prv[_j] and _prv[_j]['candid'] is None:
                            if all(_k in _prv[_j] for _k in ['diffmaglim', 'jd', 'fid']):
                                _diffmaglim = float(_prv[_j]['diffmaglim'])
                                _jd = float(_prv[_j]['jd'])
                                _fid = int(_prv[_j]['fid'])
                                _nd = NonDetection(diffmaglim=_diffmaglim, jd=_jd, fid=_fid, objectid=_oid)
                                try:
                                    print(f"Inserting nondetection for {_oid} ({_diffmaglim:.2f}, {_jd:.4f}, {_fid}) into database")
                                    session.add(_nd)
                                    session.commit()
                                    print(f"Inserted nondetection for {_oid} ({_diffmaglim:.2f}, {_jd:.4f}, {_fid}) into database")
                                except Exception as _e3:
                                    session.rollback()
                                    print(f"Failed inserting nondetection for {_oid} ({_diffmaglim:.2f}, {_jd:.4f}, {_fid}) into database, error={_e3}")


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
    if args.file or args.directory:
        nondetection_read(args.file.strip(), args.directory.strip())
    else:
        print(f'<<ERROR>> Insufficient command line arguments specified\nUse: python3 {sys.argv[0]} --help')
