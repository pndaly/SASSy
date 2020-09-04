#!/usr/bin/env python3


# +
# import(s)
# -
from src import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import argparse
import os
import sys


# +
# __doc__ string
# -
__doc__ = """
    % python3 sassy_cron.py --help
"""


# +
# __text__
# -
__text__ = """
        Column        |            Type             | Collation | Nullable | Default 
----------------------+-----------------------------+-----------+----------+---------
 zoid                 | character varying(50)       |           |          | 
 zjd                  | double precision            |           |          | 
 zmagap               | double precision            |           |          | 
 zmagpsf              | double precision            |           |          | 
 zmagdiff             | double precision            |           |          | 
 zfid                 | integer                     |           |          | 
 zdrb                 | double precision            |           |          | 
 zrb                  | double precision            |           |          | 
 zsid                 | integer                     |           |          | 
 zcandid              | bigint                      |           |          | 
 zssnamenr            | character varying(200)      |           |          | 
 zra                  | double precision            |           |          | 
 zdec                 | double precision            |           |          | 
 gid                  | integer                     |           |          | 
 gra                  | double precision            |           |          | 
 gdec                 | double precision            |           |          | 
 gz                   | double precision            |           |          | 
 gdist                | double precision            |           |          | 
 gsep                 | double precision            |           |          | 
 id                   | integer                     |           |          | 
 tns_id               | integer                     |           |          | 
 tns_name             | character varying(128)      |           |          | 
 tns_link             | character varying(128)      |           |          | 
 ra                   | double precision            |           |          | 
 dec                  | double precision            |           |          | 
 redshift             | double precision            |           |          | 
 discovery_date       | timestamp without time zone |           |          | 
 discovery_mag        | double precision            |           |          | 
 discovery_instrument | character varying(128)      |           |          | 
 filter_name          | character varying(32)       |           |          | 
 tns_class            | character varying(128)      |           |          | 
 host                 | character varying(128)      |           |          | 
 host_z               | double precision            |           |          | 
 source_group         | character varying(128)      |           |          | 
 alias                | character varying(128)      |           |          | 
 certificate          | character varying(128)      |           |          | 
 aetype               | character varying(64)       |           |          | 
 altype               | character varying(64)       |           |          | 
 aeprob               | double precision            |           |          | 
 alprob               | double precision            |           |          | 
Indexes:
    "sassy_cron_q3c_ang2ipix_idx" btree (q3c_ang2ipix(zra, zdec)) CLUSTER
"""


# +
# constant(s)
# -
DB_VARCHAR_200 = 200
DB_VARCHAR_128 = 128
DB_VARCHAR_50 = 50
DB_VARCHAR_64 = 64
DB_VARCHAR_32 = 32

SASSY_APP_HOST = os.getenv('SASSY_APP_HOST', "sassy.as.arizona.edu")
SASSY_APP_PORT = os.getenv('SASSY_APP_PORT', 5000)

SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PORT = os.getenv('SASSY_DB_PORT', None)


# +
# initialize sqlalchemy (deferred)
# -
db = SQLAlchemy()


