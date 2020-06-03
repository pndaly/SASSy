#!/usr/bin/env python3


# +
# import(s)
# -
from astropy.coordinates import Angle
from astropy.coordinates import SkyCoord
from datetime import datetime, timedelta
from src.models.tns_q3c import TnsQ3cRecord
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import argparse
import hashlib
import json
import math
import os
import sys


# +
# __doc__ string
# -
__doc__ = """
    % python3 tns_q3c_read.py --help
"""


# +
# constant(s)
# -
TNS_Q3C_CATALOG_FILE = os.path.abspath(os.path.expanduser('TnsQ3c.ans'))

SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PORT = os.getenv('SASSY_DB_PORT', None)


# +
# function: ra_to_decimal()
# -
# noinspection PyBroadException,PyBroadException
def ra_from_angle(_ra=''):
    if not isinstance(_ra, str) or _ra.strip() == '':
        return math.nan
    if not _ra.lower().endswith('hours'):
        _ra = f'{_ra} hours'
    try:
        return float(Angle(_ra).degree)
    except Exception:
        return math.nan


# noinspection PyBroadException,PyBroadException
def dec_from_angle(_dec=''):
    if not isinstance(_dec, str) or _dec.strip() == '':
        return math.nan
    if not _dec.lower().endswith('degrees'):
        _dec = f'{_dec} degrees'
    try:
        return float(Angle(_dec).degree)
    except Exception:
        return math.nan


def coord_from_angle(_ra='', _dec=''):
    if not isinstance(_ra, str) or _ra.strip() == '':
        return math.nan, math.nan
    if not isinstance(_dec, str) or _dec.strip() == '':
        return math.nan, math.nan
    return ra_from_angle(_ra), dec_from_angle(_dec)


# noinspection PyUnresolvedReferences
def coord_from_sky(_ra='', _dec=''):
    if not isinstance(_ra, str) or _ra.strip() == '':
        return math.nan, math.nan
    if not isinstance(_dec, str) or _dec.strip() == '':
        return math.nan, math.nan
    _coord = SkyCoord(f'{_ra} {_dec}', unit=(u.hourangle, u.deg))
    return _coord.ra.degree, _coord.dec.degree


def get_date_time(offset=0):
    """ return local time string like YYYY-MM-DDThh:mm:ss.ssssss with/without offset """
    return (datetime.now() + timedelta(days=offset)).isoformat()


def get_date_utctime(offset=0):
    """ return UTC time string like YYYY-MM-DDThh:mm:ss.ssssss with/without offset """
    return (datetime.utcnow() + timedelta(days=offset)).isoformat()


def get_unique_hash():
    _date = get_date_time(0)
    return hashlib.sha256(_date.encode('utf-8')).hexdigest()


