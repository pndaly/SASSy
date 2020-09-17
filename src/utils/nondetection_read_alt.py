#!/usr/bin/env python3


# +
# import(s)
# -
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
    % python3 nondetection_read_alt.py --help
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
# function: nondetection_read_alt()
# -
# noinspection PyBroadException
def nondetection_read_alt(_file='', _dir='', _nelms=DEF_NELMS, _create=False):

    # check input(s)
    if not isinstance(_file, str):
        raise Exception(f'invalid input, _file={_file}')
    if not isinstance(_dir, str):
        raise Exception(f'invalid input, _dir={_dir}')
    if not isinstance(_nelms, int) or _nelms <= 0:
        raise Exception(f'invalid input, _nelms={_nelms}')

    # set default(s)
    _create = _create if isinstance(_create, bool) else False
    _files, _non_detections, _total, _ic = [], [], 0, 0

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
        print(f'No files to process')
        return
    else:
        print(f'Processing {_total} files')

    # connect to database
    try:
        connection = psycopg2.connect(host=SASSY_DB_HOST, database=SASSY_DB_NAME,
                                      user=SASSY_DB_USER, password=SASSY_DB_PASS, port=int(SASSY_DB_PORT))
        connection.autocommit = True
    except Exception as _e0:
        raise Exception(f"Failed to connect to database, error={_e0}")

    # create table
    try:
        cursor = connection.cursor()
    except Exception as _e1:
        raise Exception(f"Failed to get cursor, error={_e1}")

    # create table (if required)
    if _create:
        try:
            cursor.execute("""
            DROP TABLE IF EXISTS nondetection;
            CREATE TABLE nondetection (id serial PRIMARY KEY,
                  diffmaglim double precision NOT NULL,
                  objectid VARCHAR(50) NOT NULL,
                  jd double precision NOT NULL,
                  fid integer NOT NULL);
                CREATE INDEX idx_nondetection_jd ON nondetection(jd);
                CREATE INDEX idx_nondetection_objectid ON nondetection(objectid);
            """)
        except Exception as _e2:
            raise Exception(f"Failed to create database table, error={_e2}")

    # get next id
    # try:
    #     cursor.execute("SELECT COUNT(*) from nondetection;")
    #     _id = int(cursor.fetchone()[0]) + 1
    # except:
    #     _id = 0
    # print(f'Next _id is {_id}')

    # process files
    for _fe in _files:
        _oid = ''
        _packets = []

        # read the data
        try:
            with open(_fe, 'rb') as _f:
                _reader = fastavro.reader(_f)
                _schema = _reader.writer_schema
                for _packet in _reader:
                    _packets.append(_packet)
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
                            _non_detections.append(
                                (float(_cand['diffmaglim']), _oid, float(_cand['jd']), int(_cand['fid'])))
                            _ic += 1

        # submit after _nelms records have been found
        if _ic > _nelms:
            print(f"Inserting {_non_detections[0]} ... {_non_detections[-1]} "
                  f"({len(_non_detections)} values) into database")
            try:
                psycopg2.extras.execute_values(
                    cursor,
                    """INSERT INTO nondetection (diffmaglim, objectid, jd, fid) VALUES %s""",
                    _non_detections, page_size=100)
                connection.commit()
            except Exception as _e4:
                cursor.execute("rollback;")
                raise Exception(f'Failed to insert values into database, error={_e4}')
            else:
                _ic = 0
                _non_detections = []

    # tidy up stragglers
    if len(_non_detections) > 0:
        print(f"Inserting stragglers {_non_detections[0]} ... {_non_detections[-1]} "
              f"({len(_non_detections)} values) into database")
        try:
            psycopg2.extras.execute_values(
                cursor,
                """INSERT INTO nondetection (diffmaglim, objectid, jd, fid) VALUES %s""",
                _non_detections, page_size=100)
            connection.commit()
        except Exception as _e5:
            cursor.execute("rollback;")
            raise Exception(f'Failed to insert stragglers into database, error={_e5}')

    # close
    cursor.close()
    connection.close()


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
    _p.add_argument('--create', default=False, action='store_true', help='if present, create table')
    args = _p.parse_args()

    # execute
    if args.file or args.directory:
        nondetection_read_alt(
            _file=args.file.strip(), _dir=args.directory.strip(), _nelms=int(args.nelms), _create=bool(args.create))
    else:
        print(f'<<ERROR>> Insufficient command line arguments specified\nUse: python3 {sys.argv[0]} --help')