# +
# class: SassyCron(), inherits from db.Model
# -
# noinspection PyPep8Naming,PyUnresolvedReferences
class SassyCron(db.Model):

    # +
    # member variable(s)
    # -

    # define table name
    __tablename__ = 'sassy_cron'

    # glade element(s)
    gdec = db.Column(db.Float)
    gdist = db.Column(db.Float)
    gid = db.Column(db.Integer, primary_key=True)
    gra = db.Column(db.Float)
    gsep = db.Column(db.Float)
    gz = db.Column(db.Float)

    # tns element(s)
    alias = db.Column(db.String(DB_VARCHAR_128))
    certificate = db.Column(db.String(DB_VARCHAR_128))
    dec = db.Column(db.Float)
    discovery_date = db.Column(db.DateTime)
    discovery_instrument = db.Column(db.String(DB_VARCHAR_128))
    discovery_mag = db.Column(db.Float)
    filter_name = db.Column(db.String(DB_VARCHAR_32))
    host = db.Column(db.String(DB_VARCHAR_128))
    host_z = db.Column(db.Float)
    id = db.Column(db.Integer)
    ra = db.Column(db.Float)
    redshift = db.Column(db.Float)
    source_group = db.Column(db.String(DB_VARCHAR_128))
    tns_class = db.Column(db.String(DB_VARCHAR_128))
    tns_id = db.Column(db.Integer)
    tns_name = db.Column(db.String(DB_VARCHAR_128))
    tns_link = db.Column(db.String(DB_VARCHAR_128))

    # ztf element(s)
    zcandid = db.Column(db.BigInteger)
    zdec = db.Column(db.Float, index=True)
    zdrb = db.Column(db.Float)
    zfid = db.Column(db.Integer)
    zjd = db.Column(db.Float, primary_key=True)
    zoid = db.Column(db.String(DB_VARCHAR_50), primary_key=True)
    zmagap = db.Column(db.Float)
    zmagpsf = db.Column(db.Float)
    zmagdiff = db.Column(db.Float)
    zra = db.Column(db.Float, index=True)
    zrb = db.Column(db.Float)
    zsid = db.Column(db.Integer)
    zssnamenr = db.Column(db.String(DB_VARCHAR_200))

    # alerce element(s)
    aetype = db.Column(db.String(DB_VARCHAR_64))
    altype = db.Column(db.String(DB_VARCHAR_64))
    aeprob = db.Column(db.Float)
    alprob = db.Column(db.Float)
    dpng = db.Column(db.String(DB_VARCHAR_200))
    spng = db.Column(db.String(DB_VARCHAR_200))
    tpng = db.Column(db.String(DB_VARCHAR_200))

    # +
    # method: serialized()
    # -
    def serialized(self):
        return {
            'aeprob': float(self.aeprob),
            'alprob': float(self.alprob),
            'aetype': str(self.aetype),
            'altype': str(self.altype),
            'dpng': str(self.dpng),
            'spng': str(self.spng),
            'tpng': str(self.tpng),
            'gdec': float(self.gdec),
            'gdist': float(self.gdist),
            'gid': int(self.gid),
            'gra': float(self.gra),
            'gsep': float(self.gsep),
            'gz': float(self.gz),
            'zcandid': int(self.zcandid),
            'zdec': float(self.zdec),
            'zdrb': float(self.zdrb),
            'zlambda': float(ZTF_WAVELENGTH.get(self.zfid, math.nan)),
            'zfilter': ZTF_FILTERS.get(int(self.zfid), ''),
            'zjd': float(self.zjd),
            'zoid': str(self.zoid),
            'zmagap': float(self.zmagap),
            'zmagpsf': float(self.zmagpsf),
            'zmagdiff': float(self.zmagdiff),
            'zra': float(self.zra),
            'zrb': float(self.zrb),
            'zsid': int(self.zsid),
            'zssnamenr': str(self.zssnamenr)
        }

    # +
    # (overload) method: __str__()
    # -
    def __str__(self):
        return f'{self.zcandid}'

    # +
    # (static) method: serialize_list()
    # -
    @staticmethod
    def serialize_list(slist=None):
        return [_a.serialized() for _a in slist]


# +
# function: sassy_cron_get_text()
# -
def sassy_cron_get_text():
    return __text__


