#!/usr/bin/env python3


# +
# import(s)
# -
from astropy.coordinates import SkyCoord
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

import argparse
import gzip
import json
import math
import os
import sys
import urllib.request


# +
# __doc__ string
# -
__doc__ = """
    % python3 gwgc_q3c.py --help
"""


# +
# __text__
# -
__text__ = """

VII/267             Gravitational Wave Galaxy Catalogue           (White+ 2011)
================================================================================
A List of Galaxies for Gravitational Wave Searches
      White D.J.,  Daw E.J., Dhillon V.S.
    <Class. Quantum Grav. 28, 085016 (2011); arXiv:1103.0695>
================================================================================
ADC_Keywords: Galaxy catalogs

Abstract:
    We present a list of galaxies within 100Mpc, which we call the
    Gravitational Wave Galaxy Catalogue (GWGC), that is currently being
    used in follow-up searches of electromagnetic counterparts from
    gravitational wave searches. Due to the time constraints of rapid
    follow-up, a locally available catalogue of reduced, homogenized data
    is required. To achieve this we used four existing catalogues: an
    updated version of the Tully Nearby Galaxy Catalog (cat. VII/145),
    145 the Catalog of Neighboring Galaxies (Karachentsev et al. 2004,
    Cat. J/AJ/127/2031), the V8k catalogue (Tully et al.
    2009AJ....138..323T, http://edd.ifa.hawaii.edu/) and HyperLEDA
    (http://leda.univ-lyon1.fr/). The GWGC contains information on sky
    position, distance, blue magnitude, major and minor diameters,
    position angle, and galaxy type for 53,255 galaxies. Errors on these
    quantities are either taken directly from the literature or estimated
    based on our understanding of the uncertainties associated with the
    measurement method. By using the PGC numbering system developed for
    HyperLEDA, the catalogue has a reduced level of degeneracies compared
    to catalogues with a similar purpose and is easily updated. We also
    include 150 Milky Way globular clusters. Finally, we compare the GWGC
    to previously used catalogues, and find the GWGC to be more complete
    within 100 Mpc due to our use of more up-to-date input catalogues and
    the fact that we have not made a blue luminosity cut.

Description:

File Summary:
--------------------------------------------------------------------------------
 FileName  Lrecl  Records   Explanations
--------------------------------------------------------------------------------
ReadMe        80        .   This file
gwgc.dat     148    53312   The Gravitational Wave Galaxy Catalogue
--------------------------------------------------------------------------------

See also:
    VII/145 : Nearby Galaxies Catalogue (NBG) (Tully 1988)
    J/AJ/127/2031 : Catalog of neighboring galaxies (Karachentsev+, 2004)
    http://leda.univ-lyon1.fr/ : The HYPERLEDA home page
    http://edd.ifa.hawaii.edu/ : The Extragalactic Distance Database (EDD)

Byte-by-byte Description of file: gwgc.dat
--------------------------------------------------------------------------------
   Bytes Format Units    Label    Explanations
--------------------------------------------------------------------------------
   1-  7  I7    ---      PGC      [2,4715229]? Identifier from HYPERLEDA
                                  (empty for globular clusters)
   9- 36  A28   ---      Name     Common name of galaxy or globular
  38- 46  F9.5  h        RAhour   Right ascension (J2000, decimal hours)
  48- 55  F8.4  deg      DEdeg    Declination (J2000)
  57- 60  F4.1  ---      TT       [-9,10]? Morphological type code (1)
  62- 66  F5.2  mag      Bmag     ? Apparent blue magnitude
  68- 74  F7.3  arcmin   a        ? Major diameter (arcmins)
  76- 82  F7.3  arcmin e_a        ? Error in major diameter (arcmins)
  84- 90  F7.3  arcmin   b        ? Minor diameter (arcmins)
  92- 98  F7.3  arcmin e_b        ? Error in minor diameter (arcmins)
 100-104  F5.3  ---      b/a      [0,1]? Ratio of minor to major diameters
 106-110  F5.3  ---    e_b/a      ? Error on ratio of minor to major diameters
 112-116  F5.1  deg      PA       [0,180]? Position angle of galaxy
                                    (degrees from north through east)
 118-123  F6.2  mag      BMAG     ? Absolute blue magnitude
 125-131  F7.2  Mpc      Dist     ? Distance (Mpc)
 133-138  F6.2  Mpc    e_Dist     ? error on Distance (Mpc)
 140-143  F4.2  mag    e_Bmag     ? error on Apparent blue magnitude
 145-148  F4.2  mag    e_BMAG     ? error on Absolute blue magnitude
--------------------------------------------------------------------------------
Note (1): Numerical morphology type (-6 to +10 for ellipticals to irregular);
     -9 is assigned for the Milky Way globular clusters.
--------------------------------------------------------------------------------


Acknowledgements:
    Roy Williams (Caltech, USA), Darren White (U. Sheffield, UK)
================================================================================
(End)                                   Francois Ochsenbein [CDS]    11-Jan-2012
"""


