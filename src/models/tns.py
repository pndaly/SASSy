#!/usr/bin/env python3


# +
# import(s)
# -
from astropy.time import Time
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import argparse
import json
import math
import pytz
import os
import sys


# +
# __doc__ string
# -
__doc__ = """
    % python3 tns.py --help
"""


# +
# function: get_iso()
# -
def get_iso():
    return Time.now().to_datetime(pytz.timezone('America/Phoenix')).isoformat()


# +
# __text__
# -
__text__ = """
    Sourced from https://wis-tns.weizman.ac.il/search ... via record(s):

    {'41314': 
        {
            'name': 'AT 2019ktf', 
            'name_link': 'https://wis-tns.weizmann.ac.il/object/2019ktf', 
            'reps': '1', 
            'reps_links': ['https://wis-tns.weizmann.ac.il/object/2019ktf/discovery-cert'], 
            'class': '', 
            'ra': '23:32:29.939', 
            'decl': '-29:33:36.66', 
            'ot_name': '', 
            'redshift': math.nan, 
            'hostname': '', 
            'host_redshift': math.nan, 
            'source_group_name': 'ATLAS', 
            'classifying_source_group_name': '', 
            'groups': 'ATLAS', 
            'internal_name': 'ATLAS19oqd', 
            'discovering_instrument_name': 'ATLAS1 - ACAM1', 
            'classifing_instrument_name': '', 
            'isTNS_AT': 'Y', 
            'public': 'Y', 
            'end_prop_period': '', 
            'spectra_count': '', 
            'discoverymag': math.nan, 
            'disc_filter_name': 'cyan-ATLAS', 
            'discoverydate': '2019-07-07 14:00:57', 
            'discoverer': 'ATLAS_Bot1', 
            'remarks': '', 
            'sources': '', 
            'bibcode': '', 
            'ext_catalogs': ''
        }
    }

    Database schema:
    DROP TABLE IF EXISTS tns;
    CREATE TABLE tns (
        id serial PRIMARY KEY,
        tns_id INTEGER,
        tns_name VARCHAR(128) NOT NULL,
        tns_link VARCHAR(128),
        ra double precision,
        dec double precision,
        redshift double precision,
        discovery_date TIMESTAMP,
        discovery_mag double precision,
        discovery_instrument VARCHAR(128),
        filter_name VARCHAR(32),
        tns_class VARCHAR(128),
        host VARCHAR(128),
        host_z double precision,
        source_group VARCHAR(128),
        alias VARCHAR(128),
        certificate VARCHAR(128)
    );
    EOF

"""


# +
# constant(s)
# -
DB_VARCHAR_32 = 32
DB_VARCHAR_128 = 128
FALSE_VALUES = ['false', 'f', '0']
SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_PORT = os.getenv('SASSY_DB_PORT', None)
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SORT_ORDER = ['asc', 'desc', 'ascending', 'descending']
SORT_VALUE = ['id', 'tns_id', 'tns_name', 'tns_link', 'ra', 'dec', 'redshift', 'discovery_date', 'discovery_mag',
              'discovery_instrument', 'filter_name', 'tns_class', 'host', 'host_z', 'source_group',
              'alias', 'certificate']
TRUE_VALUES = ['true', 't', '1']


# +
# initialize sqlalchemy (deferred)
# -
db = SQLAlchemy()


