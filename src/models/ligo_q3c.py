#!/usr/bin/env python3


# +
# import(s)
# -
from astropy.coordinates import SkyCoord
from astropy.time import Time
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

import argparse
# import gzip
import json
import math
import pytz
import os
import sys
# import urllib.request


# +
# __doc__ string
# -
__doc__ = """
    % python3 ligo_q3c.py --help
"""


# +
# (hidden) function: _get_iso()
# -
def _get_iso():
    return Time.now().to_datetime(pytz.timezone('America/Phoenix')).isoformat()


# +
# (hidden) function: _get_astropy_coords()
# -
# noinspection PyBroadException
def _get_astropy_coords(_oname=''):
    try:
        _obj = SkyCoord.from_name(_oname)
        return _obj.ra.value, _obj.dec.value
    except Exception:
        return math.nan, math.nan


# +
# __text__
# -
__text__ = """
    Sourced from https://wis-tns.weizman.ac.il/ligo/events via JSON record(s):

    "<element>": {
        "name": "<element>", 
        "name_prefix": "AT", 
        "ra": "116.669208", 
        "dec": "17.570219", 
        "type": "NULL", 
        "discoverydate": "2019-05-30 17:25:26", 
        "discoverymag": "18.08", 
        "filter": "Gaia-G", 
        "source_group": "GaiaAlerts", 
        "probability": "0.988377", 
        "sigma": "3"
    } 

    Database schema:

    DROP TABLE IF EXISTS ligo_q3c;
    CREATE TABLE ligo_q3c (
        id serial PRIMARY KEY,
        name VARCHAR(32) NOT NULL UNIQUE,
        name_prefix VARCHAR(16),
        name_suffix VARCHAR(16),
        ra double precision,
        dec double precision,
        transient_type VARCHAR(64),
        discovery_date TIMESTAMP,
        discovery_mag double precision,
        filter_name VARCHAR(32),
        source_group VARCHAR(64),
        probability double precision,
        sigma double precision,
        gw_aka VARCHAR(64),
        gw_date TIMESTAMP,
        gw_event VARCHAR(32),
        before BOOLEAN NOT NULL DEFAULT False
    );

    CREATE EXTENSION q3c;
    CREATE INDEX ON ligo_q3c (q3c_ang2ipix(ra, dec));
    CLUSTER ligo_q3c_q3c_ang2ipix_idx ON ligo_q3c;
    ANALYZE VERBOSE ligo_q3c;

"""


# +
# constant(s)
# -
DB_VARCHAR_16 = 16
DB_VARCHAR_32 = 32
DB_VARCHAR_64 = 64
FALSE_VALUES = ['false', 'f', '0']
LIGO_Q3C_GZIP_URL = 'https://wis-tns.weizman.ac.il/ligo/events'
SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_PORT = os.getenv('SASSY_DB_PORT', None)
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SORT_ORDER = ['asc', 'desc', 'ascending', 'descending']
SORT_VALUE = ['id', 'name', 'name_prefix', 'name_suffix', 'ra', 'dec', 'transient_type', 'discovery_date',
              'discovery_mag', 'filter_name', 'source_group', 'probability', 'sigma',
              'gw_aka', 'gw_date', 'gw_event', 'before']
TRUE_VALUES = ['true', 't', '1']


# +
# initialize sqlalchemy (deferred)
# -
db = SQLAlchemy()