# +
# function: read_tns_q3c()
# -
# noinspection PyBroadException
def read_tns_q3c(_file=''):

    # check input(s)
    if not isinstance(_file, str) or _file.strip() == '' or \
            not os.path.isfile(os.path.abspath(os.path.expanduser(_file))):
        raise Exception(f'invalid input, _file={_file}')

    # get data
    _all_lines = None
    _file = os.path.abspath(os.path.expanduser(_file))
    with open(f'{_file}', 'r') as _fd:
        _all_lines = _fd.readlines()
    if _all_lines is None:
        raise Exception(f'Failed to read {_file}')

    # noinspection PyBroadException
    session = None
    try:
        # connect to database
        engine = create_engine(f'postgresql+psycopg2://{SASSY_DB_USER}:{SASSY_DB_PASS}@'
                               f'{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}')
        get_session = sessionmaker(bind=engine)
        session = get_session()
    except Exception as e:
        raise Exception(f'Failed to connect to database, error={e}')

    # create records
    _icount = 0
    for _e in _all_lines:

        _json = json.loads(f'{_e.strip()}')
        _dict = dict(_json)

        for _k, _v in _dict.items():

            # get data from dictionary
            # {"41302": {"name": "AT 2019kst", "name_link": "https://wis-tns.weizmann.ac.il/object/2019kst",
            # "reps": "1", "reps_links": ["https://wis-tns.weizmann.ac.il/object/2019kst/discovery-cert"], "class": "",
            # "ra": "17:08:26.793", "decl": "+26:07:08.06", "ot_name": "", "redshift": "nan", "hostname": "",
            # "host_redshift": "nan", "source_group_name": "Pan-STARRS1", "classifying_source_group_name": "",
            # "groups": "Pan-STARRS1", "internal_name": "PS19dmh", "discovering_instrument_name": "PS1 - GPC1",
            # "classifing_instrument_name": "", "isTNS_AT": "Y", "public": "Y", "end_prop_period": "",
            # "spectra_count": "", "discoverymag": "nan", "disc_filter_name": "w-PS1",
            # "discoverydate": "2019-07-05 10:06:14", "discoverer": "PS1_Bot1", "remarks": "",
            # "sources": "", "bibcode": ""}}
            _tns_id = -1
            try:
                _tns_id = int(f'{_k}')
            except Exception:
                _tns_id = -1

            if _tns_id > 0:

                # does record already exist?
                _rec = None
                try:
                    _rec = session.query(TnsQ3cRecord).filter_by(tns_id=_tns_id).first()
                except Exception:
                    _rec = None
                if _rec is not None:
                    continue

                # get rest of data
                _tns_name = _dict[_k].get('name', '').strip()
                _tns_link = _dict[_k].get('name_link', '').strip()
                _tns_certificate = f"{_tns_link}/discovery-cert"
                _tns_class = _dict[_k].get('class', '').strip()
                _tns_ra = _dict[_k].get('ra', '').strip()
                _tns_dec = _dict[_k].get('decl', '').strip()
                _tns_ot_name = _dict[_k].get('ot_name', '').strip()
                _tns_redshift = _dict[_k].get('redshift', math.nan)
                _tns_hostname = _dict[_k].get('hostname', '').strip()
                _tns_host_redshift = _dict[_k].get('host_redshift', math.nan)
                _tns_source_group_name = _dict[_k].get('source_group_name', '').strip()
                _tns_classifying_source_group_name = _dict[_k].get('classifying_source_group_name', '').strip()
                _tns_groups = _dict[_k].get('groups', '').strip()
                _tns_internal_name = _dict[_k].get('internal_name', '').strip()
                _tns_discovering_instrument_name = _dict[_k].get('discovering_instrument_name', '').strip()
                _tns_classifing_instrument_instrument = _dict[_k].get('classifing_instrument_name', '').strip()
                _tns_isTNS_AT = _dict[_k].get('isTNS_AT', '').strip()
                _tns_public = _dict[_k].get('public', '').strip()
                _tns_end_prop_period = _dict[_k].get('end_prop_period', '').strip()
                _tns_spectra_count = _dict[_k].get('spectra_count', '').strip()
                _tns_discoverymag = _dict[_k].get('discoverymag', math.nan)
                _tns_disc_filter_name = _dict[_k].get('disc_filter_name', '').strip()
                _tns_discoverydate = _dict[_k].get('discoverydate', '').strip()
                _tns_discoverer = _dict[_k].get('discoverer', '').strip()
                _tns_remarks = _dict[_k].get('remarks', '').strip()
                _tns_sources = _dict[_k].get('sources', '').strip()
                _tns_bibcode = _dict[_k].get('bibcode', '').strip()

                # conversion(s)
                _ra, _dec = math.nan, math.nan
                if _tns_ra != '' and _tns_dec != '':
                    try:
                        _ra, _dec = coord_from_angle(_tns_ra, _tns_dec)
                    except Exception:
                        _ra, _dec = math.nan, math.nan

                # create record
                _tns_q3c = TnsQ3cRecord(tns_id=_tns_id, tns_name=_tns_name, tns_link=_tns_link, ra=_ra, dec=_dec,
                                        redshift=_tns_redshift, discovery_date=_tns_discoverydate,
                                        discovery_mag=_tns_discoverymag,
                                        discovery_instrument=_tns_discovering_instrument_name,
                                        filter_name=_tns_disc_filter_name, tns_class=_tns_class, host=_tns_hostname,
                                        host_z=_tns_host_redshift, source_group=_tns_source_group_name,
                                        alias=_tns_internal_name, certificate=_tns_certificate)

                # update database with results
                if _tns_q3c is not None and '0000-00-00' not in _tns_discoverydate:
                    try:
                        print(f"Inserting record = {_tns_q3c.serialized()}")
                        session.add(_tns_q3c)
                        session.commit()
                        print(f"Inserted record {_tns_id}")
                    except Exception as e:
                        print(f"Failed inserting record {_tns_id}, error={e}")
                        session.rollback()
                        session.commit()

    # return
    session.close()
    session.close_all()


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s)
    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description='Populate TNS_Q3C database from file',
                                 formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('-f', '--file', default=TNS_Q3C_CATALOG_FILE, help="""Input file [%(default)s]""")
    args = _p.parse_args()

    # execute
    if args.file:
        read_tns_q3c(args.file)
    else:
        print(f'Use: python3 {sys.argv[0]} --help')