# +
# class: TnsRecord(), inherits from db.Model
# -
# noinspection PyUnresolvedReferences
class TnsRecord(db.Model):

    # +
    # member variable(s)
    # -

    # define table name
    __tablename__ = 'tns'

    id = db.Column(db.Integer, primary_key=True)
    tns_id = db.Column(db.Integer)
    tns_name = db.Column(db.String(DB_VARCHAR_128), nullable=False, default='')
    tns_link = db.Column(db.String(DB_VARCHAR_128), default='')
    ra = db.Column(db.Float, default=math.nan, index=True)
    dec = db.Column(db.Float, default=math.nan, index=True)
    redshift = db.Column(db.Float, default=math.nan)
    discovery_date = db.Column(db.DateTime, default=get_iso())
    discovery_mag = db.Column(db.Float, default=math.nan)
    discovery_instrument = db.Column(db.String(DB_VARCHAR_128), default='')
    filter_name = db.Column(db.String(DB_VARCHAR_32), default='')
    tns_class = db.Column(db.String(DB_VARCHAR_128), default='')
    host = db.Column(db.String(DB_VARCHAR_128), default='')
    host_z = db.Column(db.Float, default=math.nan)
    source_group = db.Column(db.String(DB_VARCHAR_128), default='')
    alias = db.Column(db.String(DB_VARCHAR_128), default='')
    certificate = db.Column(db.String(DB_VARCHAR_128), default='')

    @property
    def pretty_serialized(self):
        return json.dumps(self.serialized(), indent=2)

    def serialized(self):
        return {
            'id': self.id,
            'tns_id': int(self.tns_id),
            'tns_name': self.tns_name,
            'tns_link': self.tns_link,
            'ra': float(self.ra),
            'dec': float(self.dec),
            'redshift': float(self.redshift),
            'discovery_date': self.discovery_date,
            'discovery_mag': float(self.discovery_mag),
            'discovery_instrument': self.discovery_instrument,
            'filter_name': self.filter_name,
            'tns_class': self.tns_class,
            'host': self.host,
            'host_z': float(self.host_z),
            'source_group': self.source_group,
            'alias': self.alias,
            'certificate': self.certificate
        }

    # +
    # (overload) method: __str__()
    # -
    def __str__(self):
        return self.id

    # +
    # (static) method: serialize_list()
    # -
    @staticmethod
    def serialize_list(m_records):
        return [_a.serialized() for _a in m_records]