# +
# constant(s)
# -
DB_VARCHAR = 128
GWGC_GZIP_URL = 'http://cdsarc.u-strasbg.fr/ftp/VII/267/gwgc.dat.gz'
SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_PORT = os.getenv('SASSY_DB_PORT', None)
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SORT_ORDER = ['asc', 'desc', 'ascending', 'descending']
SORT_VALUE = ['id', 'pgc', 'name', 'ra', 'dec', 'tt', 'b_app', 'a', 'e_a', 'b', 'e_b', 'b_div_a', 'e_b_div_a',
              'pa', 'b_abs', 'dist', 'e_dist', 'e_b_app', 'e_b_abs']


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
# initialize sqlalchemy (deferred)
# -
db = SQLAlchemy()


# +
# class: GwgcQ3cRecord(), inherits from db.Model
# -
# noinspection PyUnresolvedReferences
class GwgcQ3cRecord(db.Model):

    # +
    # member variable(s)
    # -

    # define table name
    __tablename__ = 'gwgc_q3c'

    id = db.Column(db.Integer, primary_key=True)
    pgc = db.Column(db.Integer, nullable=True, default=None)
    name = db.Column(db.String(DB_VARCHAR), nullable=False, default='')
    ra = db.Column(db.Float, nullable=False, index=True)
    dec = db.Column(db.Float, nullable=False, index=True)
    tt = db.Column(db.Float, nullable=True, default=None)
    b_app = db.Column(db.Float, nullable=True, default=None, index=True)
    a = db.Column(db.Float, nullable=True, default=None)
    e_a = db.Column(db.Float, nullable=True, default=None)
    b = db.Column(db.Float, nullable=True, default=None)
    e_b = db.Column(db.Float, nullable=True, default=None)
    b_div_a = db.Column(db.Float, nullable=True, default=None)
    e_b_div_a = db.Column(db.Float, nullable=True, default=None)
    pa = db.Column(db.Float, nullable=True, default=None)
    b_abs = db.Column(db.Float, nullable=True, default=None, index=True)
    dist = db.Column(db.Float, nullable=True, default=None)
    e_dist = db.Column(db.Float, nullable=True, default=None)
    e_b_app = db.Column(db.Float, nullable=True, default=None)
    e_b_abs = db.Column(db.Float, nullable=True, default=None)

    @property
    def pretty_serialized(self):
        return json.dumps(self.serialized(), indent=2)

    def serialized(self):
        return {
            'id': self.id,
            'pgc': self.pgc,
            'name': self.name,
            'ra': self.ra,
            'dec': self.dec,
            'tt': self.tt,
            'b_app': self.b_app,
            'a': self.a,
            'e_a': self.e_a,
            'b': self.b,
            'e_b': self.e_b,
            'b_div_a': self.b_div_a,
            'e_b_div_a': self.e_b_div_a,
            'pa': self.pa,
            'b_abs': self.b_abs,
            'dist': self.dist,
            'e_dist': self.e_dist,
            'e_b_app': self.e_b_app,
            'e_b_abs': self.e_b_abs
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
# function: gwgc_q3c_filters() alphabetically
# -
# noinspection PyBroadException
def gwgc_q3c_filters(query, request_args):

    # return records within astrocone search (API: ?cone=NGC1365,5.0)
    if request_args.get('astrocone'):
        try:
            _nam, _rad = request_args['astrocone'].split(',')
            _ra, _dec = _get_astropy_coords(_nam.strip().upper())
            query = query.filter(func.q3c_radial_query(GwgcQ3cRecord.ra, GwgcQ3cRecord.dec, _ra, _dec, _rad))
        except Exception:
            pass

    # return records within cone search (API: ?cone=23.5,29.2,5.0)
    if request_args.get('cone'):
        try:
            _ra, _dec, _rad = request_args['cone'].split(',')
            query = query.filter(func.q3c_radial_query(GwgcQ3cRecord.ra, GwgcQ3cRecord.dec, _ra, _dec, _rad))
        except Exception:
            pass

    # return records within ellipse search (API: ?ellipse=202.1,47.2,5.0,0.5,25.0)
    if request_args.get('ellipse'):
        try:
            _ra, _dec, _maj, _rat, _pos = request_args['ellipse'].split(',')
            query = query.filter(
                func.q3c_ellipse_query(GwgcQ3cRecord.ra, GwgcQ3cRecord.dec, _ra, _dec, _maj, _rat, _pos))
        except Exception:
            pass

    # return records with major axis >= value (API: ?a__gte=0.3)
    if request_args.get('a__gte'):
        query = query.filter(GwgcQ3cRecord.a >= float(request_args['a__gte']))

    # return records with major axis <= value (API: ?a__lte=0.3)
    if request_args.get('a__lte'):
        query = query.filter(GwgcQ3cRecord.a <= float(request_args['a__lte']))

    # return records with absolute B magnitude >= value (API: ?b_abs__gte=15.0)
    if request_args.get('b_abs__gte'):
        query = query.filter(GwgcQ3cRecord.b_abs >= request_args['b_abs__gte'])

    # return records with absolute B magnitude <= value (API: ?b_abs__lte=15.0)
    if request_args.get('b_abs__lte'):
        query = query.filter(GwgcQ3cRecord.b_abs <= request_args['b_abs__lte'])

    # return records with apparent B magnitude >= value (API: ?b_app__gte=15.0)
    if request_args.get('b_app__gte'):
        query = query.filter(GwgcQ3cRecord.b_app >= request_args['b_app__gte'])

    # return records with apparent B magnitude <= value (API: ?b_app__lte=15.0)
    if request_args.get('b_app__lte'):
        query = query.filter(GwgcQ3cRecord.b_app <= request_args['b_app__lte'])

    # return records with minor axis >= value (API: ?b__gte=0.3)
    if request_args.get('b__gte'):
        query = query.filter(GwgcQ3cRecord.b >= float(request_args['b__gte']))

    # return records with minor axis <= value (API: ?b__lte=0.3)
    if request_args.get('b__lte'):
        query = query.filter(GwgcQ3cRecord.b <= float(request_args['b__lte']))

    # return records with axis ratio >= value (API: ?b_div_a__gte=0.3)
    if request_args.get('b_div_a__gte'):
        query = query.filter(GwgcQ3cRecord.b_div_a >= float(request_args['b_div_a__gte']))

    # return records with a axis ratio <= value (API: ?b_div_a__lte=0.3)
    if request_args.get('b_div_a__lte'):
        query = query.filter(GwgcQ3cRecord.b_div_a <= float(request_args['b_div_a__lte']))

    # return records with an Dec >= value in degrees (API: ?dec__gte=20.0)
    if request_args.get('dec__gte'):
        query = query.filter(GwgcQ3cRecord.dec >= float(request_args['dec__gte']))

    # return records with an Dec <= value in degrees (API: ?dec__lte=20.0)
    if request_args.get('dec__lte'):
        query = query.filter(GwgcQ3cRecord.dec <= float(request_args['dec__lte']))

    # return records where the distance to the nearest source >= value (API: ?dist__gte=1.0)
    if request_args.get('dist__gte'):
        query = query.filter(GwgcQ3cRecord.dist >= float(request_args['dist__gte']))

    # return records where the distance to the nearest source <= value (API: ?dist__lte=1.0)
    if request_args.get('dist__lte'):
        query = query.filter(GwgcQ3cRecord.dist <= float(request_args['dist__lte']))

    # return records with an error in major axis >= value (API: ?e_a__gte=0.3)
    if request_args.get('e_a__gte'):
        query = query.filter(GwgcQ3cRecord.e_a >= float(request_args['e_a__gte']))

    # return records with an error in major axis <= value (API: ?e_a__lte=0.3)
    if request_args.get('e_a__lte'):
        query = query.filter(GwgcQ3cRecord.e_a <= float(request_args['e_a__lte']))

    # return records where the error in the distance to the nearest source >= value (API: ?e_dist__gte=1.0)
    if request_args.get('e_dist__gte'):
        query = query.filter(GwgcQ3cRecord.e_dist >= float(request_args['e_dist__gte']))

    # return records where the error in the distance to the nearest source <= value (API: ?e_dist__lte=1.0)
    if request_args.get('e_dist__lte'):
        query = query.filter(GwgcQ3cRecord.e_dist <= float(request_args['e_dist__lte']))

    # return records with error in absolute B magnitude >= value (API: ?e_b_abs__gte=15.0)
    if request_args.get('e_b_abs__gte'):
        query = query.filter(GwgcQ3cRecord.e_b_abs >= request_args['e_b_abs__gte'])

    # return records with error in absolute B magnitude <= value (API: ?e_b_abs__lte=15.0)
    if request_args.get('e_b_abs__lte'):
        query = query.filter(GwgcQ3cRecord.e_b_abs <= request_args['e_b_abs__lte'])

    # return records with error in apparent B magnitude >= value (API: ?e_b_app__gte=15.0)
    if request_args.get('e_b_app__gte'):
        query = query.filter(GwgcQ3cRecord.e_b_app >= request_args['e_b_app__gte'])

    # return records with error in apparent B magnitude <= value (API: ?e_b_app__lte=15.0)
    if request_args.get('e_b_app__lte'):
        query = query.filter(GwgcQ3cRecord.e_b_app <= request_args['e_b_app__lte'])

    # return records with an error in minor axis >= value (API: ?e_b__gte=0.3)
    if request_args.get('e_b__gte'):
        query = query.filter(GwgcQ3cRecord.e_b >= float(request_args['e_b__gte']))

    # return records with an error in minor axis <= value (API: ?e_b__lte=0.3)
    if request_args.get('e_b__lte'):
        query = query.filter(GwgcQ3cRecord.e_b <= float(request_args['e_b__lte']))

    # return records with an error in axis ratio >= value (API: ?e_b_div_a__gte=0.3)
    if request_args.get('e_b_div_a__gte'):
        query = query.filter(GwgcQ3cRecord.e_b_div_a >= float(request_args['e_b_div_a__gte']))

    # return records with an error in minor ratio <= value (API: ?e_b_div_a__lte=0.3)
    if request_args.get('e_b_div_a__lte'):
        query = query.filter(GwgcQ3cRecord.e_b_div_a <= float(request_args['e_b_div_a__lte']))

    # return records with id = value (API: ?id=20)
    if request_args.get('id'):
        query = query.filter(GwgcQ3cRecord.id == int(request_args['id']))

    # return records with name = value (API: ?name=20)
    if request_args.get('name'):
        query = query.filter(GwgcQ3cRecord.name == request_args['name'])

    # return records with a position angle >= value (API: ?pa__gte=1.0)
    if request_args.get('pa__gte'):
        query = query.filter(GwgcQ3cRecord.pa >= float(request_args['pa__gte']))

    # return records with a position angle <= value (API: ?pa__lte=1.0)
    if request_args.get('pa__lte'):
        query = query.filter(GwgcQ3cRecord.pa <= float(request_args['pa__lte']))

    # return records with pgc = value (API: ?pgc=20)
    if request_args.get('pgc'):
        query = query.filter(GwgcQ3cRecord.pgc == int(request_args['pgc']))

    # return records with an RA >= value in degrees (API: ?ra__gte=12.0)
    if request_args.get('ra__gte'):
        query = query.filter(GwgcQ3cRecord.ra >= float(request_args['ra__gte']))

    # return records with an RA <= value in degrees (API: ?ra__lte=12.0)
    if request_args.get('ra__lte'):
        query = query.filter(GwgcQ3cRecord.ra <= float(request_args['ra__lte']))

    # return records with morphological type >= value (API: ?tt__gte=1.0)
    if request_args.get('tt__gte'):
        query = query.filter(GwgcQ3cRecord.tt >= request_args['tt__gte'])

    # return records with morphological type <= value (API: ?tt__lte=1.0)
    if request_args.get('tt__gte'):
        query = query.filter(GwgcQ3cRecord.tt <= request_args['tt__lte'])

    # sort results
    sort_value = request_args.get('sort_value', SORT_VALUE[0]).lower()
    sort_order = request_args.get('sort_order', SORT_ORDER[0]).lower()
    if sort_order in SORT_ORDER:
        if sort_order.startswith(SORT_ORDER[0]):
            query = query.order_by(getattr(GwgcQ3cRecord, sort_value).asc())
        elif sort_order.startswith(SORT_ORDER[1]):
            query = query.order_by(getattr(GwgcQ3cRecord, sort_value).desc())

    # return query
    return query


# +
# function: gwgc_q3c_get_text()
# -
def gwgc_q3c_get_text():
    return __text__


# +
# function: gwgc_q3c_cli_db()
# -
# noinspection PyBroadException
def gwgc_q3c_cli_db(iargs=None):

    # check input(s)
    if iargs is None:
        raise Exception('Invalid arguments')

    # it --catalog is present, dump the catalog from a well-known URL
    if iargs.catalog:
        try:
            print(f"{gzip.decompress(urllib.request.urlopen(GWGC_GZIP_URL).read()).decode('utf-8')}")
        except Exception:
            pass
        return

    # if --text is present, describe of the catalog
    if iargs.text:
        print(gwgc_q3c_get_text())
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

    if iargs.a__gte:
        request_args['a__gte'] = f'{iargs.a__gte}'
    if iargs.a__lte:
        request_args['a__lte'] = f'{iargs.a__lte}'
    if iargs.b_abs__gte:
        request_args['b_abs__gte'] = f'{iargs.b_abs__gte}'
    if iargs.b_abs__lte:
        request_args['b_abs__lte'] = f'{iargs.b_abs__lte}'
    if iargs.b_app__gte:
        request_args['b_app__gte'] = f'{iargs.b_app__gte}'
    if iargs.b_app__lte:
        request_args['b_app__lte'] = f'{iargs.b_app__lte}'
    if iargs.b__gte:
        request_args['b__gte'] = f'{iargs.b__gte}'
    if iargs.b__lte:
        request_args['b__lte'] = f'{iargs.b__lte}'
    if iargs.b_div_a__gte:
        request_args['b_div_a__gte'] = f'{iargs.b_div_a__gte}'
    if iargs.b_div_a__lte:
        request_args['b_div_a__lte'] = f'{iargs.b_div_a__lte}'
    if iargs.dec__gte:
        request_args['dec__gte'] = f'{iargs.dec__gte}'
    if iargs.dec__lte:
        request_args['dec__lte'] = f'{iargs.dec__lte}'
    if iargs.dist__gte:
        request_args['dist__gte'] = f'{iargs.dist__gte}'
    if iargs.dist__lte:
        request_args['dist__lte'] = f'{iargs.dist__lte}'
    if iargs.e_a__gte:
        request_args['e_a__gte'] = f'{iargs.e_a__gte}'
    if iargs.e_a__lte:
        request_args['e_a__lte'] = f'{iargs.e_a__lte}'
    if iargs.e_b_abs__gte:
        request_args['e_b_abs__gte'] = f'{iargs.e_b_abs__gte}'
    if iargs.e_b_abs__lte:
        request_args['e_b_abs__lte'] = f'{iargs.e_b_abs__lte}'
    if iargs.e_b_app__gte:
        request_args['e_b_app__gte'] = f'{iargs.e_b_app__gte}'
    if iargs.e_b_app__lte:
        request_args['e_b_app__lte'] = f'{iargs.e_b_app__lte}'
    if iargs.e_b__gte:
        request_args['e_b__gte'] = f'{iargs.e_b__gte}'
    if iargs.e_b__lte:
        request_args['e_b__lte'] = f'{iargs.e_b__lte}'
    if iargs.e_b_div_a__gte:
        request_args['e_b_div_a__gte'] = f'{iargs.e_b_div_a__gte}'
    if iargs.e_b_div_a__lte:
        request_args['e_b_div_a__lte'] = f'{iargs.e_b_div_a__lte}'
    if iargs.e_dist__gte:
        request_args['e_dist__gte'] = f'{iargs.e_dist__gte}'
    if iargs.e_dist__lte:
        request_args['e_dist__lte'] = f'{iargs.e_dist__lte}'
    if iargs.id:
        request_args['id'] = f'{iargs.id}'
    if iargs.name:
        request_args['name'] = f'{iargs.name}'
    if iargs.pa__gte:
        request_args['pa__gte'] = f'{iargs.pa__gte}'
    if iargs.pa__lte:
        request_args['pa__lte'] = f'{iargs.pa__lte}'
    if iargs.pgc:
        request_args['pgc'] = f'{iargs.pgc}'
    if iargs.sort_order:
        request_args['sort_order'] = f'{iargs.sort_order}'
    if iargs.sort_value:
        request_args['sort_value'] = f'{iargs.sort_value}'
    if iargs.ra__gte:
        request_args['ra__gte'] = f'{iargs.ra__gte}'
    if iargs.ra__lte:
        request_args['ra__lte'] = f'{iargs.ra__lte}'
    if iargs.tt__gte:
        request_args['tt__gte'] = f'{iargs.tt__gte}'
    if iargs.tt__lte:
        request_args['tt__lte'] = f'{iargs.tt__lte}'

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
        query = session.query(GwgcQ3cRecord)
        if iargs.verbose:
            print(f'query = {query}')
        query = gwgc_q3c_filters(query, request_args)
        if iargs.verbose:
            print(f'query = {query}')
    except Exception as e:
        raise Exception(f'Failed to execute query. error={e}')

    # dump output to file
    if isinstance(iargs.output, str) and iargs.output.strip() != '':
        try:
            with open(iargs.output, 'w') as _wf:
                _wf.write(f'#id,pgc,name,ra,dec,tt,b_app,a,e_a,b,e_b,b_div_a,e_b_div_a,'
                          f'pa,b_abs,dist,e_dist,e_b_app,e_b_abs\n')
                for _e in GwgcQ3cRecord.serialize_list(query.all()):
                    _wf.write(f"{_e['id']},{_e['pgc']},{_e['name']},{_e['ra']},{_e['dec']},{_e['tt']},"
                              f"{_e['b_app']},{_e['a']},{_e['e_a']},{_e['b']},{_e['e_b']},{_e['b_div_a']},"
                              f"{_e['e_b_div_a']},{_e['pa']},{_e['b_abs']},{_e['dist']},{_e['e_dist']},"
                              f"{_e['e_b_app']},{_e['e_b_abs']}\n")
        except Exception:
            pass

    # dump output to screen
    else:
        print(f'#id,pgc,name,ra,dec,tt,b_app,a,e_a,b,e_b,b_div_a,e_b_div_a,pa,b_abs,dist,e_dist,e_b_app,e_b_abs')
        for _e in GwgcQ3cRecord.serialize_list(query.all()):
            print(f"{_e['id']},{_e['pgc']},{_e['name']},{_e['ra']},{_e['dec']},{_e['tt']},"
                  f"{_e['b_app']},{_e['a']},{_e['e_a']},{_e['b']},{_e['e_b']},{_e['b_div_a']},{_e['e_b_div_a']},"
                  f"{_e['pa']},{_e['b_abs']},{_e['dist']},{_e['e_dist']},{_e['e_b_app']},{_e['e_b_abs']}")


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s) alphabetically
    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description=f'Query GWGC_Q3C database', formatter_class=argparse.RawTextHelpFormatter)

    _p.add_argument(f'--astrocone', help=f'Astrocone search <name,radius>')
    _p.add_argument(f'--cone', help=f'Cone search <ra,dec,radius>')
    _p.add_argument(f'--ellipse', help=f'Ellipse search <ra,dec,major_axis,axis_ratio,position_angle>')

    _p.add_argument(f'--a__gte', help=f'Major axis >= <float>')
    _p.add_argument(f'--a__lte', help=f'Major axis <= <float>')
    _p.add_argument(f'--b_abs__gte', help=f'Absolute B magnitude <float>')
    _p.add_argument(f'--b_abs__lte', help=f'Absolute B magnitude <float>')
    _p.add_argument(f'--b_app__gte', help=f'Apparent B magnitude <float>')
    _p.add_argument(f'--b_app__lte', help=f'Apparent B magnitude <float>')
    _p.add_argument(f'--b__gte', help=f'Minor axis >= <float>')
    _p.add_argument(f'--b__lte', help=f'Minor axis <= <float>')
    _p.add_argument(f'--b_div_a__gte', help=f'Axis ratio >= <float>')
    _p.add_argument(f'--b_div_a__lte', help=f'Axis ratio <= <float>')
    _p.add_argument(f'--dec__gte', help=f'Dec >= <float>')
    _p.add_argument(f'--dec__lte', help=f'Dec <= <float>')
    _p.add_argument(f'--dist__gte', help=f'Distance >= <float>')
    _p.add_argument(f'--dist__lte', help=f'Distance <= <float>')
    _p.add_argument(f'--e_a__gte', help=f'Error in major axis >= <float>')
    _p.add_argument(f'--e_a__lte', help=f'Error in major axis <= <float>')
    _p.add_argument(f'--e_b_abs__gte', help=f'Error in absolute B magnitude <float>')
    _p.add_argument(f'--e_b_abs__lte', help=f'Error in absolute B magnitude <float>')
    _p.add_argument(f'--e_b_app__gte', help=f'Error in apparent B magnitude <float>')
    _p.add_argument(f'--e_b_app__lte', help=f'Error in apparent B magnitude <float>')
    _p.add_argument(f'--e_b__gte', help=f'Error in minor axis >= <float>')
    _p.add_argument(f'--e_b__lte', help=f'Error in minor axis <= <float>')
    _p.add_argument(f'--e_b_div_a__gte', help=f'Error in axis ratio >= <float>')
    _p.add_argument(f'--e_b_div_a__lte', help=f'Error in axis ratio <= <float>')
    _p.add_argument(f'--e_dist__gte', help=f'Error in distance >= <float>')
    _p.add_argument(f'--e_dist__lte', help=f'Error in distance <= <float>')
    _p.add_argument(f'--id', help=f'id <int>')
    _p.add_argument(f'--name', help=f'name <str>')
    _p.add_argument(f'--pa__gte', help=f'Position angle >= <float>')
    _p.add_argument(f'--pa__lte', help=f'Position angle <= <float>')
    _p.add_argument(f'--pgc', help=f'pgc <int>')
    _p.add_argument(f'--ra__gte', help=f'RA >= <float>')
    _p.add_argument(f'--ra__lte', help=f'RA <= <float>')
    _p.add_argument(f'--tt__gte', help=f'Morphological type <float>')
    _p.add_argument(f'--tt__lte', help=f'Morphological type <float>')

    _p.add_argument(f'--catalog', default=False, action='store_true', help=f'if present, dump the catalog')
    _p.add_argument(f'--output', default='', help=f'Output file <str>')
    _p.add_argument(f'--sort_order', help=f"Sort order, one of {SORT_ORDER}")
    _p.add_argument(f'--sort_value', help=f"Sort value, one of {SORT_VALUE}")
    _p.add_argument(f'--text', default=False, action='store_true', help=f'if present, describe the catalog')
    _p.add_argument(f'--verbose', default=False, action='store_true', help=f'if present, produce more verbose output')
    args = _p.parse_args()

    # execute
    if args:
        gwgc_q3c_cli_db(args)
    else:
        raise Exception(f'Insufficient command line arguments specified\nUse: python {sys.argv[0]} --help')
