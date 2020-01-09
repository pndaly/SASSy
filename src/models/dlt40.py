#!/usr/bin/env python3.7


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
import os
import pytz
import sys


# +
# __doc__ string
# -
__doc__ = """
    % python3.7 dlt40.py --help
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
Column     Name               Description
1          id                 not relevant
2          hostName           Host (galaxy) name (if known)
3          discoverer         Discoverer
4          prefix             AT or SN
5          objectname         Object name
6          redshift           Redshift
7          discMag            Discovery magnitude
8          ra                 Right Ascension [deg]
9          dec                Declination [deg]
10         sourceGroup        Discovering source group
11         discMagFilter      Filter
12         discDate           Discovery date
13         classType          Discovery class
14         hostRedshift       Redshift of host (galaxy)
15         cx                 cx coefficient (ignore)
16         cy                 cy coefficient (ignore)
17         cz                 cz coefficient (ignore)
18         htm16ID            htm16ID (ignore)
"""


# +
# constant(s)
# -
DB_VARCHAR_8 = 8
DB_VARCHAR_32 = 32
DB_VARCHAR_64 = 64
SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_PORT = int(os.getenv('SASSY_DB_PORT', -1))
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SORT_ORDER = ['asc', 'desc', 'ascending', 'descending']
SORT_VALUE = ['id', 'hostName', 'discoverer', 'prefix', 'objectname', 'redshift', 'discMag', 
              'ra', 'dec', 'sourceGroup', 'discMagFilter', 'discDate', 'classType', 'hostRedshift', 
              'cx', 'cy', 'cz', 'htm16ID']


# +
# initialize sqlalchemy (deferred)
# -
db = SQLAlchemy()