# +
# function: tns_filters() alphabetically
# -
def tns_filters(query, request_args):

    # return records with alias like value (API: ?alias=GW20190817_051234)
    if request_args.get('alias'):
        query = query.filter(TnsRecord.alias.ilike(f"%{request_args['alias']}%"))

    # return records with an dec >= value in degrees (API: ?dec__gte=20.0)
    if request_args.get('dec__gte'):
        query = query.filter(TnsRecord.dec >= float(request_args['dec__gte']))

    # return records with an dec <= value in degrees (API: ?dec__lte=20.0)
    if request_args.get('dec__lte'):
        query = query.filter(TnsRecord.dec <= float(request_args['dec__lte']))

    # return records with discovery_date like value (API: ?discovery_date=2019-07-15)
    if request_args.get('discovery_date'):
        _date = datetime.strptime(request_args['discovery_date'], '%Y-%m-%d')
        query = query.filter(TnsRecord.discovery_date >= _date)

    # return records with discovery_instrument like value (API: ?discovery_instrument=ATLAS)
    if request_args.get('discovery_instrument'):
        query = query.filter(TnsRecord.discovery_instrument.ilike(f"%{request_args['discovery_instrument']}%"))

    # return records with discovery_mag >= value (API: ?discovery_mag__gte=15.0)
    if request_args.get('discovery_mag__gte'):
        query = query.filter(TnsRecord.discovery_mag >= request_args['discovery_mag__gte'])

    # return records with discovery_mag <= value (API: ?discovery_mag__lte=15.0)
    if request_args.get('discovery_mag__lte'):
        query = query.filter(TnsRecord.discovery_mag <= request_args['discovery_mag__lte'])

    # return records with filter_name like value (API: ?filter_name=U)
    if request_args.get('filter_name'):
        query = query.filter(TnsRecord.filter_name.ilike(f"%{request_args['filter_name']}%"))

    # return records with host like value (API: ?host=NGC1365)
    if request_args.get('host'):
        query = query.filter(TnsRecord.host.ilike(f"%{request_args['host']}%"))

    # return records with host_z >= value (API: ?host_z=1.0)
    if request_args.get('host_z__gte'):
        query = query.filter(TnsRecord.host_z >= request_args['host_z__gte'])

    # return records with host_z <= value (API: ?host_z=1.0)
    if request_args.get('host_z__lte'):
        query = query.filter(TnsRecord.host_z <= request_args['host_z__lte'])

    # return records with id = value (API: ?id=20)
    if request_args.get('id'):
        query = query.filter(TnsRecord.id == int(request_args['id']))

    # return records with id >= value (API: ?id__gte=20)
    if request_args.get('id__gte'):
        query = query.filter(TnsRecord.id >= int(request_args['id__gte']))

    # return records with id <= value (API: ?id__lte=20)
    if request_args.get('id__lte'):
        query = query.filter(TnsRecord.id <= int(request_args['id__lte']))

    # return records with an ra >= value in degrees (API: ?ra__gte=12.0)
    if request_args.get('ra__gte'):
        query = query.filter(TnsRecord.ra >= float(request_args['ra__gte']))

    # return records with an ra <= value in degrees (API: ?ra__lte=12.0)
    if request_args.get('ra__lte'):
        query = query.filter(TnsRecord.ra <= float(request_args['ra__lte']))

    # return records with an redshift >= value in degrees (API: ?redshift__gte=1.0)
    if request_args.get('redshift__gte'):
        query = query.filter(TnsRecord.redshift >= float(request_args['redshift__gte']))

    # return records with an redshift <= value in degrees (API: ?redshift__lte=1.0)
    if request_args.get('redshift__lte'):
        query = query.filter(TnsRecord.redshift <= float(request_args['redshift__lte']))

    # return records with source_group like value (API: ?source_group=ZTF)
    if request_args.get('source_group'):
        query = query.filter(TnsRecord.source_group.ilike(f"%{request_args['source_group']}%"))

    # return records with tns_class like value (API: ?tns_class=ZTF)
    if request_args.get('tns_class'):
        query = query.filter(TnsRecord.tns_class.ilike(f"%{request_args['tns_class']}%"))

    # return records with tns_id = value (API: ?tns_id=20)
    if request_args.get('tns_id'):
        query = query.filter(TnsRecord.tns_id == int(request_args['tns_id']))

    # return records with tns_id >= value (API: ?tns_id__gte=20)
    if request_args.get('tns_id__gte'):
        query = query.filter(TnsRecord.tns_id >= int(request_args['tns_id__gte']))

    # return records with tns_id <= value (API: ?tns_id__lte=20)
    if request_args.get('tns_id__lte'):
        query = query.filter(TnsRecord.tns_id <= int(request_args['tns_id__lte']))

    # return records with tns_link like value (API: ?tns_link=2019xyz)
    if request_args.get('tns_link'):
        query = query.filter(TnsRecord.tns_link.ilike(f"%{request_args['tns_link']}%"))

    # return records with tns_name like value (API: ?tns_name=2019xyz)
    if request_args.get('tns_name'):
        query = query.filter(TnsRecord.tns_name.ilike(f"%{request_args['tns_name']}%"))

    # sort results
    sort_value = request_args.get('sort_value', SORT_VALUE[0]).lower()
    sort_order = request_args.get('sort_order', SORT_ORDER[0]).lower()
    if sort_order in SORT_ORDER:
        if sort_order.startswith(SORT_ORDER[0]):
            query = query.order_by(getattr(TnsRecord, sort_value).asc())
        elif sort_order.startswith(SORT_ORDER[1]):
            query = query.order_by(getattr(TnsRecord, sort_value).desc())

    # return query
    return query


# +
# function: tns_get_text()
# -
def tns_get_text():
    return __text__


