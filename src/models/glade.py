#!/usr/bin/env python3


# +
# import(s)
# -
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import argparse
import json
import os
import sys
import urllib.request


# +
# __doc__ string
# -
__doc__ = """
    % python3 glade.py --help
"""


# +
# __text__
# -
__text__ = """
Column     Name               Description
1          PGC                PGC number
2          GWGC               Name in the GWGC catalog
3          HyperLEDA          Name in the HyperLEDA catalog
4          2MASS              Name in the 2MASS XSC catalog
5          SDSS               Name in the SDSS-DR12 QSO catalog
6          flag1              Q: source is from the SDSS-DR12 QSO catalog
                              C: source is a globular cluster
                              G: source is from another catalog and not identified as a globular cluster
7          RA                 Right ascension [deg]
8          Dec                Declination [deg]
9          Dist               Luminosity distance [Mpc]
10         Dist_err           Error of distance [Mpc]
11         z                  Redshift
12         B                  Apparent B magnitude
13         B_err              Error of apparent B magnitude
14         B_abs              Absolute B magnitude
15         J                  Apparent J magnitude
16         J_err              Error of apparent J magnitude
17         H                  Apparent H magnitude
18         H_err              Error of apparent H magnitude
19         K                  Apparent K magnitude
20         K_err              Error of apparent K magnitude
21         flag2              0: galaxy had neither measured distance nor measured redshift value
                              1: galaxy had measured redshift value, from which we have calculated distance using the 
                              following cosmological parameters: H_0=70/km/s/Mpc, Omega_M=0.27 and Omega_Lambda=0.73
                              2: galaxy had measured distance value from which we have calculated redshift using the 
                              following cosmological parameters: H_0=70/km/s/Mp, Omega_M=0.27 and Omega_Lambda=0.73
                              3: measured photometric redshift of the galaxy has been changed to spectroscopic 
                              redshift, from which we have calculated distance using the following cosmological 
                              parameters: H_0=70/km/s/Mpc, Omega_M=0.27 and Omega_Lambda=0.73
22         flag3              0: velocity field correction has not been applied to the object
                              1: we have subtracted the radial velocity of the object

"""


# +
# constant(s)
# -
DB_VARCHAR_1 = 1
DB_VARCHAR_128 = 128
DB_VARCHAR_256 = 256
GLADE_TXT_URL = 'http://glade.elte.hu/GLADE_2.3.txt'
SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_PORT = int(os.getenv('SASSY_DB_PORT', -1))
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SORT_ORDER = ['asc', 'desc', 'ascending', 'descending']
SORT_VALUE = ['id', 'pgc', 'gwgc', 'hyperleda', 'twomass', 'sdss', 'flag1', 'ra', 'dec', 'dist', 'disterr', 'z',
              'b', 'b_err', 'b_abs', 'j', 'j_err', 'h', 'h_err', 'k', 'k_err', 'flag2', 'flag3']


# +
# initialize sqlalchemy (deferred)
# -
db = SQLAlchemy()