# +
# function: sassy_cron_filters() alphabetically
# -
def sassy_cron_filters(query, request_args):

    # return records with aetype like value (API: ?aetype='Bogus')
    if request_args.get('aetype'):
        query = query.filter(SassyCron.aetype.ilike(f"%{request_args['aetype']}%"))

    # return records with altype like value (API: ?altype='Bogus')
    if request_args.get('altype'):
        query = query.filter(SassyCron.altype.ilike(f"%{request_args['altype']}%"))

    # return records with gdist >= value (API: ?gdist__gte=150.0)
    if request_args.get('gdist__gte'):
        query = query.filter(SassyCron.gdist >= float(request_args['gdist__gte']))

    # return records with gdist <= value (API: ?gdist__lte=150.0)
    if request_args.get('gdist__lte'):
        query = query.filter(SassyCron.gdist <= float(request_args['gdist__lte']))

    # return records with gsep >= value (API: ?gsep__gte=30.0)
    if request_args.get('gsep__gte'):
        query = query.filter(SassyCron.gsep >= float(request_args['gsep__gte'])/3600.0)

    # return records with gsep <= value (API: ?gsep__lte=30.0)
    if request_args.get('gsep__lte'):
        query = query.filter(SassyCron.gsep <= float(request_args['gsep__lte'])/3600.0)

    # return records with zcandid (API: ?zcandid=xxdcdcdvfwd)
    if request_args.get('zcandid'):
        query = query.filter(SassyCron.zcandid == str(request_args['zcandid']))

    # return records with an Dec >= value in degrees (API: ?zdec__gte=20.0)
    if request_args.get('zdec__gte'):
        query = query.filter(SassyCron.zdec >= float(request_args['zdec__gte']))

    # return records with an Dec <= value in degrees (API: ?zdec__lte=20.0)
    if request_args.get('zdec__lte'):
        query = query.filter(SassyCron.zdec <= float(request_args['zdec__lte']))

    # return records where the deep-learning real-bogus score >= value (API: ?zdrb__gte=1.0)
    if request_args.get('zdrb__gte'):
        query = query.filter(SassyCron.zdrb >= float(request_args['zdrb__gte']))

    # return records where the deep-learning real-bogus score <= value (API: ?zdrb__lte=1.0)
    if request_args.get('zdrb__lte'):
        query = query.filter(SassyCron.zdrb <= float(request_args['zdrb__lte']))

    # return records where filter = value (API: ?zfid=1)
    if request_args.get('zfid'):
        query = query.filter(SassyCron.zfid == int(request_args['zfid']))

    # return records with zfilter (API: ?zfilter=red)
    if request_args.get('zfilter'):
        query = query.filter(SassyCron.zfid == int(ZTF_FILTERS_R.get(request_args['zfilter'], 0)))

    # return records with a JD >= date (API: ?zjd__gte=2458302.6906713)
    if request_args.get('zjd__gte'):
        query = query.filter(SassyCron.zjd >= request_args['zjd__gte'])

    # return records with a JD <= date (API: ?zjd__lte=2458302.6906713)
    if request_args.get('zjd__lte'):
        query = query.filter(SassyCron.zjd <= request_args['zjd__lte'])

    # return records with a magap >= value (API: ?zmagap__gte=15.6906713)
    if request_args.get('zmagap__gte'):
        query = query.filter(SassyCron.zmagap >= request_args['zmagap__gte'])

    # return records with a magap <= value (API: ?zmagap__lte=20.6906713)
    if request_args.get('zmagap__lte'):
        query = query.filter(SassyCron.zmagap <= request_args['zmagap__lte'])

    # return records with a magpsf >= value (API: ?zmagpsf__gte=15.6906713)
    if request_args.get('zmagpsf__gte'):
        query = query.filter(SassyCron.zmagpsf >= request_args['zmagpsf__gte'])

    # return records with a magpsf <= value (API: ?zmagpsf__lte=20.6906713)
    if request_args.get('zmagpsf__lte'):
        query = query.filter(SassyCron.zmagpsf <= request_args['zmagpsf__lte'])

    # return records with a magdiff >= value (API: ?zmagdiff__gte=0.6906713)
    if request_args.get('zmagdiff__gte'):
        query = query.filter(SassyCron.zmagdiff >= request_args['zmagdiff__gte'])

    # return records with a magdiff <= value (API: ?zmagdiff__lte=0.6906713)
    if request_args.get('zmagdiff__lte'):
        query = query.filter(SassyCron.zmagdiff <= request_args['zmagdiff__lte'])

    # return records with zoid (API: ?zoid=ZTFsdneuenf)
    if request_args.get('zoid'):
        query = query.filter(SassyCron.zoid == request_args['zoid'])

    # return records with an RA >= value in degrees (API: ?zra__gte=20.0)
    if request_args.get('zra__gte'):
        query = query.filter(SassyCron.zra >= float(request_args['zra__gte']))

    # return records with an RA <= value in degrees (API: ?zra__lte=20.0)
    if request_args.get('zra__lte'):
        query = query.filter(SassyCron.zra <= float(request_args['zra__lte']))

    # return records with a real/bogus score >= value (API: ?zrb__gte=0.3)
    if request_args.get('zrb__gte'):
        query = query.filter(SassyCron.zrb >= float(request_args['zrb__gte']))

    # return records with a real/bogus score <= value (API: ?zrb__lte=0.3)
    if request_args.get('zrb__lte'):
        query = query.filter(SassyCron.zrb <= float(request_args['zrb__lte']))

    # return records with zsid >= value (API: ?zsid__gte=20.0)
    if request_args.get('zsid__gte'):
        query = query.filter(SassyCron.zsid >= int(request_args['zsid__gte']))

    # return records with zsid <= value (API: ?zsid__lte=20.0)
    if request_args.get('zsid__lte'):
        query = query.filter(SassyCron.zsid <= int(request_args['zsid__lte']))

    # sort results
    sort_by = request_args.get('sort_value', 'zjd')
    sort_order = request_args.get('sort_order', 'desc')
    if sort_order == 'desc':
        query = query.order_by(getattr(SassyCron, sort_by).desc())
    elif sort_order == 'asc':
        query = query.order_by(getattr(SassyCron, sort_by).asc())

    # return query
    return query