# +
# function: tns_cli_db()
# -
# noinspection PyBroadException
def tns_cli_db(iargs=None):

    # check input(s)
    if iargs is None:
        raise Exception('Invalid arguments')

    # if --text is present, describe of the database
    if iargs.text:
        print(tns_get_text())
        return

    # set default(s)
    request_args = {}

    # get input(s) alphabetically
    if iargs.alias:
        request_args['alias'] = f'{iargs.alias}'
    if iargs.dec__gte:
        request_args['dec__gte'] = f'{iargs.dec__gte}'
    if iargs.dec__lte:
        request_args['dec__lte'] = f'{iargs.dec__lte}'
    if iargs.discovery_date:
        request_args['discovery_date'] = f'{iargs.discovery_date}'
    if iargs.discovery_instrument:
        request_args['discovery_instrument'] = f'{iargs.discovery_instrument}'
    if iargs.discovery_mag__gte:
        request_args['discovery_mag__gte'] = f'{iargs.discovery_mag__gte}'
    if iargs.discovery_mag__lte:
        request_args['discovery_mag__lte'] = f'{iargs.discovery_mag__lte}'
    if iargs.filter_name:
        request_args['filter_name'] = f'{iargs.filter_name}'
    if iargs.host:
        request_args['host'] = f'{iargs.host}'
    if iargs.host_z__gte:
        request_args['host_z__gte'] = f'{iargs.host_z__gte}'
    if iargs.host_z__lte:
        request_args['host_z__lte'] = f'{iargs.host_z__lte}'
    if iargs.id:
        request_args['id'] = f'{iargs.id}'
    if iargs.id__gte:
        request_args['id__gte'] = f'{iargs.id__gte}'
    if iargs.id__lte:
        request_args['id__lte'] = f'{iargs.id__lte}'
    if iargs.ra__gte:
        request_args['ra__gte'] = f'{iargs.ra__gte}'
    if iargs.ra__lte:
        request_args['ra__lte'] = f'{iargs.ra__lte}'
    if iargs.redshift__gte:
        request_args['redshift__gte'] = f'{iargs.redshift__gte}'
    if iargs.redshift__lte:
        request_args['redshift__lte'] = f'{iargs.redshift__lte}'
    if iargs.sort_order:
        request_args['sort_order'] = f'{iargs.sort_order}'
    if iargs.sort_value:
        request_args['sort_value'] = f'{iargs.sort_value}'
    if iargs.source_group:
        request_args['source_group'] = f'{iargs.source_group}'
    if iargs.tns_class:
        request_args['tns_class'] = f'{iargs.tns_class}'
    if iargs.tns_id:
        request_args['tns_id'] = f'{iargs.tns_id}'
    if iargs.tns_id__gte:
        request_args['tns_id__gte'] = f'{iargs.tns_id__gte}'
    if iargs.tns_id__lte:
        request_args['tns_id__lte'] = f'{iargs.tns_id__lte}'
    if iargs.tns_name:
        request_args['tns_name'] = f'{iargs.tns_name}'
    if iargs.tns_link:
        request_args['tns_link'] = f'{iargs.tns_link}'

    # set up access to database
    try:
        if iargs.verbose:
            print(f'connecting via postgresql+psycopg2://'
                  f'{SASSY_DB_USER}:{SASSY_DB_PASS}@{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}')
        engine = create_engine(
            f'postgresql+psycopg2://{SASSY_DB_USER}:{SASSY_DB_PASS}@{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}')
        if iargs.verbose:
            print(f'engine = {engine}')
        get_session = sessionmaker(bind=engine)
        if iargs.verbose:
            print(f'Session = {get_session}')
        session = get_session()
        if iargs.verbose:
            print(f'session = {session}')
    except Exception as e:
        raise Exception(f'Failed to connect to database. error={e}')

    # execute query
    try:
        if iargs.verbose:
            print(f'executing query')
        query = session.query(TnsRecord)
        if iargs.verbose:
            print(f'query = {query}')
        query = tns_filters(query, request_args)
        if iargs.verbose:
            print(f'query = {query}')
    except Exception as e:
        raise Exception(f'Failed to execute query. error={e}')

    # dump output to file
    if isinstance(iargs.output, str) and iargs.output.strip() != '':
        try:
            with open(iargs.output, 'w') as _wf:
                _wf.write(f'#id,tns_id,tns_name,ra,dec,redshift,date,mag,instrument,filter,class,host,'
                          f'host_z,source,alias,certificate\n')
                for _e in TnsRecord.serialize_list(query.all()):
                    _wf.write(f"{_e['id']},{_e['tns_id']},{_e['tns_name']},{_e['ra']},{_e['dec']},{_e['redshift']},"
                              f"{_e['discovery_date']},{_e['discovery_mag']},{_e['discovery_instrument']},"
                              f"{_e['filter_name']},{_e['tns_class']},{_e['host']},{_e['host_z']},"
                              f"{_e['source_group']},{_e['alias']},{_e['certificate']}\n")
        except Exception:
            pass

    # dump output to screen
    else:
        print(f'#id,tns_id,tns_name,ra,dec,redshift,date,mag,instrument,filter,class,host,'
              f'host_z,source,alias,certificate')
        for _e in TnsRecord.serialize_list(query.all()):
            print(f"{_e['id']},{_e['tns_id']},{_e['tns_name']},{_e['ra']},{_e['dec']},{_e['redshift']},"
                  f"{_e['discovery_date']},{_e['discovery_mag']},{_e['discovery_instrument']},{_e['filter_name']},"
                  f"{_e['tns_class']},{_e['host']},{_e['host_z']},{_e['source_group']}",
                  f"{_e['alias']},{_e['certificate']}")


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s) alphabetically
    _p = argparse.ArgumentParser(description=f'Query TNS database', formatter_class=argparse.RawTextHelpFormatter)

    _p.add_argument(f'--alias', help=f'Alternate name <str>')
    _p.add_argument(f'--dec__gte', help=f'Dec >= <float>')
    _p.add_argument(f'--dec__lte', help=f'Dec <= <float>')
    _p.add_argument(f'--discovery_date', help=f'Discovery date <str>')
    _p.add_argument(f'--discovery_instrument', help=f'Discovery instrument <str>')
    _p.add_argument(f'--discovery_mag__gte', help=f'Discovery magnitude >= <float>')
    _p.add_argument(f'--discovery_mag__lte', help=f'Discovery magnitude <= <float>')
    _p.add_argument(f'--filter_name', help=f'Filter name <str>')
    _p.add_argument(f'--host', help=f'Host object <str>')
    _p.add_argument(f'--host_z__gte', help=f'Host object redshift >= <float>')
    _p.add_argument(f'--host_z__lte', help=f'Host object redshift <= <float>')
    _p.add_argument(f'--id', help=f'Database id = <int>')
    _p.add_argument(f'--id__gte', help=f'Database id >= <int>')
    _p.add_argument(f'--id__lte', help=f'Database id <= <int>')
    _p.add_argument(f'--ra__gte', help=f'RA >= <float>')
    _p.add_argument(f'--ra__lte', help=f'RA <= <float>')
    _p.add_argument(f'--redshift__gte', help=f'Redshift >= <float>')
    _p.add_argument(f'--redshift__lte', help=f'Redshift <= <float>')
    _p.add_argument(f'--source_group', help=f'Source group <str>')
    _p.add_argument(f'--tns_class', help=f'Transient type <str>')
    _p.add_argument(f'--tns_id', help=f'TNS id = <int>')
    _p.add_argument(f'--tns_id__gte', help=f'TNS id >= <int>')
    _p.add_argument(f'--tns_id__lte', help=f'TNS id <= <int>')
    _p.add_argument(f'--tns_name', help=f'TNS name <str>')
    _p.add_argument(f'--tns_link', help=f'TNS link <str>')

    _p.add_argument(f'--output', default='', help=f'Output file <str>')
    _p.add_argument(f'--sort_order', help=f"Sort order, one of {SORT_ORDER}")
    _p.add_argument(f'--sort_value', help=f"Sort value, one of {SORT_VALUE}")
    _p.add_argument(f'--text', default=False, action='store_true', help=f'if present, describe the database')
    _p.add_argument(f'--verbose', default=False, action='store_true', help=f'if present, produce more verbose output')
    args = _p.parse_args()

    # execute
    if args:
        tns_cli_db(args)
    else:
        raise Exception(f'Insufficient command line arguments specified\nUse: python {sys.argv[0]} --help')