# +
# class: LigoQ3cRecord(), inherits from db.Model
# -
# noinspection PyUnresolvedReferences
class LigoQ3cRecord(db.Model):

    # +
    # member variable(s)
    # -

    # define table name
    __tablename__ = 'ligo_q3c'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(DB_VARCHAR_32), nullable=False, unique=True, default='')
    name_prefix = db.Column(db.String(DB_VARCHAR_16), default='')
    name_suffix = db.Column(db.String(DB_VARCHAR_16), default='')
    ra = db.Column(db.Float, default=math.nan, index=True)
    dec = db.Column(db.Float, default=math.nan, index=True)
    transient_type = db.Column(db.String(DB_VARCHAR_64), default='')
    discovery_date = db.Column(db.DateTime, default=_get_iso())
    discovery_mag = db.Column(db.Float, default=math.nan)
    filter_name = db.Column(db.String(DB_VARCHAR_32), default='')
    source_group = db.Column(db.String(DB_VARCHAR_64), default='')
    probability = db.Column(db.Float, default=math.nan)
    sigma = db.Column(db.Float, default=math.nan)
    gw_aka = db.Column(db.String(DB_VARCHAR_64), default='')
    gw_date = db.Column(db.DateTime, default=_get_iso())
    gw_event = db.Column(db.String(DB_VARCHAR_32), default='')
    before = db.Column(db.Boolean, default=False, nullable=False)

    @property
    def pretty_serialized(self):
        return json.dumps(self.serialized(), indent=2)

    def serialized(self):
        return {
            'id': self.id,
            'name': self.name,
            'name_prefix': self.name_prefix,
            'name_suffix': self.name_suffix,
            'ra': float(self.ra),
            'dec': float(self.dec),
            'transient_type': self.transient_type,
            'discovery_date': self.discovery_date,
            'discovery_mag': float(self.discovery_mag),
            'filter_name': self.filter_name,
            'source_group': self.source_group,
            'probability': float(self.probability),
            'sigma': float(self.sigma),
            'gw_aka': self.gw_aka,
            'gw_date': self.gw_date,
            'gw_event': self.gw_event,
            'before': bool(self.before)
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
# function: ligo_q3c_filters() alphabetically
# -
# noinspection PyBroadException
def ligo_q3c_filters(query, request_args):

    # return records within astrocone search (API: ?cone=M51,25.0)
    if request_args.get('astrocone'):
        try:
            _nam, _rad = request_args['astrocone'].split(',')
            _ra, _dec = _get_astropy_coords(_nam.strip().upper())
            query = query.filter(func.q3c_radial_query(LigoQ3cRecord.ra, LigoQ3cRecord.dec, _ra, _dec, _rad))
        except Exception:
            pass

    # return records within cone search (API: ?cone=23.5,29.2,5.0)
    if request_args.get('cone'):
        try:
            _ra, _dec, _rad = request_args['cone'].split(',')
            query = query.filter(func.q3c_radial_query(LigoQ3cRecord.ra, LigoQ3cRecord.dec, _ra, _dec, _rad))
        except Exception:
            pass

    # return records within ellipse search (API: ?ellipse=202.1,47.2,5.0,0.5,25.0)
    if request_args.get('ellipse'):
        try:
            _ra, _dec, _maj, _rat, _pos = request_args['ellipse'].split(',')
            query = query.filter(
                func.q3c_ellipse_query(LigoQ3cRecord.ra, LigoQ3cRecord.dec, _ra, _dec, _maj, _rat, _pos))
        except Exception:
            pass

    # return records with before = boolean (API: ?before=True)
    if request_args.get('before'):
        query = query.filter(LigoQ3cRecord.before == request_args.get('before').lower() in TRUE_VALUES)

    # return records with an dec >= value in degrees (API: ?dec__gte=20.0)
    if request_args.get('dec__gte'):
        query = query.filter(LigoQ3cRecord.dec >= float(request_args['dec__gte']))

    # return records with an dec <= value in degrees (API: ?dec__lte=20.0)
    if request_args.get('dec__lte'):
        query = query.filter(LigoQ3cRecord.dec <= float(request_args['dec__lte']))

    # return records with discovery_date like value (API: ?discovery_date=2019-07-15)
    if request_args.get('discovery_date'):
        _date = datetime.strptime(request_args['discovery_date'], '%Y-%m-%d')
        query = query.filter(LigoQ3cRecord.discovery_date >= _date)

    # return records with discovery_mag >= value (API: ?discovery_mag__gte=15.0)
    if request_args.get('discovery_mag__gte'):
        query = query.filter(LigoQ3cRecord.discovery_mag >= request_args['discovery_mag__gte'])

    # return records with discovery_mag <= value (API: ?discovery_mag__lte=15.0)
    if request_args.get('discovery_mag__lte'):
        query = query.filter(LigoQ3cRecord.discovery_mag <= request_args['discovery_mag__lte'])

    # return records with filter_name like value (API: ?filter_name=U)
    if request_args.get('filter_name'):
        query = query.filter(LigoQ3cRecord.filter_name.ilike(f"%{request_args['filter_name']}%"))

    # return records with gw_aka like value (API: ?gw_aka=GW20190817_051234)
    if request_args.get('gw_aka'):
        query = query.filter(LigoQ3cRecord.gw_aka.ilike(f"%{request_args['gw_aka']}%"))

    # return records with gw_date like value (API: ?gw_date=2019-07-15)
    if request_args.get('gw_date'):
        _date = datetime.strptime(request_args['gw_date'], '%Y-%m-%d')
        query = query.filter(LigoQ3cRecord.discovery_date >= _date)

    # return records with gw_event like value (API: ?gw_event=G339873)
    if request_args.get('gw_event'):
        query = query.filter(LigoQ3cRecord.gw_event.ilike(f"%{request_args['gw_event']}%"))

    # return records with id = value (API: ?id=20)
    if request_args.get('id'):
        query = query.filter(LigoQ3cRecord.id == int(request_args['id']))

    # return records with id >= value (API: ?id__gte=20)
    if request_args.get('id__gte'):
        query = query.filter(LigoQ3cRecord.id >= int(request_args['id__gte']))

    # return records with id <= value (API: ?id__lte=20)
    if request_args.get('id__lte'):
        query = query.filter(LigoQ3cRecord.id <= int(request_args['id__lte']))

    # return records with name like value (API: ?name=2019xyz)
    if request_args.get('name'):
        query = query.filter(LigoQ3cRecord.name.ilike(f"%{request_args['name']}%"))

    # return records with name_prefix like value (API: ?name_prefix=SN)
    if request_args.get('name_prefix'):
        query = query.filter(LigoQ3cRecord.name_prefix.ilike(f"%{request_args['name_prefix']}%"))

    # return records with name_suffix like value (API: ?name_suffix=xyz)
    if request_args.get('name_suffix'):
        query = query.filter(LigoQ3cRecord.name_suffix.ilike(f"%{request_args['name_suffix']}%"))

    # return records with a probability >= value (API: ?probability__gte=0.0)
    if request_args.get('probability__gte'):
        query = query.filter(LigoQ3cRecord.probability >= float(request_args['probability__gte']))

    # return records with a position angle <= value (API: ?probability__lte=1.0)
    if request_args.get('probability__lte'):
        query = query.filter(LigoQ3cRecord.probability <= float(request_args['probability__lte']))

    # return records with an ra >= value in degrees (API: ?ra__gte=12.0)
    if request_args.get('ra__gte'):
        query = query.filter(LigoQ3cRecord.ra >= float(request_args['ra__gte']))

    # return records with an ra <= value in degrees (API: ?ra__lte=12.0)
    if request_args.get('ra__lte'):
        query = query.filter(LigoQ3cRecord.ra <= float(request_args['ra__lte']))

    # return records with an sigma >= value in degrees (API: ?sigma__gte=12.0)
    if request_args.get('sigma__gte'):
        query = query.filter(LigoQ3cRecord.sigma >= float(request_args['sigma__gte']))

    # return records with an sigma <= value in degrees (API: ?sigma__lte=12.0)
    if request_args.get('sigma__lte'):
        query = query.filter(LigoQ3cRecord.sigma <= float(request_args['sigma__lte']))

    # return records with source_group like value (API: ?source_group=ZTF)
    if request_args.get('source_group'):
        query = query.filter(LigoQ3cRecord.source_group.ilike(f"%{request_args['source_group']}%"))

    # return records with transient_type like value (API: ?transient_type=ZTF)
    if request_args.get('transient_type'):
        query = query.filter(LigoQ3cRecord.transient_type.ilike(f"%{request_args['transient_type']}%"))

    # sort results
    sort_value = request_args.get('sort_value', SORT_VALUE[0]).lower()
    sort_order = request_args.get('sort_order', SORT_ORDER[0]).lower()
    if sort_order in SORT_ORDER:
        if sort_order.startswith(SORT_ORDER[0]):
            query = query.order_by(getattr(LigoQ3cRecord, sort_value).asc())
        elif sort_order.startswith(SORT_ORDER[1]):
            query = query.order_by(getattr(LigoQ3cRecord, sort_value).desc())

    # return query
    return query


# +
# function: ligo_q3c_get_text()
# -
def ligo_q3c_get_text():
    return __text__


# +
# function: ligo_q3c_cli_db()
# -
# noinspection PyBroadException
def ligo_q3c_cli_db(iargs=None):

    # check input(s)
    if iargs is None:
        raise Exception('Invalid arguments')

    # if --text is present, describe of the database
    if iargs.text:
        print(ligo_q3c_get_text())
        return

    # set default(s)
    request_args = {}

    # get input(s) alphabetically
    if iargs.astrocone:
        request_args['astrocone'] = f'{iargs.astrocone}'
    if iargs.cone:
        request_args['cone'] = f'{iargs.cone}'
    if iargs.ellipse:
        request_args['ellipse'] = f'{iargs.ellipse}'

    if iargs.before:
        request_args['before'] = f'{iargs.before}'
    if iargs.dec__gte:
        request_args['dec__gte'] = f'{iargs.dec__gte}'
    if iargs.dec__lte:
        request_args['dec__lte'] = f'{iargs.dec__lte}'
    if iargs.discovery_date:
        request_args['discovery_date'] = f'{iargs.discovery_date}'
    if iargs.discovery_mag__gte:
        request_args['discovery_mag__gte'] = f'{iargs.discovery_mag__gte}'
    if iargs.discovery_mag__lte:
        request_args['discovery_mag__lte'] = f'{iargs.discovery_mag__lte}'
    if iargs.filter_name:
        request_args['filter_name'] = f'{iargs.filter_name}'
    if iargs.gw_aka:
        request_args['gw_aka'] = f'{iargs.gw_aka}'
    if iargs.gw_date:
        request_args['gw_date'] = f'{iargs.gw_date}'
    if iargs.gw_event:
        request_args['gw_event'] = f'{iargs.gw_event}'
    if iargs.id:
        request_args['id'] = f'{iargs.id}'
    if iargs.id__gte:
        request_args['id__gte'] = f'{iargs.id__gte}'
    if iargs.id__lte:
        request_args['id__lte'] = f'{iargs.id__lte}'
    if iargs.name:
        request_args['name'] = f'{iargs.name}'
    if iargs.name_prefix:
        request_args['name_prefix'] = f'{iargs.name_prefix}'
    if iargs.name_suffix:
        request_args['name_suffix'] = f'{iargs.name_suffix}'
    if iargs.probability__gte:
        request_args['probability__gte'] = f'{iargs.probability__gte}'
    if iargs.probability__lte:
        request_args['probability__lte'] = f'{iargs.probability__lte}'
    if iargs.ra__gte:
        request_args['ra__gte'] = f'{iargs.ra__gte}'
    if iargs.ra__lte:
        request_args['ra__lte'] = f'{iargs.ra__lte}'
    if iargs.sigma__gte:
        request_args['sigma__gte'] = f'{iargs.sigma__gte}'
    if iargs.sigma__lte:
        request_args['sigma__lte'] = f'{iargs.sigma__lte}'
    if iargs.sort_order:
        request_args['sort_order'] = f'{iargs.sort_order}'
    if iargs.sort_value:
        request_args['sort_value'] = f'{iargs.sort_value}'
    if iargs.source_group:
        request_args['source_group'] = f'{iargs.source_group}'
    if iargs.transient_type:
        request_args['transient_type'] = f'{iargs.transient_type}'

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
        query = session.query(LigoQ3cRecord)
        if iargs.verbose:
            print(f'query = {query}')
        query = ligo_q3c_filters(query, request_args)
        if iargs.verbose:
            print(f'query = {query}')
    except Exception as e:
        raise Exception(f'Failed to execute query. error={e}')

    # dump output to file
    if isinstance(iargs.output, str) and iargs.output.strip() != '':
        try:
            with open(iargs.output, 'w') as _wf:
                _wf.write(f'#id,name,name_prefix,name_suffix,ra,dec,type,date,mag,filter,'
                          f'source,probability,sigma,gw_aka,'
                          f'gw_date,gw_event,before\n')
                for _e in LigoQ3cRecord.serialize_list(query.all()):
                    _wf.write(f"{_e['id']},{_e['name']},{_e['name_prefix']},{_e['name_suffix']},"
                              f"{_e['ra']},{_e['dec']},{_e['transient_type']},"
                              f"{_e['discovery_date']},{_e['discovery_mag']},{_e['filter_name']},{_e['source_group']},"
                              f"{_e['probability']},{_e['sigma']},{_e['gw_aka']},{_e['gw_date']},{_e['gw_event']},"
                              f"{_e['before']}\n")
        except Exception:
            pass

    # dump output to screen
    else:
        print(f'#id,name,name_prefix,name_suffix,ra,dec,type,date,mag,filter,source,probability,'
              f'sigma,gw_aka,gw_date,gw_event,before')
        for _e in LigoQ3cRecord.serialize_list(query.all()):
            print(f"{_e['id']},{_e['name']},{_e['name_prefix']},{_e['name_suffix']},{_e['ra']},"
                  f"{_e['dec']},{_e['transient_type']},"
                  f"{_e['discovery_date']},{_e['discovery_mag']},{_e['filter_name']},{_e['source_group']},"
                  f"{_e['probability']},{_e['sigma']},{_e['gw_aka']},{_e['gw_date']},{_e['gw_event']},"
                  f"{_e['before']}")


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s) alphabetically
    _p = argparse.ArgumentParser(description=f'Query LIGO_Q3C database', formatter_class=argparse.RawTextHelpFormatter)

    _p.add_argument(f'--astrocone', help=f'Cone search <name,radius>')
    _p.add_argument(f'--cone', help=f'Cone search <ra,dec,radius>')
    _p.add_argument(f'--ellipse', help=f'Ellipse search <ra,dec,major_axis,axis_ratio,position_angle>')

    _p.add_argument(f'--before', help=f'Before transient = <boolean>')
    _p.add_argument(f'--dec__gte', help=f'Dec >= <float>')
    _p.add_argument(f'--dec__lte', help=f'Dec <= <float>')
    _p.add_argument(f'--discovery_date', help=f'Discovery date <str>')
    _p.add_argument(f'--discovery_mag__gte', help=f'Discovery magnitude >= <float>')
    _p.add_argument(f'--discovery_mag__lte', help=f'Discovery magnitude <= <float>')
    _p.add_argument(f'--filter_name', help=f'Filter name <str>')
    _p.add_argument(f'--gw_aka', help=f'GW alternate name <str>')
    _p.add_argument(f'--gw_date', help=f'GW discovery date <str>')
    _p.add_argument(f'--gw_event', help=f'GW event name <str>')
    _p.add_argument(f'--id', help=f'Database id = <int>')
    _p.add_argument(f'--id__gte', help=f'Database id >= <int>')
    _p.add_argument(f'--id__lte', help=f'Database id <= <int>')
    _p.add_argument(f'--name', help=f'Transient name <str>')
    _p.add_argument(f'--name_prefix', help=f'Transient prefix <str>')
    _p.add_argument(f'--name_suffix', help=f'Transient suffix <str>')
    _p.add_argument(f'--probability__gte', help=f'Probability >= <float>')
    _p.add_argument(f'--probability__lte', help=f'Probability <= <float>')
    _p.add_argument(f'--ra__gte', help=f'RA >= <float>')
    _p.add_argument(f'--ra__lte', help=f'RA <= <float>')
    _p.add_argument(f'--sigma__gte', help=f'Sigma >= <float>')
    _p.add_argument(f'--sigma__lte', help=f'Sigma <= <float>')
    _p.add_argument(f'--source_group', help=f'Source group <str>')
    _p.add_argument(f'--transient_type', help=f'Transient type <str>')

    _p.add_argument(f'--output', default='', help=f'Output file <str>')
    _p.add_argument(f'--sort_order', help=f"Sort order, one of {SORT_ORDER}")
    _p.add_argument(f'--sort_value', help=f"Sort value, one of {SORT_VALUE}")
    _p.add_argument(f'--text', default=False, action='store_true', help=f'if present, describe the database')
    _p.add_argument(f'--verbose', default=False, action='store_true', help=f'if present, produce more verbose output')
    args = _p.parse_args()

    # execute
    if args:
        ligo_q3c_cli_db(args)
    else:
        raise Exception(f'Insufficient command line arguments specified\nUse: python {sys.argv[0]} --help')