# +
# function: sassy_cron_cli_db()
# -
# noinspection PyBroadException
def sassy_cron_cli_db(iargs=None):

    # check input(s)
    if iargs is None:
        raise Exception('Invalid arguments')

    # if --text is present, describe of the catalog
    if iargs.text:
        print(sassy_cron_get_text())
        return

    # set default(s)
    request_args = {}

    # get input(s) alphabetically
    if iargs.aetype:
        request_args['aetype'] = f'{iargs.aetype}'
    if iargs.altype:
        request_args['altype'] = f'{iargs.altype}'
    if iargs.gdist__gte:
        request_args['gdist__gte'] = f'{iargs.gdist__gte}'
    if iargs.gdist__lte:
        request_args['gdist__lte'] = f'{iargs.gdist__lte}'
    if iargs.gsep__gte:
        request_args['gsep__gte'] = f'{iargs.gsep__gte}'
    if iargs.gsep__lte:
        request_args['gsep__lte'] = f'{iargs.gsep__lte}'
    if iargs.zcandid:
        request_args['zcandid'] = f'{iargs.zcandid}'
    if iargs.zdec__gte:
        request_args['zdec__gte'] = f'{iargs.zdec__gte}'
    if iargs.zdec__lte:
        request_args['zdec__lte'] = f'{iargs.zdec__lte}'
    if iargs.zdrb__gte:
        request_args['zdrb__gte'] = f'{iargs.zdrb__gte}'
    if iargs.zdrb__lte:
        request_args['zdrb__lte'] = f'{iargs.zdrb__lte}'
    if iargs.zfid:
        request_args['zfid'] = f'{iargs.zfid}'
    if iargs.zfilter:
        request_args['zfilter'] = f'{iargs.zfilter}'
    if iargs.zjd__gte:
        request_args['zjd__gte'] = f'{iargs.zjd__gte}'
    if iargs.zjd__lte:
        request_args['zjd__lte'] = f'{iargs.zjd__lte}'
    if iargs.zmagap__gte:
        request_args['zmagap__gte'] = f'{iargs.zmagap__gte}'
    if iargs.zmagap__lte:
        request_args['zmagap__lte'] = f'{iargs.zmagap__lte}'
    if iargs.zmagpsf__gte:
        request_args['zmagpsf__gte'] = f'{iargs.zmagpsf__gte}'
    if iargs.zmagpsf__lte:
        request_args['zmagpsf__lte'] = f'{iargs.zmagpsf__lte}'
    if iargs.zmagdiff__gte:
        request_args['zmagdiff__gte'] = f'{iargs.zmagdiff__gte}'
    if iargs.zmagdiff__lte:
        request_args['zmagdiff__lte'] = f'{iargs.zmagdiff__lte}'
    if iargs.zoid:
        request_args['zoid'] = f'{iargs.zoid}'
    if iargs.zra__gte:
        request_args['zra__gte'] = f'{iargs.zra__gte}'
    if iargs.zra__lte:
        request_args['zra__lte'] = f'{iargs.zra__lte}'
    if iargs.zrb__gte:
        request_args['zrb__gte'] = f'{iargs.zrb__gte}'
    if iargs.zrb__lte:
        request_args['zrb__lte'] = f'{iargs.zrb__lte}'
    if iargs.zsid__gte:
        request_args['zsid__gte'] = f'{iargs.zsid__gte}'
    if iargs.zsid__lte:
        request_args['zsid__lte'] = f'{iargs.zsid__lte}'

    # set up access to database
    try:
        if iargs.verbose:
            print(f'connection string = postgresql+psycopg2://'
                  f'{SASSY_DB_USER}:{SASSY_DB_PASS}@{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}')
        engine = create_engine(f'postgresql+psycopg2://'
                               f'{SASSY_DB_USER}:{SASSY_DB_PASS}@{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}')
        if iargs.verbose:
            print(f'engine = {engine}')
        _session = sessionmaker(bind=engine)
        if iargs.verbose:
            print(f'Session = {_session}')
        session = _session()
        if iargs.verbose:
            print(f'session = {session}')
    except Exception as e:
        raise Exception(f'Failed to connect to database, error={e}')

    # execute query
    try:
        if iargs.verbose:
            print(f'executing query')
        query = session.query(SassyCron)
        if iargs.verbose:
            print(f'query = {query}')
        query = sassy_cron_filters(query, request_args)
        if iargs.verbose:
            print(f'query = {query}')
        query = query.order_by(SassyCron.zjd.desc())
        if iargs.verbose:
            print(f'query = {query}')
    except Exception as e:
        raise Exception(f'Failed to execute query, error={e}')

    # dump output to file
    if isinstance(iargs.output, str) and iargs.output.strip() != '':
        try:
            with open(iargs.output, 'w') as _wf:
                _wf.write('#gdec,gdist,gid,gra,gsep,gz,zcandid,zdec,zdrb,'
                          'zlambda,zfilter,zjd,zoid,zmagap,zmagpsf,zmagdiff,zra,zrb,zsid,aeprob,alprob,aetype,altype\n')
                for _e in SassyCron.serialize_list(query.all()):
                    _wf.write(f"{_e['gdec']},{_e['gdist']},{_e['gid']},{_e['gra']},{_e['gz']},"
                              f"{_e['zcandid']},{_e['zdec']},{_e['zdrb']},{_e['zlambda']},"
                              f"{_e['zfilter']},{_e['zjd']},{_e['zoid']},{_e['zmagap']},"
                              f"{_e['zmagpsf']},{_e['zmagdiff']},{_e['zra']},{_e['zrb']},{_e['zsid']},"
                              f"{_e['aeprob']},{_e['alprob']},{_e['aetype']},{_e['altype']}\n")
        except Exception:
            pass

    # dump output to screen
    else:
        print('#gdec,gdist,gid,gra,gsep,gz,zcandid,zdec,zdrb,'
              'zlambda,zfilter,zjd,zoid,zmagap,zmagpsf,zmagdiff,zra,zrb,zsid,aeprob,alprob,aetype,altype')
        for _e in SassyCron.serialize_list(query.all()):
            print(f"{_e['gdec']},{_e['gdist']},{_e['gid']},{_e['gra']},{_e['gz']},"
                  f"{_e['zcandid']},{_e['zdec']},{_e['zdrb']},{_e['zlambda']},"
                  f"{_e['zfilter']},{_e['zjd']},{_e['zoid']},{_e['zmagap']},"
                  f"{_e['zmagpsf']},{_e['zmagdiff']},{_e['zra']},{_e['zrb']},{_e['zsid']},"
                  f"{_e['aeprob']},{_e['alprob']},{_e['aetype']},{_e['altype']}")


