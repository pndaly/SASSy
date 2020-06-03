#!/usr/bin/env python3


# +
# import(s)
# -
import argparse
import os
import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.ztf import ZtfAlert


# +
# dunder string(s)
# -
__doc__ = """
    % python3 get_sid.py --help
"""

__author__ = 'Philip N. Daly'
__date__ = '19 May, 2020'
__email__ = 'pndaly@arizona.edu'
__institution__ = 'Steward Observatory, 933 N. Cherry Avenue, Tucson AZ 85719'


# +
# constant(s)
# -
AVRO_FILTERS = {1: 'g', 2: 'r', 3: 'i'}

SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PORT = os.getenv('SASSY_DB_PORT', None)


# +
# function(s)
# 
def db_connect():
    try:
        engine = create_engine(f'postgresql+psycopg2://{SASSY_DB_USER}:{SASSY_DB_PASS}@{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}')
        get_session = sessionmaker(bind=engine)
        return get_session()
    except Exception as e:
        print(f'Failed to connect to database, error={e}')
        return None


# noinspection PyBroadException
def db_disconnect(_session=None):
    try:
        _session.close()
        _session.close_all()
    except Exception:
        pass


def db_sid(_session=None, _sid=0):
    alert = _session.query(ZtfAlert).get(_sid)
    return alert.serialized(prv_candidate=True)


# +
# function: make_dataframe()
# -
# noinspection PyBroadException
def make_dataframe(packet=None):

    # check input(s)
    if packet is None or not isinstance(packet, dict):
        raise Exception(f'invalid input, packet={packet}')

    # create pandas data frame
    try:
        if 'candidate' in packet and 'prv_candidates' in packet:
            df_1 = pd.DataFrame(packet['candidate'], index=[0])
            df_2 = pd.DataFrame(packet['prv_candidates'])
            return pd.concat([df_1, df_2], ignore_index=True)
        else:
            return None
    except Exception:
        return None


# +
# get_sid()
# -
def get_sid(_sid=0):

    # check input(s)
    if not isinstance(_sid, int) or _sid < 0:
        raise Exception(f'invalid input, _sid={_sid}')

    # connect to database
    _s = db_connect()
    print(f'_s={_s}, type(_s)={type(_s)}')

    # get data
    _res = db_sid(_s, _sid)
    print(f'_res={_res}')

    # disconnect from database
    db_disconnect(_s)


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s)
    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description='Get AVRO Data',
                                 formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('-s', '--sid', default=0, help="""Database id""")
    args = _p.parse_args()

    # execute
    get_sid(int(args.sid))