# +
# class: Dlt40Record(), inherits from db.Model
# -
# noinspection PyUnresolvedReferences
class Dlt40Record(db.Model):

    # +
    # member variable(s)
    # -

    # define table
    __tablename__ = 'dlt40'

    id = db.Column(db.Integer, primary_key=True)
    hostName = db.Column(db.String(DB_VARCHAR_64))
    discoverer = db.Column(db.String(DB_VARCHAR_64))
    prefix = db.Column(db.String(DB_VARCHAR_8))
    objectname = db.Column(db.String(DB_VARCHAR_64), nullable=False)
    redshift = db.Column(db.Float)
    discMag = db.Column(db.Float)
    ra = db.Column(db.Float)
    dec = db.Column(db.Float)
    sourceGroup = db.Column(db.String(DB_VARCHAR_64))
    discMagFilter = db.Column(db.String(DB_VARCHAR_32))
    discDate = db.Column(db.DateTime, default=get_iso())
    classType = db.Column(db.String(DB_VARCHAR_64))
    hostRedshift = db.Column(db.Float)
    cx = db.Column(db.Float)
    cy = db.Column(db.Float)
    cz = db.Column(db.Float)
    htm16ID = db.Column(db.Integer)

    @property
    def pretty_serialized(self):
        return json.dumps(self.serialized(), indent=2)

    def serialized(self):
        return {
            'id': self.id,
            'hostName': self.hostName,
            'discoverer': self.discoverer,
            'prefix': self.prefix,
            'objectname': self.objectname,
            'redshift': self.redshift,
            'discMag': self.discMag,
            'ra': self.ra,
            'dec': self.dec,
            'sourceGroup': self.sourceGroup,
            'discMagFilter': self.discMagFilter,
            'discDate': self.discDate,
            'classType': self.classType,
            'hostRedshift': self.hostRedshift,
            'cx': self.cx,
            'cy': self.cy,
            'cz': self.cz,
            'htm16ID': self.htm16ID
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
# function: dlt40_filters() alphabetically
# -
def dlt40_filters(query, request_args):

    # return records with classType name like value (API: ?classType=demo)
    if request_args.get('classType'):
        query = query.filter(Dlt40Record.classType.ilike(f"%{request_args['classType']}%"))
    # return records with cx >= value (API: ?cx__gte=0.0)
    if request_args.get('cx__gte'):
        query = query.filter(Dlt40Record.cx >= float(request_args['cx__gte']))
    # return records with cx <= value (API: ?cx__lte=0.0)
    if request_args.get('cx__lte'):
        query = query.filter(Dlt40Record.cx <= float(request_args['cx__lte']))
    # return records with cy >= value (API: ?cy__gte=0.0)
    if request_args.get('cy__gte'):
        query = query.filter(Dlt40Record.cy >= float(request_args['cy__gte']))
    # return records with cy <= value (API: ?cy__lte=0.0)
    if request_args.get('cy__lte'):
        query = query.filter(Dlt40Record.cy <= float(request_args['cy__lte']))
    # return records with cz >= value (API: ?cz__gte=0.0)
    if request_args.get('cz__gte'):
        query = query.filter(Dlt40Record.cz >= float(request_args['cz__gte']))
    # return records with cz <= value (API: ?cz__lte=0.0)
    if request_args.get('cz__lte'):
        query = query.filter(Dlt40Record.cz <= float(request_args['cz__lte']))
    # return records with dec >= value (API: ?dec__gte=90.0)
    if request_args.get('dec__gte'):
        query = query.filter(Dlt40Record.dec >= float(request_args['dec__gte']))
    # return records with dec <= value (API: ?dec__lte=90.0)
    if request_args.get('dec__lte'):
        query = query.filter(Dlt40Record.dec <= float(request_args['dec__lte']))
    # return records with discDate like value (API: ?discDate=2019-07-15)
    if request_args.get('discDate'):
        _date = datetime.strptime(request_args['discDate'], '%Y-%m-%d')
        query = query.filter(Dlt40Record.discDate >= _date)
    # return records with discMag >= value (API: ?discMag__gte=0.0)
    if request_args.get('discMag__gte'):
        query = query.filter(Dlt40Record.discMag >= float(request_args['discMag__gte']))
    # return records with discMag <= value (API: ?discMag__lte=10.0)
    if request_args.get('discMag__lte'):
        query = query.filter(Dlt40Record.discMag <= float(request_args['discMag__lte']))
    # return records with discMagFilter like value (API: ?discMagFilter=Q)
    if request_args.get('discMagFilter'):
        query = query.filter(Dlt40Record.discMagFilter.ilike(f"%{request_args['discMagFilter']}%"))
    # return records with discoverer like value (API: ?discoverer=Q)
    if request_args.get('discoverer'):
        query = query.filter(Dlt40Record.discoverer.ilike(f"%{request_args['discoverer']}%"))
    # return records with hostRedshift >= value (API: ?hostRedshift__gte=0.0)
    if request_args.get('hostRedshift__gte'):
        query = query.filter(Dlt40Record.hostRedshift >= float(request_args['hostRedshift__gte']))
    # return records with hostRedshift <= value (API: ?hostRedshift__lte=10.0)
    if request_args.get('hostRedshift__lte'):
        query = query.filter(Dlt40Record.hostRedshift <= float(request_args['hostRedshift__lte']))
    # return records with htm16ID = value (API: ?htm16ID=20)
    if request_args.get('htm16ID'):
        query = query.filter(Dlt40Record.htm16ID == int(request_args['htm16ID']))
    # return records with htm16ID >= value (API: ?htm16ID__gte=20)
    if request_args.get('htm16ID__gte'):
        query = query.filter(Dlt40Record.htm16ID >= int(request_args['htm16ID__gte']))
    # return records with htm16ID <= value (API: ?htm16ID__lte=20)
    if request_args.get('htm16ID__lte'):
        query = query.filter(Dlt40Record.htm16ID <= int(request_args['htm16ID__lte']))
    # return records with id = value (API: ?id=20)
    if request_args.get('id'):
        query = query.filter(Dlt40Record.id == int(request_args['id']))
    # return records with id >= value (API: ?id__gte=20)
    if request_args.get('id__gte'):
        query = query.filter(Dlt40Record.id >= int(request_args['id__gte']))
    # return records with id <= value (API: ?id__lte=20)
    if request_args.get('id__lte'):
        query = query.filter(Dlt40Record.id <= int(request_args['id__lte']))
    # return records with objectname like value (API: ?objectname=Q)
    if request_args.get('objectname'):
        query = query.filter(Dlt40Record.objectname.ilike(f"%{request_args['objectname']}%"))
    # return records with prefix like value (API: ?prefix=AT)
    if request_args.get('prefix'):
        query = query.filter(Dlt40Record.prefix.ilike(f"%{request_args['prefix']}%"))
    # return records with ra >= value (API: ?ra__gte=0.0)
    if request_args.get('ra__gte'):
        query = query.filter(Dlt40Record.ra >= float(request_args['ra__gte']))
    # return records with ra <= value (API: ?ra__lte=360.0)
    if request_args.get('ra__lte'):
        query = query.filter(Dlt40Record.ra <= float(request_args['ra__lte']))
    # return records with redshift >= value (API: ?redshift__gte=0.0)
    if request_args.get('redshift__gte'):
        query = query.filter(Dlt40Record.redshift >= float(request_args['redshift__gte']))
    # return records with redshift <= value (API: ?redshift__lte=10.0)
    if request_args.get('redshift__lte'):
        query = query.filter(Dlt40Record.redshift <= float(request_args['redshift__lte']))
    # return records with sourceGroup name like value (API: ?sourceGroup=demo)
    if request_args.get('sourceGroup'):
        query = query.filter(Dlt40Record.sourceGroup.ilike(f"%{request_args['sourceGroup']}%"))

    # sort results
    sort_value = request_args.get('sort_value', SORT_VALUE[0]).lower()
    sort_order = request_args.get('sort_order', SORT_ORDER[0]).lower()
    if sort_order in SORT_ORDER:
        if sort_order.startswith(SORT_ORDER[0]):
            query = query.order_by(getattr(Dlt40Record, sort_value).asc())
        elif sort_order.startswith(SORT_ORDER[1]):
            query = query.order_by(getattr(Dlt40Record, sort_value).desc())

    # return query
    return query


# +
# function: dlt40_get_text()
# -
def dlt40_get_text():
    return __text__


# +
# function: dlt40_cli_db()
# -
# noinspection PyBroadException
def dlt40_cli_db(iargs=None):

    # check input(s)
    if iargs is None:
        raise Exception('Invalid arguments')

    # it --text is present, describe of the catalog
    if iargs.text:
        print(dlt40_get_text())
        return

    # set default(s)
    request_args = {}

    # get input(s) alphabetically
    if iargs.classType:
        request_args['classType'] = f'{iargs.classType}'
    if iargs.cx__gte:
        request_args['cx__gte'] = f'{iargs.cx__gte}'
    if iargs.cx__lte:
        request_args['cx__lte'] = f'{iargs.cx__lte}'
    if iargs.cy__gte:
        request_args['cy__gte'] = f'{iargs.cy__gte}'
    if iargs.cy__lte:
        request_args['cy__lte'] = f'{iargs.cy__lte}'
    if iargs.cz__gte:
        request_args['cz__gte'] = f'{iargs.cz__gte}'
    if iargs.cz__lte:
        request_args['cz__lte'] = f'{iargs.cz__lte}'
    if iargs.dec__gte:
        request_args['dec__gte'] = f'{iargs.dec__gte}'
    if iargs.dec__lte:
        request_args['dec__lte'] = f'{iargs.dec__lte}'
    if iargs.discDate:
        request_args['discDate'] = f'{iargs.discDate}'
    if iargs.discMag__gte:
        request_args['discMag__gte'] = f'{iargs.discMag__gte}'
    if iargs.discMag__lte:
        request_args['discMag__lte'] = f'{iargs.discMag__lte}'
    if iargs.discMagFilter:
        request_args['discMagFilter'] = f'{iargs.discMagFilter}'
    if iargs.discoverer:
        request_args['discoverer'] = f'{iargs.discoverer}'
    if iargs.hostName:
        request_args['hostName'] = f'{iargs.hostName}'
    if iargs.hostRedshift__gte:
        request_args['hostRedshift__gte'] = f'{iargs.hostRedshift__gte}'
    if iargs.hostRedshift__lte:
        request_args['hostRedshift__lte'] = f'{iargs.hostRedshift__lte}'
    if iargs.htm16ID:
        request_args['htm16ID'] = f'{iargs.htm16ID}'
    if iargs.htm16ID__gte:
        request_args['htm16ID__gte'] = f'{iargs.htm16ID__gte}'
    if iargs.htm16ID__lte:
        request_args['htm16ID__lte'] = f'{iargs.htm16ID__lte}'
    if iargs.id:
        request_args['id'] = f'{iargs.id}'
    if iargs.id__gte:
        request_args['id__gte'] = f'{iargs.id__gte}'
    if iargs.id__lte:
        request_args['id__lte'] = f'{iargs.id__lte}'
    if iargs.objectname:
        request_args['objectname'] = f'{iargs.objectname}'
    if iargs.prefix:
        request_args['prefix'] = f'{iargs.prefix}'
    if iargs.ra__gte:
        request_args['ra__gte'] = f'{iargs.ra__gte}'
    if iargs.ra__lte:
        request_args['ra__lte'] = f'{iargs.ra__lte}'
    if iargs.redshift__gte:
        request_args['redshift__gte'] = f'{iargs.redshift__gte}'
    if iargs.redshift__lte:
        request_args['redshift__lte'] = f'{iargs.redshift__lte}'
    if iargs.sourceGroup:
        request_args['sourceGroup'] = f'{iargs.sourceGroup}'

    # set up access to database
    try:
        if iargs.verbose:
            print(f'connection string = postgresql+psycopg2://{SASSY_DB_USER}:{SASSY_DB_PASS}@'
                  f'{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}')
        engine = create_engine(f'postgresql+psycopg2://{SASSY_DB_USER}:{SASSY_DB_PASS}@'
                               f'{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}')
        if iargs.verbose:
            print(f'engine = {engine}')
        get_session = sessionmaker(bind=engine)
        if iargs.verbose:
            print(f'Session = {get_session}')
        session = get_session()
        if iargs.verbose:
            print(f'session = {session}')
    except Exception as e:
        raise Exception(f'Failed to connect to database, error={e}')

    # execute query
    try:
        if iargs.verbose:
            print(f'executing query')
        query = session.query(Dlt40Record)
        if iargs.verbose:
            print(f'query = {query}')
        query = dlt40_filters(query, request_args)
        if iargs.verbose:
            print(f'query = {query}')
    except Exception as e:
        raise Exception(f'Failed to execute query, error={e}')

    # dump output to file
    if isinstance(iargs.output, str) and iargs.output.strip() != '':
        try:
            with open(iargs.output, 'w') as _wf:
                _wf.write(f'#id,hostName,discoverer,prefix,objectname,redshift,discMag,ra,dec,'
                          f'sourceGroup,discMagFilter,discDate,classType,hostRedshift,cx,cy,cz,htm16ID\n')
                for _e in Dlt40Record.serialize_list(query.all()):
                    _wf.write(f"{_e['id']},{_e['hostName']},{_e['discoverer']},{_e['prefix']},"
                              f"{_e['objectname']},{_e['redshift']},{_e['discMag']},{_e['ra']},{_e['dec']},"
                              f"{_e['sourceGroup']},{_e['discMagFilter']},{_e['discDate']},"
                              f"{_e['classType']},{_e['hostRedshift']},{_e['cx']},{_e['cy']},{_e['cz']},"
                              f"{_e['htm16ID']}\n")
        except Exception:
            pass

    # dump output to screen
    else:
        print(f'#id,hostName,discoverer,prefix,objectname,redshift,discMag,ra,dec,'
              f'sourceGroup,discMagFilter,discDate,classType,hostRedshift,cx,cy,cz,htm16ID')
        for _e in Dlt40Record.serialize_list(query.all()):
            print(f"{_e['id']},{_e['hostName']},{_e['discoverer']},{_e['prefix']},"
                  f"{_e['objectname']},{_e['redshift']},{_e['discMag']},{_e['ra']},{_e['dec']},"
                  f"{_e['sourceGroup']},{_e['discMagFilter']},{_e['discDate']},"
                  f"{_e['classType']},{_e['hostRedshift']},{_e['cx']},{_e['cy']},{_e['cz']},"
                  f"{_e['htm16ID']}")


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s) alphabetically
    _p = argparse.ArgumentParser(description=f'Query DLT40 database', formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument(f'--classType', help=f'class type <str>')
    _p.add_argument(f'--cx__gte', help=f'cx__gte >= <float>')
    _p.add_argument(f'--cx__lte', help=f'cx__lte <= <float>')
    _p.add_argument(f'--cy__gte', help=f'cy__gte >= <float>')
    _p.add_argument(f'--cy__lte', help=f'cy__lte <= <float>')
    _p.add_argument(f'--cz__gte', help=f'cz__gte >= <float>')
    _p.add_argument(f'--cz__lte', help=f'cz__lte <= <float>')
    _p.add_argument(f'--dec__gte', help=f'dec__gte >= <float>')
    _p.add_argument(f'--dec__lte', help=f'dec__lte <= <float>')
    _p.add_argument(f'--discDate', help=f'discovery date <str>')
    _p.add_argument(f'--discMag__gte', help=f'discMag__gte >= <float>')
    _p.add_argument(f'--discMag__lte', help=f'discMag__lte <= <float>')
    _p.add_argument(f'--discMagFilter', help=f'filter <str>')
    _p.add_argument(f'--discoverer', help=f'discoverer <str>')
    _p.add_argument(f'--hostName', help=f'host name <str>')
    _p.add_argument(f'--hostRedshift__gte', help=f'hostRedshift__gte >= <float>')
    _p.add_argument(f'--hostRedshift__lte', help=f'hostRedshift__lte <= <float>')
    _p.add_argument(f'--htm16ID', help=f'htm16ID = <int>')
    _p.add_argument(f'--htm16ID__gte', help=f'htm16ID >= <int>')
    _p.add_argument(f'--htm16ID__lte', help=f'htm16ID <= <int>')
    _p.add_argument(f'--id', help=f'id = <int>')
    _p.add_argument(f'--id__gte', help=f'id >= <int>')
    _p.add_argument(f'--id__lte', help=f'id <= <int>')
    _p.add_argument(f'--objectname', help=f'object name <str>')
    _p.add_argument(f'--prefix', help=f'prefix <str>')
    _p.add_argument(f'--ra__gte', help=f'ra__gte >= <float>')
    _p.add_argument(f'--ra__lte', help=f'ra__lte <= <float>')
    _p.add_argument(f'--redshift__gte', help=f'redshift__gte >= <float>')
    _p.add_argument(f'--redshift__lte', help=f'redshift__lte <= <float>')
    _p.add_argument(f'--sourceGroup', help=f'source group <str>')

    _p.add_argument(f'--output', default='', help=f'output file <str>')
    _p.add_argument(f'--sort_order', help=f"Sort order, one of {SORT_ORDER}")
    _p.add_argument(f'--sort_value', help=f"Sort value, one of {SORT_VALUE}")
    _p.add_argument(f'--text', default=False, action='store_true', help=f'if present, describe the table')
    _p.add_argument(f'--verbose', default=False, action='store_true', help=f'if present, produce more verbose output')
    args = _p.parse_args()

    # execute
    if args:
        dlt40_cli_db(args)
    else:
        raise Exception(f'Insufficient command line arguments specified\nUse: python {sys.argv[0]} --help')