# +
# function: main()
# -
if __name__ == '__main__':

    # get command line argument(s) alphabetically
    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description=f'Query SassyCron Table', formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument(f'--aetype', help=f'Alerce Early Classifier <= <str>')
    _p.add_argument(f'--altype', help=f'Alerce Late Classifier <= <str>')
    _p.add_argument(f'--gdist__gte', help=f'Glade Distance (Mpc) >= <float>')
    _p.add_argument(f'--gdist__lte', help=f'Glade Distance (Mpc) <= <float>')
    _p.add_argument(f'--gsep__gte', help=f'Glade separation (asec) >= <float>')
    _p.add_argument(f'--gsep__lte', help=f'Glade separation (asec) <= <float>')
    _p.add_argument(f'--zcandid', help=f'ZTF Candidate ID <int>')
    _p.add_argument(f'--zdec__gte', help=f'ZTF Dec >= <float>')
    _p.add_argument(f'--zdec__lte', help=f'ZTF Dec <= <float>')
    _p.add_argument(f'--zdrb__gte', help=f'ZTF Deep-Learning Real-Bogus score >= <float>')
    _p.add_argument(f'--zdrb__lte', help=f'ZTF Deep-Learning Real-Bogus score <= <float>')
    _p.add_argument(f'--zfid', help=f'ZTF Filter ID >= <int>')
    _p.add_argument(f'--zfilter', help=f'ZTF Filter Name <= <str>')
    _p.add_argument(f'--zjd__gte', help=f'ZTF Julian Day >= <float>')
    _p.add_argument(f'--zjd__lte', help=f'ZTF Julian Day <= <float>')
    _p.add_argument(f'--zmagap__gte', help=f'ZTF Aperture Magnitude >= <float>')
    _p.add_argument(f'--zmagap__lte', help=f'ZTF Aperture Magnitude <= <float>')
    _p.add_argument(f'--zmagpsf__gte', help=f'ZTF PSF Magnitude >= <float>')
    _p.add_argument(f'--zmagpsf__lte', help=f'ZTF PSF Magnitude <= <float>')
    _p.add_argument(f'--zmagdiff__gte', help=f'ZTF Magnitude Difference >= <float>')
    _p.add_argument(f'--zmagdiff__lte', help=f'ZTF Magnitude Difference <= <float>')
    _p.add_argument(f'--zoid', help=f'ZTF Object ID <str>')
    _p.add_argument(f'--zra__gte', help=f'ZTF RA >= <float>')
    _p.add_argument(f'--zra__lte', help=f'ZTF RA <= <float>')
    _p.add_argument(f'--zrb__gte', help=f'ZTF Real-Bogus score >= <float>')
    _p.add_argument(f'--zrb__lte', help=f'ZTF Real-Bogus score <= <float>')
    _p.add_argument(f'--zsid__gte', help=f'ZTF SASSy id >= <int>')
    _p.add_argument(f'--zsid__lte', help=f'ZTF SASSy id <= <int>')

    _p.add_argument(f'--output', default='', help=f'Output file <str>')
    _p.add_argument(f'--text', default=False, action='store_true', help=f'if present, describe the catalog')
    _p.add_argument(f'--verbose', default=False, action='store_true', help=f'if present, produce more verbose output')
    args = _p.parse_args()

    # execute
    if args:
        sassy_cron_cli_db(args)
    else:
        raise Exception(f'Insufficient command line arguments specified\nUse: python {sys.argv[0]} --help') 