# +
# class: GladeRecord(), inherits from db.Model
# -
# noinspection PyUnresolvedReferences
class GladeRecord(db.Model):

    # +
    # member variable(s)
    # -

    # define table name
    __tablename__ = 'glade'

    id = db.Column(db.Integer, primary_key=True)
    pgc = db.Column(db.Integer)
    gwgc = db.Column(db.String(DB_VARCHAR_256))
    hyperleda = db.Column(db.String(DB_VARCHAR_128))
    twomass = db.Column(db.String(DB_VARCHAR_128))
    sdss = db.Column(db.String(DB_VARCHAR_128))
    flag1 = db.Column(db.String(DB_VARCHAR_1))
    ra = db.Column(db.Float)
    dec = db.Column(db.Float)
    dist = db.Column(db.Float)
    disterr = db.Column(db.Float)
    z = db.Column(db.Float)
    b = db.Column(db.Float)
    b_err = db.Column(db.Float)
    b_abs = db.Column(db.Float)
    j = db.Column(db.Float)
    j_err = db.Column(db.Float)
    h = db.Column(db.Float)
    h_err = db.Column(db.Float)
    k = db.Column(db.Float)
    k_err = db.Column(db.Float)
    flag2 = db.Column(db.Integer)
    flag3 = db.Column(db.Integer)

    @property
    def pretty_serialized(self):
        return json.dumps(self.serialized(), indent=2)

    def serialized(self):
        return {
            'id': self.id,
            'pgc': self.pgc,
            'gwgc': self.gwgc,
            'hyperleda': self.hyperleda,
            'twomass': self.twomass,
            'sdss': self.sdss,
            'flag1': self.flag1,
            'ra': self.ra,
            'dec': self.dec,
            'dist': self.dist,
            'disterr': self.disterr,
            'z': self.z,
            'b': self.b,
            'b_err': self.b_err,
            'b_abs': self.b_abs,
            'j': self.j,
            'j_err': self.j_err,
            'h': self.h,
            'h_err': self.h_err,
            'k': self.k,
            'k_err': self.k_err,
            'flag2': self.flag2,
            'flag3': self.flag3
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
# function: glade_filters() alphabetically
# -
def glade_filters(query, request_args):

    # return records with b >= value (API: ?b__gte=12.5)
    if request_args.get('b__gte'):
        query = query.filter(GladeRecord.b >= float(request_args['b__gte']))
    # return records with b <= value (API: ?b__lte=12.5)
    if request_args.get('b__lte'):
        query = query.filter(GladeRecord.b <= float(request_args['b__lte']))
    # return records with b_abs >= value (API: ?b_abs__gte=12.5)
    if request_args.get('b_abs__gte'):
        query = query.filter(GladeRecord.b_abs >= float(request_args['b_abs__gte']))
    # return records with b_abs <= value (API: ?b_abs__lte=12.5)
    if request_args.get('b_abs__lte'):
        query = query.filter(GladeRecord.b_abs <= float(request_args['b_abs__lte']))
    # return records with b_err >= value (API: ?b_err__gte=12.5)
    if request_args.get('b_err__gte'):
        query = query.filter(GladeRecord.b_err >= float(request_args['b_err__gte']))
    # return records with b_err <= value (API: ?b_err__lte=12.5)
    if request_args.get('b_err__lte'):
        query = query.filter(GladeRecord.b_err <= float(request_args['b_err__lte']))
    # return records with dec >= value (API: ?dec__gte=-90.0)
    if request_args.get('dec__gte'):
        query = query.filter(GladeRecord.dec >= float(request_args['dec__gte']))
    # return records with dec <= value (API: ?dec__lte=90.0)
    if request_args.get('dec__lte'):
        query = query.filter(GladeRecord.dec <= float(request_args['dec__lte']))
    # return records with dist >= value (API: ?dist__gte=0.0)
    if request_args.get('dist__gte'):
        query = query.filter(GladeRecord.dist >= float(request_args['dist__gte']))
    # return records with dist <= value (API: ?dist__lte=10.0)
    if request_args.get('dist__lte'):
        query = query.filter(GladeRecord.dist <= float(request_args['dist__lte']))
    # return records with disterr >= value (API: ?disterr__gte=0.5)
    if request_args.get('disterr__gte'):
        query = query.filter(GladeRecord.disterr >= float(request_args['disterr__gte']))
    # return records with disterr <= value (API: ?disterr__lte=0.5)
    if request_args.get('disterr__lte'):
        query = query.filter(GladeRecord.disterr <= float(request_args['disterr__lte']))
    # return records with flag1 like value (API: ?flag1=Q)
    if request_args.get('flag1'):
        query = query.filter(GladeRecord.flag1.ilike(f"%{request_args['flag1']}%"))
    # return records with flag2 >= value (API: ?flag2__gte=3)
    if request_args.get('flag2__gte'):
        query = query.filter(GladeRecord.flag2 >= int(request_args['flag2__gte']))
    # return records with flag2 <= value (API: ?flag2__lte=1)
    if request_args.get('flag2__lte'):
        query = query.filter(GladeRecord.flag2 <= int(request_args['flag2__lte']))
    # return records with flag3 >= value (API: ?flag3__gte=3)
    if request_args.get('flag3__gte'):
        query = query.filter(GladeRecord.flag3 >= int(request_args['flag3__gte']))
    # return records with flag3 <= value (API: ?flag3__lte=1)
    if request_args.get('flag3__lte'):
        query = query.filter(GladeRecord.flag3 <= int(request_args['flag3__lte']))
    # return records with gwgc name like value (API: ?gwgc=demo)
    if request_args.get('gwgc'):
        query = query.filter(GladeRecord.gwgc.ilike(f"%{request_args['gwgc']}%"))
    # return records with h >= value (API: ?h__gte=12.5)
    if request_args.get('h__gte'):
        query = query.filter(GladeRecord.h >= float(request_args['h__gte']))
    # return records with h <= value (API: ?h__lte=12.5)
    if request_args.get('h__lte'):
        query = query.filter(GladeRecord.h <= float(request_args['h__lte']))
    # return records with h_err >= value (API: ?h_err__gte=0.5)
    if request_args.get('h_err__gte'):
        query = query.filter(GladeRecord.h_err >= float(request_args['h_err__gte']))
    # return records with h_err <= value (API: ?h_err__lte=0.5)
    if request_args.get('h_err__lte'):
        query = query.filter(GladeRecord.h_err <= float(request_args['h_err__lte']))
    # return records with hyperleda name like value (API: ?hyperleda=demo)
    if request_args.get('hyperleda'):
        query = query.filter(GladeRecord.hyperleda.ilike(f"%{request_args['hyperleda']}%"))
    # return records with id = value (API: ?id=20)
    if request_args.get('id'):
        query = query.filter(GladeRecord.id == int(request_args['id']))
    # return records with id >= value (API: ?id__gte=20)
    if request_args.get('id__gte'):
        query = query.filter(GladeRecord.id >= int(request_args['id__gte']))
    # return records with id <= value (API: ?id__lte=20)
    if request_args.get('id__lte'):
        query = query.filter(GladeRecord.id <= int(request_args['id__lte']))
    # return records with j >= value (API: ?j__gte=13.5)
    if request_args.get('j__gte'):
        query = query.filter(GladeRecord.j >= float(request_args['j__gte']))
    # return records with j <= value (API: ?j__lte=13.5)
    if request_args.get('j__lte'):
        query = query.filter(GladeRecord.j <= float(request_args['j__lte']))
    # return records with j_err >= value (API: ?j_err__gte=0.5)
    if request_args.get('j_err__gte'):
        query = query.filter(GladeRecord.j_err >= float(request_args['j_err__gte']))
    # return records with j_err <= value (API: ?j_err__lte=0.5)
    if request_args.get('j_err__lte'):
        query = query.filter(GladeRecord.j_err <= float(request_args['j_err__lte']))
    # return records with k >= value (API: ?k__gte=14.5)
    if request_args.get('k__gte'):
        query = query.filter(GladeRecord.k >= float(request_args['k__gte']))
    # return records with k <= value (API: ?k__lte=14.5)
    if request_args.get('k__lte'):
        query = query.filter(GladeRecord.k <= float(request_args['k__lte']))
    # return records with k_err >= value (API: ?k_err__gte=0.5)
    if request_args.get('k_err__gte'):
        query = query.filter(GladeRecord.k_err >= float(request_args['k_err__gte']))
    # return records with k_err <= value (API: ?k_err__lte=0.5)
    if request_args.get('k_err__lte'):
        query = query.filter(GladeRecord.k_err <= float(request_args['k_err__lte']))
    # return records with id = value (API: ?pgc=20)
    if request_args.get('pgc'):
        query = query.filter(GladeRecord.pgc == int(request_args['pgc']))
    # return records with pgc >= value (API: ?pgc__gte=20)
    if request_args.get('pgc__gte'):
        query = query.filter(GladeRecord.pgc >= int(request_args['pgc__gte']))
    # return records with pgc <= value (API: ?pgc__lte=20)
    if request_args.get('pgc__lte'):
        query = query.filter(GladeRecord.pgc <= int(request_args['pgc__lte']))
    # return records with ra >= value (API: ?ra__gte=0.0)
    if request_args.get('ra__gte'):
        query = query.filter(GladeRecord.ra >= float(request_args['ra__gte']))
    # return records with ra <= value (API: ?ra__lte=360.0)
    if request_args.get('ra__lte'):
        query = query.filter(GladeRecord.ra <= float(request_args['ra__lte']))
    # return records with sdss name like value (API: ?sdss=demo)
    if request_args.get('sdss'):
        query = query.filter(GladeRecord.sdss.ilike(f"%{request_args['sdss']}%"))
    # return records with twomass name like value (API: ?twomass=demo)
    if request_args.get('twomass'):
        query = query.filter(GladeRecord.twomass.ilike(f"%{request_args['twomass']}%"))
    # return records with z >= value (API: ?z__gte=0.5)
    if request_args.get('z__gte'):
        query = query.filter(GladeRecord.z >= float(request_args['z__gte']))
    # return records with z >= value (API: ?z__lte=3.5)
    if request_args.get('z__lte'):
        query = query.filter(GladeRecord.z <= float(request_args['z__lte']))

    # sort results
    sort_value = request_args.get('sort_value', SORT_VALUE[0]).lower()
    sort_order = request_args.get('sort_order', SORT_ORDER[0]).lower()
    if sort_order in SORT_ORDER:
        if sort_order.startswith(SORT_ORDER[0]):
            query = query.order_by(getattr(GladeRecord, sort_value).asc())
        elif sort_order.startswith(SORT_ORDER[1]):
            query = query.order_by(getattr(GladeRecord, sort_value).desc())

    # return query
    return query


# +
# function: glade_get_text()
# -
def glade_get_text():
    return __text__


# +
# function: glade_cli_db()
# -
# noinspection PyBroadException
def glade_cli_db(iargs=None):

    # check input(s)
    if iargs is None:
        raise Exception('Invalid arguments')

    # if --catalog is present, get the catalog from a well-known URL
    if iargs.catalog:
        try:
            print(f'Receiving catalog from {GLADE_TXT_URL}, this can take some time!')
            with urllib.request.urlopen(GLADE_TXT_URL) as _catalog, open('glade.local.csv', 'w') as _wfd:
                _wfd.write(f'#pgc,gwgc,hyperleda,twomass,sdss,flag1,ra,dec,dist,disterr,z,'
                           f'b,b_err,b_abs,j,j_err,h,h_err,k,k_err,flag2,flag3\n')
                _line = _catalog.read().decode('utf-8')
                _wfd.write(f"{_line.replace(' ', ',')}\n")
            print(f'Received catalog from {GLADE_TXT_URL} OK')
        except Exception:
            pass
        return

    # it --text is present, describe of the catalog
    if iargs.text:
        print(glade_get_text())
        return

    # set default(s)
    request_args = {}

    # get input(s) alphabetically
    if iargs.b__gte:
        request_args['b__gte'] = f'{iargs.b__gte}'
    if iargs.b__lte:
        request_args['b__lte'] = f'{iargs.b__lte}'
    if iargs.b_abs__gte:
        request_args['b_abs__gte'] = f'{iargs.b_abs__gte}'
    if iargs.b_abs__lte:
        request_args['b_abs__lte'] = f'{iargs.b_abs__lte}'
    if iargs.b_err__gte:
        request_args['b_err__gte'] = f'{iargs.b_err__gte}'
    if iargs.b_err__lte:
        request_args['b_err__lte'] = f'{iargs.b_err__lte}'
    if iargs.dec__gte:
        request_args['dec__gte'] = f'{iargs.dec__gte}'
    if iargs.dec__lte:
        request_args['dec__lte'] = f'{iargs.dec__lte}'
    if iargs.dist__gte:
        request_args['dist__gte'] = f'{iargs.dist__gte}'
    if iargs.dist__lte:
        request_args['dist__lte'] = f'{iargs.dist__lte}'
    if iargs.disterr__gte:
        request_args['disterr__gte'] = f'{iargs.disterr__gte}'
    if iargs.disterr__lte:
        request_args['disterr__lte'] = f'{iargs.disterr__lte}'
    if iargs.flag1:
        request_args['flag1'] = f'{iargs.flag1}'
    if iargs.flag2__gte:
        request_args['flag2__gte'] = f'{iargs.flag2__gte}'
    if iargs.flag2__lte:
        request_args['flag2__lte'] = f'{iargs.flag2__lte}'
    if iargs.flag3__gte:
        request_args['flag3__gte'] = f'{iargs.flag3__gte}'
    if iargs.flag3__lte:
        request_args['flag3__lte'] = f'{iargs.flag3__lte}'
    if iargs.gwgc:
        request_args['gwgc'] = f'{iargs.gwgc}'
    if iargs.h__gte:
        request_args['h__gte'] = f'{iargs.h__gte}'
    if iargs.h__lte:
        request_args['h__lte'] = f'{iargs.h__lte}'
    if iargs.h_err__gte:
        request_args['h_err__gte'] = f'{iargs.h_err__gte}'
    if iargs.h_err__lte:
        request_args['h_err__lte'] = f'{iargs.h_err__lte}'
    if iargs.hyperleda:
        request_args['hyperleda'] = f'{iargs.hyperleda}'
    if iargs.id:
        request_args['id'] = f'{iargs.id}'
    if iargs.id__gte:
        request_args['id__gte'] = f'{iargs.id__gte}'
    if iargs.id__lte:
        request_args['id__lte'] = f'{iargs.id__lte}'
    if iargs.j__gte:
        request_args['j__gte'] = f'{iargs.j__gte}'
    if iargs.j__lte:
        request_args['j__lte'] = f'{iargs.j__lte}'
    if iargs.j_err__gte:
        request_args['j_err__gte'] = f'{iargs.j_err__gte}'
    if iargs.j_err__lte:
        request_args['j_err__lte'] = f'{iargs.j_err__lte}'
    if iargs.k__gte:
        request_args['k__gte'] = f'{iargs.k__gte}'
    if iargs.k__lte:
        request_args['k__lte'] = f'{iargs.k__lte}'
    if iargs.k_err__gte:
        request_args['k_err__gte'] = f'{iargs.k_err__gte}'
    if iargs.k_err__lte:
        request_args['k_err__lte'] = f'{iargs.k_err__lte}'
    if iargs.pgc:
        request_args['pgc'] = f'{iargs.pgc}'
    if iargs.pgc__gte:
        request_args['pgc__gte'] = f'{iargs.pgc__gte}'
    if iargs.pgc__lte:
        request_args['pgc__lte'] = f'{iargs.pgc__lte}'
    if iargs.ra__gte:
        request_args['ra__gte'] = f'{iargs.ra__gte}'
    if iargs.ra__lte:
        request_args['ra__lte'] = f'{iargs.ra__lte}'
    if iargs.sdss:
        request_args['sdss'] = f'{iargs.sdss}'
    if iargs.sort_order:
        request_args['sort_order'] = f'{iargs.sort_order}'
    if iargs.sort_value:
        request_args['sort_value'] = f'{iargs.sort_value}'
    if iargs.twomass:
        request_args['twomass'] = f'{iargs.twomass}'
    if iargs.z__gte:
        request_args['z__gte'] = f'{iargs.z__gte}'
    if iargs.z__lte:
        request_args['z__lte'] = f'{iargs.z__lte}'

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
        query = session.query(GladeRecord)
        if iargs.verbose:
            print(f'query = {query}')
        query = glade_filters(query, request_args)
        if iargs.verbose:
            print(f'query = {query}')
    except Exception as e:
        raise Exception(f'Failed to execute query, error={e}')

    # dump output to file
    if isinstance(iargs.output, str) and iargs.output.strip() != '':
        try:
            with open(iargs.output, 'w') as _wf:
                _wf.write(f'#id,pgc,gwgc,hyperleda,twomass,sdss,flag1,ra,dec,dist,disterr,'
                          f'z,b,b_err,b_abs,j,j_err,h,h_err,k,k_err,flag2,flag3\n')
                for _e in GladeRecord.serialize_list(query.all()):
                    _wf.write(f"{_e['id']},{_e['pgc']},{_e['gwgc']},{_e['hyperleda']},{_e['twomass']},"
                              f"{_e['sdss']},{_e['flag1']},{_e['ra']},{_e['dec']},{_e['dist']},"
                              f"{_e['disterr']},{_e['z']},{_e['b']},{_e['b_err']},{_e['b_abs']},"
                              f"{_e['j']},{_e['j_err']},{_e['h']},{_e['h_err']},{_e['k']}, "
                              f"{_e['k_err']},{_e['flag2']},{_e['flag3']}")
        except Exception:
            pass

    # dump output to screen
    else:
        print(f'#id,pgc,gwgc,hyperleda,twomass,sdss,flag1,ra,dec,dist,disterr,'
              f'z,b,b_err,b_abs,j,j_err,h,h_err,k,k_err,flag2,flag3')
        for _e in GladeRecord.serialize_list(query.all()):
            print(f"{_e['id']},{_e['pgc']},{_e['gwgc']},{_e['hyperleda']},{_e['twomass']},"
                  f"{_e['sdss']},{_e['flag1']},{_e['ra']},{_e['dec']},{_e['dist']},"
                  f"{_e['disterr']},{_e['z']},{_e['b']},{_e['b_err']},{_e['b_abs']},"
                  f"{_e['j']},{_e['j_err']},{_e['h']},{_e['h_err']},{_e['k']}, "
                  f"{_e['k_err']},{_e['flag2']},{_e['flag3']}")


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s) alphabetically
    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description=f'Query GLADE database', formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument(f'--b__gte', help=f'b__gte >= <float>')
    _p.add_argument(f'--b__lte', help=f'b__lte <= <float>')
    _p.add_argument(f'--b_abs__gte', help=f'b_abs__gte >= <float>')
    _p.add_argument(f'--b_abs__lte', help=f'b_abs__lte <= <float>')
    _p.add_argument(f'--b_err__gte', help=f'b_err__gte >= <float>')
    _p.add_argument(f'--b_err__lte', help=f'b_err__lte <= <float>')
    _p.add_argument(f'--dec__gte', help=f'dec__gte >= <float>')
    _p.add_argument(f'--dec__lte', help=f'dec__lte <= <float>')
    _p.add_argument(f'--dist__gte', help=f'dist__gte >= <float>')
    _p.add_argument(f'--dist__lte', help=f'dist__lte <= <float>')
    _p.add_argument(f'--disterr__gte', help=f'disterr__gte >= <float>')
    _p.add_argument(f'--disterr__lte', help=f'disterr__lte <= <float>')
    _p.add_argument(f'--flag1', help=f'flag1 <str>')
    _p.add_argument(f'--flag2__gte', help=f'flag2__gte >= <int>')
    _p.add_argument(f'--flag2__lte', help=f'flag2__lte <= <int>')
    _p.add_argument(f'--flag3__gte', help=f'flag3__gte >= <int>')
    _p.add_argument(f'--flag3__lte', help=f'flag3__lte <= <int>')
    _p.add_argument(f'--gwgc', help=f'GWGC name <str>')
    _p.add_argument(f'--h__gte', help=f'h__gte >= <float>')
    _p.add_argument(f'--h__lte', help=f'h__lte <= <float>')
    _p.add_argument(f'--h_err__gte', help=f'h_err__gte >= <float>')
    _p.add_argument(f'--h_err__lte', help=f'h_err__lte <= <float>')
    _p.add_argument(f'--hyperleda', help=f'HyperLEDA name <str>')
    _p.add_argument(f'--id', help=f'id = <int>')
    _p.add_argument(f'--id__gte', help=f'id >= <int>')
    _p.add_argument(f'--id__lte', help=f'id <= <int>')
    _p.add_argument(f'--j__gte', help=f'j__gte >= <float>')
    _p.add_argument(f'--j__lte', help=f'j__lte <= <float>')
    _p.add_argument(f'--j_err__gte', help=f'j_err__gte >= <float>')
    _p.add_argument(f'--j_err__lte', help=f'j_err__lte <= <float>')
    _p.add_argument(f'--k__gte', help=f'k__gte >= <float>')
    _p.add_argument(f'--k__lte', help=f'k__lte <= <float>')
    _p.add_argument(f'--k_err__gte', help=f'k_err__gte >= <float>')
    _p.add_argument(f'--k_err__lte', help=f'k_err__lte <= <float>')
    _p.add_argument(f'--pgc', help=f'id = <int>')
    _p.add_argument(f'--pgc__gte', help=f'id >= <int>')
    _p.add_argument(f'--pgc__lte', help=f'id <= <int>')
    _p.add_argument(f'--ra__gte', help=f'ra__gte >= <float>')
    _p.add_argument(f'--ra__lte', help=f'ra__lte <= <float>')
    _p.add_argument(f'--sdss', help=f'SDSS name <str>')
    _p.add_argument(f'--twomass', help=f'2MASS name <str>')
    _p.add_argument(f'--z__gte', help=f'z__gte >= <float>')
    _p.add_argument(f'--z__lte', help=f'z__lte <= <float>')

    _p.add_argument(f'--catalog', default=False, action='store_true', help=f'if present, get the catalog')
    _p.add_argument(f'--output', default='', help=f'output file <str>')
    _p.add_argument(f'--sort_order', help=f"Sort order, one of {SORT_ORDER}")
    _p.add_argument(f'--sort_value', help=f"Sort value, one of {SORT_VALUE}")
    _p.add_argument(f'--text', default=False, action='store_true', help=f'if present, describe the catalog')
    _p.add_argument(f'--verbose', default=False, action='store_true', help=f'if present, produce more verbose output')
    args = _p.parse_args()

    # execute
    if args:
        glade_cli_db(args)
    else:
        raise Exception(f'Insufficient command line arguments specified\nUse: python {sys.argv[0]} --help')
