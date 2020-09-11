#!/usr/bin/env python3


# +
# import(s)
# -
from astropy.coordinates import SkyCoord
from astropy.time import Time
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import shape
from geoalchemy2 import Geography
from geoalchemy2 import Geometry
from sqlalchemy import cast
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import argparse
import fastavro
import io
import json
import math
import os
import pandas as pd
import requests
import sys


# +
# __doc__ string
# -
__doc__ = """
    % python3 ztf.py --help
"""


# +
# __text__
# -
__text__ = """

sid:             Unique ID for this alert, assigned by SASSy. sid in JSON view.
objectId:        Unique identifier for this object.
time:            Observation time at start of exposure [UTC]
filter:          (Derived) Filter name (g, r, i) derived from fid (1, 2, 3).
ra:              Right Ascension of candidate; J2000 [deg]
dec:             Declination of candidate; J2000 [deg]
magpsf:          Magnitude from PSF-fit photometry measured from difference image [mag]
magap:           Aperture mag using 8 pixel diameter aperture measured from difference image [mag]
distnr:          Distance to nearest source in reference image PSF-catalog within 30 arcsec 
                   (1 pixel = 1.0 arcsecond) [pixels]
deltamaglatest:  (Derived) magpsf[this alert] - magpsf[last alert at this location from image of same filter] 
                   if a previous alert is available, otherwise Null.
deltamagref:     (Derived) If distnr < 2" (~2 ZTF pixels), deltamagref = (magnr - magpsf), otherwise Null.
rb:              RealBogus quality score; range is 0 to 1 where closer to 1 is more reliable.
classtar:        Star/Galaxy classification score from SExtractor measured from the difference image.

Most modifiers correspond to columns displayed in the main table, with the exception of the following:

jd:                   Modify alerts by JD instead of gregorian date.
candid:               The value of the candid field of the alert. Exact match.
Cone Search:          Returns results contained within the radius of a given point, in degrees. 
                      For example: 43.2,-30.2,0.2. The format is ra,dec,radius in degrees.
Cone Search (Object): Returns results contained within the radius of a given point, obtained via 
                      looking up an object name with astropy. For example: m51,5.
Nearby Objects:       Each alert contains the names of the 3 closest objects from the Panstarrs-1 catalog. 
                      Modifying on a PS1 object id will return alerts for which this object is listed as close by.
Classtar:             Return alerts where the The Star/Galaxy classification score from SExtractor is within 
                      the provided bounds. Measured from the difference image, not the reference.
FWHM:                 Return alerts where the FWHM is less than or equal to the given value. 
                      Measured from the difference image, not the reference. [pixels].

"""


# +
# constant(s)
# -
DB_VARCHAR = 200
DB_OBJCHAR = 50
DB_VARCHAR_32 = 32
DB_SRID = 4035

EARTH_RADIUS_METERS = 6371008.77141506

SASSY_APP_HOST = os.getenv('SASSY_APP_HOST', "sassy.as.arizona.edu")
SASSY_APP_PORT = os.getenv('SASSY_APP_PORT', 5000)
if SASSY_APP_HOST.lower() == 'localhost' or SASSY_APP_HOST == '127.0.0.1':
    SASSY_APP_ZTF_FILES_URL = f'http://{SASSY_APP_HOST}/sassy/ztf/files'
else:
    SASSY_APP_ZTF_FILES_URL = f'https://{SASSY_APP_HOST}/sassy/ztf/files'

SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PORT = os.getenv('SASSY_DB_PORT', None)

ZTF_FILTERS = ['g', 'r', 'i']
ZTF_PREVIOUS_CANDIDATES_RADIUS = 0.000416667


# +
# initialize sqlalchemy (deferred)
# -
db = SQLAlchemy()


# +
# class: ZtfAlert(), inherits from db.Model
# -
# noinspection PyPep8Naming,PyUnresolvedReferences
class ZtfAlert(db.Model):

    # +
    # member variable(s)
    # -

    # define table name
    __tablename__ = 'alert'

    id = db.Column(db.Integer, primary_key=True)
    publisher = db.Column(db.String(DB_VARCHAR), nullable=False, default='')
    objectId = db.Column(db.String(DB_OBJCHAR), index=True)
    alert_candid = db.Column(db.BigInteger, nullable=True, default=None, index=True, unique=True)
    jd = db.Column(db.Float, nullable=False, index=True)
    fid = db.Column(db.Integer, nullable=False)
    pid = db.Column(db.BigInteger, nullable=False)
    diffmaglim = db.Column(db.Float, nullable=True, default=None)
    pdiffimfilename = db.Column(db.String(DB_VARCHAR), nullable=True, default=None)
    programpi = db.Column(db.String(DB_VARCHAR), nullable=True, default=None)
    programid = db.Column(db.Integer, nullable=False)
    candid = db.Column(db.BigInteger, nullable=True, default=None)
    isdiffpos = db.Column(db.String(1), nullable=False)
    tblid = db.Column(db.BigInteger, nullable=True, default=None)
    nid = db.Column(db.Integer, nullable=True, default=None)
    rcid = db.Column(db.Integer, nullable=True, default=None)
    field = db.Column(db.Integer, nullable=True, default=None)
    xpos = db.Column(db.Float, nullable=True, default=None)
    ypos = db.Column(db.Float, nullable=True, default=None)
    location = db.Column(Geography('POINT', srid=DB_SRID), nullable=False, index=True)
    magpsf = db.Column(db.Float, nullable=False, index=True)
    sigmapsf = db.Column(db.Float, nullable=False, index=True)
    deltamaglatest = db.Column(db.Float, nullable=True, default=None, index=True)
    deltamagref = db.Column(db.Float, nullable=True, default=None, index=True)
    chipsf = db.Column(db.Float, nullable=True, default=None)
    magap = db.Column(db.Float, nullable=True, default=None, index=True)
    sigmagap = db.Column(db.Float, nullable=True, default=None)
    distnr = db.Column(db.Float, nullable=True, default=None)
    magnr = db.Column(db.Float, nullable=True, default=None)
    sigmagnr = db.Column(db.Float, nullable=True, default=None)
    chinr = db.Column(db.Float, nullable=True, default=None)
    sharpnr = db.Column(db.Float, nullable=True, default=None)
    sky = db.Column(db.Float, nullable=True, default=None)
    magdiff = db.Column(db.Float, nullable=True, default=None)
    fwhm = db.Column(db.Float, nullable=True, default=None, index=True)
    classtar = db.Column(db.Float, nullable=True, default=None, index=True)
    mindtoedge = db.Column(db.Float, nullable=True, default=None)
    magfromlim = db.Column(db.Float, nullable=True, default=None)
    seeratio = db.Column(db.Float, nullable=True, default=None)
    aimage = db.Column(db.Float, nullable=True, default=None)
    bimage = db.Column(db.Float, nullable=True, default=None)
    aimagerat = db.Column(db.Float, nullable=True, default=None)
    bimagerat = db.Column(db.Float, nullable=True, default=None)
    elong = db.Column(db.Float, nullable=True, default=None, index=True)
    nneg = db.Column(db.Integer, nullable=True, default=None)
    nbad = db.Column(db.Integer, nullable=True, default=None)
    rb = db.Column(db.Float, nullable=True, default=None, index=True)
    rbversion = db.Column(db.String(DB_VARCHAR), nullable=False, default='')
    ssdistnr = db.Column(db.Float, nullable=True, default=None, index=True)
    ssmagnr = db.Column(db.Float, nullable=True, default=None)
    ssnamenr = db.Column(db.String(DB_VARCHAR), nullable=False, default='')
    sumrat = db.Column(db.Float, nullable=True, default=None)
    magapbig = db.Column(db.Float, nullable=True, default=None)
    sigmagapbig = db.Column(db.Float, nullable=True, default=None)
    ranr = db.Column(db.Float, nullable=False)
    decnr = db.Column(db.Float, nullable=False)
    ndethist = db.Column(db.Integer, nullable=False)
    ncovhist = db.Column(db.Integer, nullable=False)
    jdstarthist = db.Column(db.Float, nullable=True, default=None)
    jdendhist = db.Column(db.Float, nullable=True, default=None)
    scorr = db.Column(db.Float, nullable=True)
    tooflag = db.Column(db.SmallInteger, nullable=False, default=0)
    gal_l = db.Column(db.Float, nullable=False, index=True)
    gal_b = db.Column(db.Float, nullable=False, index=True)
    objectidps1 = db.Column(db.BigInteger, nullable=True, default=None, index=True)
    sgmag1 = db.Column(db.Float, nullable=True, default=None)
    srmag1 = db.Column(db.Float, nullable=True, default=None)
    simag1 = db.Column(db.Float, nullable=True, default=None)
    szmag1 = db.Column(db.Float, nullable=True, default=None)
    sgscore1 = db.Column(db.Float, nullable=True, default=None)
    distpsnr1 = db.Column(db.Float, nullable=True, default=None)
    objectidps2 = db.Column(db.BigInteger, nullable=True, default=None, index=True)
    sgmag2 = db.Column(db.Float, nullable=True, default=None)
    srmag2 = db.Column(db.Float, nullable=True, default=None)
    simag2 = db.Column(db.Float, nullable=True, default=None)
    szmag2 = db.Column(db.Float, nullable=True, default=None)
    sgscore2 = db.Column(db.Float, nullable=True, default=None)
    distpsnr2 = db.Column(db.Float, nullable=True, default=None)
    objectidps3 = db.Column(db.BigInteger, nullable=True, default=None, index=True)
    sgmag3 = db.Column(db.Float, nullable=True, default=None)
    srmag3 = db.Column(db.Float, nullable=True, default=None)
    simag3 = db.Column(db.Float, nullable=True, default=None)
    szmag3 = db.Column(db.Float, nullable=True, default=None)
    sgscore3 = db.Column(db.Float, nullable=True, default=None)
    distpsnr3 = db.Column(db.Float, nullable=True, default=None)
    nmtchps = db.Column(db.Integer, nullable=False)
    rfid = db.Column(db.BigInteger, nullable=False)
    jdstartref = db.Column(db.Float, nullable=False)
    jdendref = db.Column(db.Float, nullable=False)
    nframesref = db.Column(db.Integer, nullable=False)
    cutoutScienceFileName = db.Column(db.String(DB_VARCHAR), nullable=True, default=None)
    cutoutTemplateFileName = db.Column(db.String(DB_VARCHAR), nullable=True, default=None)
    cutoutDifferenceFileName = db.Column(db.String(DB_VARCHAR), nullable=True, default=None)
    dsnrms = db.Column(db.Float, nullable=True, default=None)
    ssnrms = db.Column(db.Float, nullable=True, default=None)
    dsdiff = db.Column(db.Float, nullable=True, default=None)
    magzpsci = db.Column(db.Float, nullable=True, default=None)
    magzpsciunc = db.Column(db.Float, nullable=True, default=None)
    magzpscirms = db.Column(db.Float, nullable=True, default=None)
    nmatches = db.Column(db.Integer, nullable=True, default=None)
    clrcoeff = db.Column(db.Float, nullable=True, default=None)
    clrcounc = db.Column(db.Float, nullable=True, default=None)
    zpclrcov = db.Column(db.Float, nullable=True, default=None)
    zpmed = db.Column(db.Float, nullable=True, default=None)
    clrmed = db.Column(db.Float, nullable=True, default=None)
    clrrms = db.Column(db.Float, nullable=True, default=None)
    neargaia = db.Column(db.Float, nullable=True, default=None)
    neargaiabright = db.Column(db.Float, nullable=True, default=None)
    maggaia = db.Column(db.Float, nullable=True, default=None)
    maggaiabright = db.Column(db.Float, nullable=True, default=None)
    exptime = db.Column(db.Float, nullable=True, default=None)
    drb = db.Column(db.Float, nullable=True, default=None)
    drbversion = db.Column(db.String(DB_VARCHAR_32), nullable=True, default='')

    # +
    # getter decorator(s):
    # -
    @property
    def ra(self):
        ra = shape.to_shape(self.location).x
        if ra <= 0.0:
            ra += 360.0
        return ra

    @property
    def dec(self):
        return shape.to_shape(self.location).y

    @property
    def prv_candidate(self):
        point = db.session.scalar(self.location.ST_AsText())
        query = db.session.query(ZtfAlert).filter(
            ZtfAlert.id != self.id,
            ZtfAlert.location.ST_DWithin(
                f'srid={DB_SRID};{point}', _degrees_to_meters(ZTF_PREVIOUS_CANDIDATES_RADIUS)))
        return query.order_by(ZtfAlert.jd.desc())

    @property
    def wall_time(self):
        t = Time(self.jd, format='jd')
        return t.datetime

    @property
    def wall_time_format(self):
        return f'{self.wall_time.year}/{str(self.wall_time.month).zfill(2)}/{str(self.wall_time.day).zfill(2)}'

    @property
    def avro(self):
        """ http://localhost/sassy/ztf/files/2020/05/22/1237486751415010006.avro """
        if SASSY_APP_HOST.lower() == 'localhost' and int(SASSY_APP_PORT) == 5000:
            _old_str = f'{SASSY_APP_HOST.lower()}'
            _new_str = f'{SASSY_APP_HOST.lower()}:{SASSY_APP_PORT}'
            return f'{SASSY_APP_ZTF_FILES_URL}/{self.wall_time_format}/{self.alert_candid}.avro'.replace(_old_str, _new_str)
        else:
            return f'{SASSY_APP_ZTF_FILES_URL}/{self.wall_time_format}/{self.alert_candid}.avro'

    @property
    def avro_packet(self):
        response = requests.get(self.avro)
        freader = fastavro.reader(io.BytesIO(response.content))
        for packet in freader:
            if packet['candidate']['candid'] == self.candid:
                return packet
        return None

    @property
    def cutoutScience(self):
        return self.avro_packet['cutoutScience']

    @property
    def cutoutTemplate(self):
        return self.avro_packet['cutoutTemplate']

    @property
    def cutoutDifference(self):
        return self.avro_packet['cutoutDifference']

    @property
    def pretty_serialized(self):
        return json.dumps(self.serialized(prv_candidate=True), indent=2)

    @property
    def filter(self):
        return ZTF_FILTERS[self.fid - 1]

    def serialized(self, prv_candidate=False):
        return {
            'sid': self.id,
            'objectId': self.objectId,
            'publisher': self.publisher,
            'candid': self.alert_candid,
            'avro': self.avro,
            'prv_candidate': ZtfAlert.serialize_list(self.prv_candidate) if prv_candidate else None,
            'candidate': {
                'jd': self.jd,
                'wall_time': self.wall_time,
                'fid': self.fid,
                'filter': self.filter,
                'pid': self.pid,
                'diffmaglim': self.diffmaglim,
                'pdiffimfilename': self.pdiffimfilename,
                'programpi': self.programpi,
                'programid': self.programid,
                'candid': self.candid,
                'isdiffpos': self.isdiffpos,
                'tblid': self.tblid,
                'nid': self.nid,
                'rcid': self.rcid,
                'field': self.field,
                'xpos': self.xpos,
                'ypos': self.ypos,
                'ra': self.ra,
                'dec': self.dec,
                'l': self.gal_l,
                'b': self.gal_b,
                'magpsf': self.magpsf,
                'sigmapsf': self.sigmapsf,
                'deltamaglatest': self.deltamaglatest,
                'deltamagref': self.deltamagref,
                'chipsf': self.chipsf,
                'magap': self.magap,
                'distnr': self.distnr,
                'sigmagap': self.sigmagap,
                'magnr': self.magnr,
                'sigmagnr': self.sigmagnr,
                'chinr': self.chinr,
                'sharpnr': self.sharpnr,
                'sky': self.sky,
                'magdiff': self.magdiff,
                'fwhm': self.fwhm,
                'classtar': self.classtar,
                'mindtoedge': self.mindtoedge,
                'magfromlim': self.magfromlim,
                'seeratio': self.seeratio,
                'aimage': self.aimage,
                'bimage': self.bimage,
                'aimagerat': self.aimagerat,
                'bimagerat': self.bimagerat,
                'elong': self.elong,
                'nneg': self.nneg,
                'nbad': self.nbad,
                'rb': self.rb,
                'rbversion': self.rbversion,
                'ssdistnr': self.ssdistnr,
                'ssmagnr': self.ssmagnr,
                'ssnamenr': self.ssnamenr,
                'sumrat': self.sumrat,
                'magapbig': self.magapbig,
                'sigmagapbig': self.sigmagapbig,
                'ranr': self.ranr,
                'decnr': self.decnr,
                'ndethist': self.ndethist,
                'ncovhist': self.ncovhist,
                'jdstarthist': self.jdstarthist,
                'jdendhist': self.jdendhist,
                'scorr': self.scorr,
                'tooflag': self.tooflag,
                'objectidps1': self.objectidps1,
                'sgmag1': self.sgmag1,
                'srmag1': self.srmag1,
                'simag1': self.simag1,
                'szmag1': self.szmag1,
                'sgscore1': self.sgscore1,
                'distpsnr1': self.distpsnr1,
                'objectidps2': self.objectidps2,
                'sgmag2': self.sgmag2,
                'srmag2': self.srmag2,
                'simag2': self.simag2,
                'szmag2': self.szmag2,
                'sgscore2': self.sgscore2,
                'distpsnr2': self.distpsnr2,
                'objectidps3': self.objectidps3,
                'sgmag3': self.sgmag3,
                'srmag3': self.srmag3,
                'simag3': self.simag3,
                'szmag3': self.szmag3,
                'sgscore3': self.sgscore3,
                'distpsnr3': self.distpsnr3,
                'nmtchps': self.nmtchps,
                'rfid': self.rfid,
                'jdstartref': self.jdstartref,
                'jdendref': self.jdendref,
                'nframesref': self.nframesref,
                'dsnrms': self.dsnrms,
                'ssnrms': self.ssnrms,
                'dsdiff': self.dsdiff,
                'magzpsci': self.magzpsci,
                'magzpsciunc': self.magzpsciunc,
                'magzpscirms': self.magzpscirms,
                'nmatches': self.nmatches,
                'clrcoeff': self.clrcoeff,
                'clrcounc': self.clrcounc,
                'zpclrcov': self.zpclrcov,
                'zpmed': self.zpmed,
                'clrmed': self.clrmed,
                'clrrms': self.clrrms,
                'neargaia': self.neargaia,
                'neargaiabright': self.neargaiabright,
                'maggaia': self.maggaia,
                'maggaiabright': self.maggaiabright,
                'exptime': self.exptime,
                'drb': self.drb,
                'drbversion': self.drbversion,
            }
        }

    def get_csv(self):
        _keys = ['jd', 'fid', 'magpsf', 'sigmapsf', 'diffmaglim']
        _filters = ['x', 'g', 'r', 'i']
        _previous = ZtfAlert.serialize_list(self.prv_candidate)
        _csv = []
        for _c in _previous:
            if 'candidate' in _c and all(_k in _c['candidate'] for _k in _keys):
                _csv.append({
                    'jd': _c['candidate']['jd'],
                    'isot': Time(_c['candidate']['jd'], format='jd').isot,
                    'filter': _filters[_c['candidate']['fid']],
                    'magpsf': _c['candidate']['magpsf'],
                    'sigmapsf': _c['candidate']['sigmapsf'],
                    'diffmaglim': _c['candidate']['diffmaglim']
                })
        return pd.DataFrame(_csv)

    def get_photometry(self):
        filter_mapping = ['x', 'g', 'r', 'i']
        prv_candidates = ZtfAlert.serialize_list(self.prv_candidate)
        photometry = {}
        index = 0
        for candidate in prv_candidates:
            values = candidate['candidate']
            photometry[index] = {}
            for key in values.keys():
                if key in ['diffmaglim', 'magpsf', 'sigmapsf']:
                    photometry[index][key] = values[key]
                elif key == 'fid':
                    photometry[index]['filter'] = filter_mapping[values[key]]
                elif key == 'jd':
                    photometry[index][key] = values[key]
                    photometry[index]['isot'] = Time(values[key], format='jd').isot
            index += 1
        photometry[index] = {
            'jd': self.jd,
            'isot': Time(self.jd, format='jd').isot,
            'filter': filter_mapping[self.fid],
            'magpsf': self.magpsf,
            'sigmapsf': self.sigmapsf,
            'diffmaglim': self.diffmaglim
        }
        return photometry

    def get_non_detections(self):
        non_detections = []
        filter_mapping = {1: 'g', 2: 'r', 3: 'i'}
        prv_candidates = ZtfAlert.serialize_list(self.prv_candidate)
        for _prv in prv_candidates:
            if 'candid' in _prv and _prv['candid'] is None:
                if all(_k in _prv for _k in ['diffmaglim', 'jd', 'fid']):
                    non_detections.append(
                        {'diffmaglim': float(_prv['diffmaglim']), 'jd': float(_prv['jd']),
                         'filter': filter_mapping.get(_prv['fid'], ''), 'isot': jd_to_isot(_prv['jd'])})
        return _non_detections

    # +
    # (overload) method: __str__()
    # -
    def __str__(self):
        return self.objectId

    # +
    # (static) method: serialize_list()
    # -
    @staticmethod
    def serialize_list(m_alerts):
        return [_a.serialized() for _a in m_alerts]


# +
# (hidden) function: _degrees_to_meters()
# -
def _degrees_to_meters(degrees=0.0):
    _degrees = degrees % 360.0
    return 2.0 * math.pi * EARTH_RADIUS_METERS * _degrees / 360.0


# +
# (hidden) function: _meters_to_degrees()
# -
def _meters_to_degrees(meters=0.0):
    _meters = (meters * 360.0) / (2.0 * math.pi * EARTH_RADIUS_METERS)
    return _meters % 360.0


# +
# (hidden) function: _get_simbad2k_coords()
# -
# noinspection PyBroadException
def _get_simbad2k_coords(objectname=''):
    try:
        response = requests.get(f'https://simbad2k.lco.global/{objectname}?target_type=sidereal')
        response.raise_for_status()
        result = response.json()
        return result['ra_d'], result['dec_d']
    except Exception:
        return math.nan, math.nan


# +
# (hidden) function: _get_astropy_coords()
# -
# noinspection PyBroadException
def _get_astropy_coords(objectname=''):
    try:
        _obj = SkyCoord.from_name(objectname)
        return _obj.ra.value, _obj.dec.value
    except Exception:
        return math.nan, math.nan


# +
# function: ztf_get_text()
# -
def ztf_get_text():
    return __text__


# +
# function: ztf_filters() alphabetically
# -
def ztf_filters(query, request_args):

    # return records within a cone search on a named object with csv-args: name, radius (API: ?astrocone=ngc1316,0.5)
    if request_args.get('astrocone'):
        objectname, radius = request_args['astrocone'].split(',')
        ra, dec = _get_astropy_coords(objectname)
        query = query.filter(
            ZtfAlert.location.ST_DWithin(f'srid={DB_SRID};POINT({ra} {dec})', _degrees_to_meters(float(radius)))
        )

    # return records with galactic b >= value in degrees (API: ?b__gte=20.0)
    if request_args.get('b__gte'):
        query = query.filter(ZtfAlert.gal_b >= float(request_args['b__gte']))

    # return records with galactic b <= value in degrees (API: ?b__lte=20.0)
    if request_args.get('b__lte'):
        query = query.filter(ZtfAlert.gal_b <= float(request_args['b__lte']))

    # return records with candid (API: ?candid=xxdcdcdvfwd) <<< CHECK!
    if request_args.get('candid'):
        query = query.filter(ZtfAlert.alert_candid == request_args['candid'])

    # return records with a star/galaxy score >= value (API: ?clastar__gte=0.4)
    if request_args.get('classtar__gte'):
        query = query.filter(ZtfAlert.classtar >= float(request_args['classtar__gte']))

    # return records with a star/galaxy score <= value (API: ?clastar__lte=0.4)
    if request_args.get('classtar__lte'):
        query = query.filter(ZtfAlert.classtar <= float(request_args['classtar__lte']))

    # return records within a cone search with csv-args: ra, dec, radius (API: ?cone=23.5,29.2,0.5)
    if request_args.get('cone'):
        ra, dec, radius = request_args['cone'].split(',')
        query = query.filter(
            ZtfAlert.location.ST_DWithin(f'srid={DB_SRID};POINT({ra} {dec})', _degrees_to_meters(float(radius)))
        )

    # return records with an Dec >= value in degrees (API: ?dec__gte=20.0)
    if request_args.get('dec__gte'):
        query = query.filter(cast(ZtfAlert.location, Geometry).ST_Y() >= float(request_args['dec__gte']))

    # return records with an Dec <= value in degrees (API: ?dec__lte=20.0)
    if request_args.get('dec__lte'):
        query = query.filter(cast(ZtfAlert.location, Geometry).ST_Y() <= float(request_args['dec__lte']))

    # return records with a magnitude difference >= abs value (API: ?deltamaglatest__gte=1.0)
    if request_args.get('deltamaglatest__gte'):
        query = query.filter(ZtfAlert.deltamaglatest >= float(request_args['deltamaglatest__gte']))

    # return records with a magnitude difference <= abs value (API: ?deltamaglatest__lte=1.0)
    if request_args.get('deltamaglatest__lte'):
        query = query.filter(ZtfAlert.deltamaglatest <= float(request_args['deltamaglatest__lte']))

    # return records with a mag diff on the reference image >= value (API: ?deltamagref__gte=1.0)
    if request_args.get('deltamagref__gte'):
        query = query.filter(ZtfAlert.deltamagref >= float(request_args['deltamagref__gte']))

    # return records with a mag diff on the reference image <= value (API: ?deltamagref__gte=1.0)
    if request_args.get('deltamagref__lte'):
        query = query.filter(ZtfAlert.deltamagref <= float(request_args['deltamagref__lte']))

    # return records where the distance to the nearest source >= value (API: ?distnr__gte=1.0)
    if request_args.get('distnr__gte'):
        query = query.filter(ZtfAlert.distnr >= float(request_args['distnr__gte']))

    # return records where the distance to the nearest source <= value (API: ?distnr__lte=1.0)
    if request_args.get('distnr__lte'):
        query = query.filter(ZtfAlert.distnr <= float(request_args['distnr__lte']))

    # return records where the deep-learning real-bogus score >= value (API: ?drb__gte=1.0)
    if request_args.get('drb__gte'):
        query = query.filter(ZtfAlert.drb >= float(request_args['drb__gte']))

    # return records where the deep-learning real-bogus score <= value (API: ?drb__lte=1.0)
    if request_args.get('drb__lte'):
        query = query.filter(ZtfAlert.drb <= float(request_args['drb__lte']))

    # return records where the exposure time >= value (API: ?exptime__gte=30.0)
    if request_args.get('exptime__gte'):
        query = query.filter(ZtfAlert.exptime >= float(request_args['exptime__gte']))

    # return records where the exposure time <= value (API: ?exptime__lte=30.0)
    if request_args.get('exptime__lte'):
        query = query.filter(ZtfAlert.exptime <= float(request_args['exptime__lte']))

    # return records with a given filter (API: ?filter=g)
    if request_args.get('filter'):
        query = query.filter(ZtfAlert.fid == ZTF_FILTERS.index(request_args['filter']) + 1)

    # return records with a fwhm >= value (API: ?fwhm__gte=1.123)
    if request_args.get('fwhm__gte'):
        query = query.filter(ZtfAlert.fwhm <= float(request_args['fwhm__gte']))

    # return records with a fwhm <= value (API: ?fwhm__lte=1.123)
    if request_args.get('fwhm__lte'):
        query = query.filter(ZtfAlert.fwhm <= float(request_args['fwhm__lte']))

    # return records with a JD >= date (API: ?jd__gte=2458302.6906713)
    if request_args.get('jd__gte'):
        query = query.filter(ZtfAlert.jd >= request_args['jd__gte'])

    # return records with a JD <= date (API: ?jd__lte=2458302.6906713)
    if request_args.get('jd__lte'):
        query = query.filter(ZtfAlert.jd <= request_args['jd__lte'])

    # return records with galactic l >= value in degrees (API: ?l__gte=20.0)
    if request_args.get('l__gte'):
        query = query.filter(ZtfAlert.gal_l >= float(request_args['l__gte']))

    # return records with galactic l <= value in degrees (API: ?l__lte=20.0)
    if request_args.get('l__lte'):
        query = query.filter(ZtfAlert.gal_l <= float(request_args['l__lte']))

    # return records with a magap >= value (API: ?magap__gte=0.4)
    if request_args.get('magap__gte'):
        query = query.filter(ZtfAlert.magap >= float(request_args['magap__gte']))

    # return records with a magap <= value (API: ?magap__lte=0.4)
    if request_args.get('magap__lte'):
        query = query.filter(ZtfAlert.magap <= float(request_args['magap__lte']))

    # return records with a magpsf >= value (API: ?magpsf__gte=20.0)
    if request_args.get('magpsf__gte'):
        query = query.filter(ZtfAlert.magpsf >= float(request_args['magpsf__gte']))

    # return records with a magpsf <= value (API: ?magpsf__lte=20.0)
    if request_args.get('magpsf__lte'):
        query = query.filter(ZtfAlert.magpsf <= float(request_args['magpsf__lte']))

    # return records within a cone search on a named object with csv-args: name, radius (API: ?objectcone=ngc1316,0.5)
    if request_args.get('objectcone'):
        objectname, radius = request_args['objectcone'].split(',')
        ra, dec = _get_simbad2k_coords(objectname)
        query = query.filter(
            ZtfAlert.location.ST_DWithin(f'srid={DB_SRID};POINT({ra} {dec})', _degrees_to_meters(float(radius)))
        )

    # return records near a PS1 object ID (API: ?objectidps=178183210973037920)
    if request_args.get('objectidps'):
        psid = int(request_args['objectidps'])
        query = query.filter(
            (ZtfAlert.objectidps1 == psid) | (ZtfAlert.objectidps2 == psid) | (ZtfAlert.objectidps3 == psid))

    # return records with objectId (API: ?objectId=ZTFsdneuenf)
    if request_args.get('objectId'):
        query = query.filter(ZtfAlert.objectId == request_args['objectId'])

    # return records with an RA >= value in degrees (API: ?ra__gte=20.0)
    if request_args.get('ra__gte'):
        ra = float(request_args['ra__gte'])
        query = query.filter(cast(ZtfAlert.location, Geometry).ST_X() >= ra)

    # return records with an RA <= value in degrees (API: ?ra__lte=20.0)
    if request_args.get('ra__lte'):
        ra = float(request_args['ra__lte'])
        query = query.filter(cast(ZtfAlert.location, Geometry).ST_X() <= ra)

    # return records with a real/bogus score >= value (API: ?rb__gte=0.3)
    if request_args.get('rb__gte'):
        query = query.filter(ZtfAlert.rb >= float(request_args['rb__gte']))

    # return records with a real/bogus score <= value (API: ?rb__lte=0.3)
    if request_args.get('rb__lte'):
        query = query.filter(ZtfAlert.rb >= float(request_args['rb__lte']))

    # return records with sid = value (API: ?sid=20)
    if request_args.get('sid'):
        query = query.filter(ZtfAlert.id == int(request_args['sid']))

    # return records with sid >= value (API: ?sid__gte=20.0)
    if request_args.get('sid__gte'):
        query = query.filter(ZtfAlert.id >= int(request_args['sid__gte']))

    # return records with sid <= value (API: ?sid__lte=20.0)
    if request_args.get('sid__lte'):
        query = query.filter(ZtfAlert.id <= int(request_args['sid__lte']))

    # return records with a sigmapsf >= value (API: ?sigmapsf__gte=0.4)
    if request_args.get('sigmapsf__gte'):
        query = query.filter(ZtfAlert.sigmapsf <= float(request_args['sigmapsf__gte']))

    # return records with a sigmapsf <= value (API: ?sigmapsf__lte=0.4)
    if request_args.get('sigmapsf__lte'):
        query = query.filter(ZtfAlert.sigmapsf <= float(request_args['sigmapsf__lte']))

    # return records with ssnamenr (API: ?ssnamenr=16495)
    if request_args.get('ssnamenr'):
        query = query.filter(ZtfAlert.ssnamenr == request_args['ssnamenr'])

    # return records with a wall time >= date (API: ?time__gte=2018-07-17)
    if request_args.get('time__gte'):
        a_time = Time(request_args['time__gte'], format='isot')
        query = query.filter(ZtfAlert.jd >= a_time.jd)

    # return records with a wall time <= date (API: ?time__lte=2018-07-17)
    if request_args.get('time__lte'):
        a_time = Time(request_args['time__lte'], format='isot')
        query = query.filter(ZtfAlert.jd <= a_time.jd)

    # sort results
    sort_by = request_args.get('sort_value', 'jd')
    sort_order = request_args.get('sort_order', 'desc')
    if sort_order == 'desc':
        query = query.order_by(getattr(ZtfAlert, sort_by).desc())
    elif sort_order == 'asc':
        query = query.order_by(getattr(ZtfAlert, sort_by).asc())

    # return query
    return query


# +
# function: ztf_cli_db()
# -
# noinspection PyBroadException
def ztf_cli_db(iargs=None):

    # check input(s)
    if iargs is None:
        raise Exception('Invalid arguments')

    # if --text is present, describe of the catalog
    if iargs.text:
        print(ztf_get_text())
        return

    # set default(s)
    request_args = {}

    # get input(s) alphabetically
    if iargs.astrocone:
        request_args['astrocone'] = f'{iargs.astrocone}'
    if iargs.b__gte:
        request_args['b__gte'] = f'?{iargs.b__gte}'
    if iargs.b__lte:
        request_args['b__lte'] = f'{iargs.b__lte}'
    if iargs.candid:
        request_args['candid'] = f'{iargs.candid}'
    if iargs.classtar__gte:
        request_args['classtar__gte'] = f'{iargs.classtar__gte}'
    if iargs.classtar__lte:
        request_args['classtar__lte'] = f'{iargs.classtar__lte}'
    if iargs.cone:
        request_args['cone'] = f'{iargs.cone}'
    if iargs.dec__gte:
        request_args['dec__gte'] = f'{iargs.dec__gte}'
    if iargs.dec__lte:
        request_args['dec__lte'] = f'{iargs.dec__lte}'
    if iargs.deltamaglatest__gte:
        request_args['deltamaglatest__gte'] = f'{iargs.deltamaglatest__gte}'
    if iargs.deltamaglatest__lte:
        request_args['deltamaglatest__lte'] = f'{iargs.deltamaglatest__lte}'
    if iargs.deltamagref__gte:
        request_args['deltamagref__gte'] = f'{iargs.deltamagref__gte}'
    if iargs.deltamagref__lte:
        request_args['deltamagref__lte'] = f'{iargs.deltamagref__lte}'
    if iargs.distnr__gte:
        request_args['distnr__gte'] = f'{iargs.distnr__gte}'
    if iargs.distnr__lte:
        request_args['distnr__lte'] = f'{iargs.distnr__lte}'
    if iargs.drb__gte:
        request_args['drb__gte'] = f'{iargs.drb__gte}'
    if iargs.drb__lte:
        request_args['drb__lte'] = f'{iargs.drb__lte}'
    if iargs.exptime__gte:
        request_args['exptime__gte'] = f'{iargs.exptime__gte}'
    if iargs.exptime__lte:
        request_args['exptime__lte'] = f'{iargs.exptime__lte}'
    if iargs.filter:
        request_args['filter'] = f'{iargs.filter}'
    if iargs.fwhm__gte:
        request_args['fwhm__gte'] = f'{iargs.fwhm__gte}'
    if iargs.fwhm__lte:
        request_args['fwhm__lte'] = f'{iargs.fwhm__lte}'
    if iargs.jd__gte:
        request_args['jd__gte'] = f'{iargs.jd__gte}'
    if iargs.jd__lte:
        request_args['jd__lte'] = f'{iargs.jd__lte}'
    if iargs.l__gte:
        request_args['l__gte'] = f'{iargs.l__gte}'
    if iargs.l__lte:
        request_args['l__lte'] = f'{iargs.l__lte}'
    if iargs.magap__gte:
        request_args['magap__gte'] = f'{iargs.magap__gte}'
    if iargs.magap__lte:
        request_args['magap__lte'] = f'{iargs.magap__lte}'
    if iargs.magpsf__gte:
        request_args['magpsf__gte'] = f'{iargs.magpsf__gte}'
    if iargs.magpsf__lte:
        request_args['magpsf__lte'] = f'{iargs.magpsf__lte}'
    if iargs.objectcone:
        request_args['objectcone'] = f'{iargs.objectcone}'
    if iargs.objectidps:
        request_args['objectidps'] = f'{iargs.objectidps}'
    if iargs.objectId:
        request_args['objectId'] = f'{iargs.objectId}'
    if iargs.ra__gte:
        request_args['ra__gte'] = f'{iargs.ra__gte}'
    if iargs.ra__lte:
        request_args['ra__lte'] = f'{iargs.ra__lte}'
    if iargs.rb__gte:
        request_args['rb__gte'] = f'{iargs.rb__gte}'
    if iargs.rb__lte:
        request_args['rb__lte'] = f'{iargs.rb__lte}'
    if iargs.sid:
        request_args['sid'] = f'{iargs.sid}'
    if iargs.sid__gte:
        request_args['sid__gte'] = f'{iargs.sid__gte}'
    if iargs.sid__lte:
        request_args['sid__lte'] = f'{iargs.sid__lte}'
    if iargs.sigmagpsf__gte:
        request_args['sigmagpsf__gte'] = f'{iargs.sigmagpsf__gte}'
    if iargs.sigmagpsf__lte:
        request_args['sigmagpsf__lte'] = f'{iargs.sigmagpsf__lte}'
    if iargs.ssnamenr:
        request_args['ssnamenr'] = f'{iargs.ssnamenr}'
    if iargs.time__gte:
        request_args['time__gte'] = f'{iargs.time__gte}'
    if iargs.time__lte:
        request_args['time__lte'] = f'{iargs.time__lte}'

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
        query = session.query(ZtfAlert)
        if iargs.verbose:
            print(f'query = {query}')
        query = ztf_filters(query, request_args)
        if iargs.verbose:
            print(f'query = {query}')
        query = query.order_by(ZtfAlert.jd.desc())
        if iargs.verbose:
            print(f'query = {query}')
    except Exception as e:
        raise Exception(f'Failed to execute query, error={e}')

    # dump output to file
    if isinstance(iargs.output, str) and iargs.output.strip() != '':
        try:
            with open(iargs.output, 'w') as _wf:
                _wf.write(f'#sid,candid,objectId,ra,dec,mag,exptime,publisher,avro,prv_candidate,aimage,'
                          f'aimagerat,b,bimage,bimagerat,candid,chinr,chipsf,classtar,clrcoeff,clrcounc,clrmed,clrrms,'
                          f'decnr,deltamaglatest,deltamagref,diffmaglim,distnr,distpsnr1,distpsnr2,distpsnr3,dsdiff,'
                          f'dsnrms,drb,drbversion,elong,fid,field,filter,fwhm,isdiffpos,jd,jdendhist,'
                          f'jdendref,jdstarthist,jdstartref,'
                          f'l,magap,magapbig,magdiff,magfromlim,maggaia,maggaiabright,magnr,magzpsci,magzpscirms,'
                          f'magzpsciunc,mindtoedge,nbad,ncovhist,ndethist,neargaia,neargaiabright,nframesref,nid,'
                          f'nmatches,nmtchps,nneg,objectidps1,objectidps2,objectidps3,pdiffimfilename,pid,programid,'
                          f'programpi,ranr,rb,rbversion,rcid,rfid,scorr,seeratio,sgmag1,sgmag2,sgmag3,sgscore1,'
                          f'sgscore2,sgscore3,sharpnr,sigmagap,sigmagapbig,sigmagnr,sigmapsf,simag1,simag2,simag3,'
                          f'sky,srmag1,srmag2,srmag3,ssdistnr,ssmagnr,ssnamenr,ssnrms,sumrat,szmag1,szmag2,szmag3,'
                          f'tblid,tooflag,wall_time,xpos,ypos,zpclrcov,zpmed\n')
                for _e in ZtfAlert.serialize_list(query.all()):
                    _wf.write(f"{_e['sid']},{_e['candid']},{_e['objectId']},{_e['candidate']['ra']},"
                              f"{_e['candidate']['dec']},{_e['candidate']['magpsf']},{_e['candidate']['exptime']},"
                              f"{_e['publisher']},{_e['avro']},{_e['prv_candidate']},{_e['candidate']['aimage']},"
                              f"{_e['candidate']['aimagerat']},{_e['candidate']['b']},{_e['candidate']['bimage']},"
                              f"{_e['candidate']['bimagerat']},{_e['candidate']['candid']},{_e['candidate']['chinr']},"
                              f"{_e['candidate']['chipsf']},{_e['candidate']['classtar']},"
                              f"{_e['candidate']['clrcoeff']},{_e['candidate']['clrcounc']},"
                              f"{_e['candidate']['clrmed']},{_e['candidate']['clrrms']},{_e['candidate']['decnr']},"
                              f"{_e['candidate']['deltamaglatest']},{_e['candidate']['deltamagref']},"
                              f"{_e['candidate']['diffmaglim']},{_e['candidate']['distnr']},"
                              f"{_e['candidate']['distpsnr1']},{_e['candidate']['distpsnr2']},"
                              f"{_e['candidate']['distpsnr3']},{_e['candidate']['dsdiff']},"
                              f"{_e['candidate']['dsnrms']},{_e['candidate']['drb']},{_e['candidate']['drbversion']},"
                              f"{_e['candidate']['elong']},{_e['candidate']['fid']},"
                              f"{_e['candidate']['field']},{_e['candidate']['filter']},{_e['candidate']['fwhm']},"
                              f"{_e['candidate']['isdiffpos']},{_e['candidate']['jd']},{_e['candidate']['jdendhist']},"
                              f"{_e['candidate']['jdendref']},{_e['candidate']['jdstarthist']},"
                              f"{_e['candidate']['jdstartref']}, {_e['candidate']['l']},{_e['candidate']['magap']},"
                              f"{_e['candidate']['magapbig']},{_e['candidate']['magdiff']},"
                              f"{_e['candidate']['magfromlim']},{_e['candidate']['maggaia']},"
                              f"{_e['candidate']['maggaiabright']},{_e['candidate']['magnr']},"
                              f"{_e['candidate']['magzpsci']}, {_e['candidate']['magzpscirms']},"
                              f"{_e['candidate']['magzpsciunc']},{_e['candidate']['mindtoedge']},"
                              f"{_e['candidate']['nbad']},{_e['candidate']['ncovhist']},{_e['candidate']['ndethist']},"
                              f"{_e['candidate']['neargaia']},{_e['candidate']['neargaiabright']},"
                              f"{_e['candidate']['nframesref']}, {_e['candidate']['nid']},"
                              f"{_e['candidate']['nmatches']},{_e['candidate']['nmtchps']},{_e['candidate']['nneg']},"
                              f"{_e['candidate']['objectidps1']},{_e['candidate']['objectidps2']},"
                              f"{_e['candidate']['objectidps3']},{_e['candidate']['pdiffimfilename']},"
                              f"{_e['candidate']['pid']}, {_e['candidate']['programid']},"
                              f"{_e['candidate']['programpi']},{_e['candidate']['ranr']},{_e['candidate']['rb']},"
                              f"{_e['candidate']['rbversion']},{_e['candidate']['rcid']},{_e['candidate']['rfid']},"
                              f"{_e['candidate']['scorr']},{_e['candidate']['seeratio']},{_e['candidate']['sgmag1']},"
                              f"{_e['candidate']['sgmag2']},{_e['candidate']['sgmag3']},{_e['candidate']['sgscore1']},"
                              f"{_e['candidate']['sgscore2']},{_e['candidate']['sgscore3']},"
                              f"{_e['candidate']['sharpnr']},{_e['candidate']['sigmagap']},"
                              f"{_e['candidate']['sigmagapbig']}, {_e['candidate']['sigmagnr']},"
                              f"{_e['candidate']['sigmapsf']},{_e['candidate']['simag1']},{_e['candidate']['simag2']},"
                              f"{_e['candidate']['simag3']},{_e['candidate']['sky']},{_e['candidate']['srmag1']},"
                              f"{_e['candidate']['srmag2']},{_e['candidate']['srmag3']},{_e['candidate']['ssdistnr']},"
                              f"{_e['candidate']['ssmagnr']},{_e['candidate']['ssnamenr']},{_e['candidate']['ssnrms']},"
                              f"{_e['candidate']['sumrat']},{_e['candidate']['szmag1']},{_e['candidate']['szmag2']},"
                              f"{_e['candidate']['szmag3']},{_e['candidate']['tblid']},{_e['candidate']['tooflag']},"
                              f"{_e['candidate']['wall_time']},{_e['candidate']['xpos']},{_e['candidate']['ypos']},"
                              f"{_e['candidate']['zpclrcov']},{_e['candidate']['zpmed']}\n")
        except Exception:
            pass

    # dump output to screen
    else:
        print(f'#sid,candid,objectId,ra,dec,mag,exptime,publisher,avro,prv_candidate,aimage,aimagerat,b,'
              f'bimage,bimagerat,candid,chinr,chipsf,classtar,clrcoeff,clrcounc,clrmed,clrrms,decnr,deltamaglatest,'
              f'deltamagref,diffmaglim,distnr,distpsnr1,distpsnr2,distpsnr3,dsdiff,dsnrms,drb,drbversion,'
              f'elong,fid,field,filter,fwhm,'
              f'isdiffpos,jd,jdendhist,jdendref,jdstarthist,jdstartref,l,magap,magapbig,magdiff,magfromlim,maggaia,'
              f'maggaiabright,magnr,magzpsci,magzpscirms,magzpsciunc,mindtoedge,nbad,ncovhist,ndethist,neargaia,'
              f'neargaiabright,nframesref,nid,nmatches,nmtchps,nneg,objectidps1,objectidps2,objectidps3,'
              f'pdiffimfilename,pid,programid,programpi,ranr,rb,rbversion,rcid,rfid,scorr,seeratio,sgmag1,sgmag2,'
              f'sgmag3,sgscore1,sgscore2,sgscore3,sharpnr,sigmagap,sigmagapbig,sigmagnr,sigmapsf,simag1,simag2,'
              f'simag3,sky,srmag1,srmag2,srmag3,ssdistnr,ssmagnr,ssnamenr,ssnrms,sumrat,szmag1,szmag2,szmag3,tblid,'
              f'tooflag,wall_time,xpos,ypos,zpclrcov,zpmed')
        for _e in ZtfAlert.serialize_list(query.all()):
            print(f"{_e['sid']},{_e['candid']},{_e['objectId']},{_e['candidate']['ra']},"
                  f"{_e['candidate']['dec']},{_e['candidate']['magpsf']},{_e['candidate']['exptime']},"
                  f"{_e['publisher']},{_e['avro']},{_e['prv_candidate']},{_e['candidate']['aimage']},"
                  f"{_e['candidate']['aimagerat']},{_e['candidate']['b']},{_e['candidate']['bimage']},"
                  f"{_e['candidate']['bimagerat']},{_e['candidate']['candid']},{_e['candidate']['chinr']},"
                  f"{_e['candidate']['chipsf']},{_e['candidate']['classtar']},{_e['candidate']['clrcoeff']},"
                  f"{_e['candidate']['clrcounc']},{_e['candidate']['clrmed']},{_e['candidate']['clrrms']},"
                  f"{_e['candidate']['decnr']},{_e['candidate']['deltamaglatest']},{_e['candidate']['deltamagref']},"
                  f"{_e['candidate']['diffmaglim']},{_e['candidate']['distnr']},{_e['candidate']['distpsnr1']},"
                  f"{_e['candidate']['distpsnr2']},{_e['candidate']['distpsnr3']},{_e['candidate']['dsdiff']},"
                  f"{_e['candidate']['dsnrms']},{_e['candidate']['drb']},{_e['candidate']['drbversion']},"
                  f"{_e['candidate']['elong']},{_e['candidate']['fid']},"
                  f"{_e['candidate']['field']},{_e['candidate']['filter']},{_e['candidate']['fwhm']},"
                  f"{_e['candidate']['isdiffpos']},{_e['candidate']['jd']},{_e['candidate']['jdendhist']},"
                  f"{_e['candidate']['jdendref']},{_e['candidate']['jdstarthist']},{_e['candidate']['jdstartref']},"
                  f"{_e['candidate']['l']},{_e['candidate']['magap']},{_e['candidate']['magapbig']},"
                  f"{_e['candidate']['magdiff']},{_e['candidate']['magfromlim']},{_e['candidate']['maggaia']},"
                  f"{_e['candidate']['maggaiabright']},{_e['candidate']['magnr']},{_e['candidate']['magzpsci']},"
                  f"{_e['candidate']['magzpscirms']},{_e['candidate']['magzpsciunc']},{_e['candidate']['mindtoedge']},"
                  f"{_e['candidate']['nbad']},{_e['candidate']['ncovhist']},{_e['candidate']['ndethist']},"
                  f"{_e['candidate']['neargaia']},{_e['candidate']['neargaiabright']},{_e['candidate']['nframesref']},"
                  f"{_e['candidate']['nid']},{_e['candidate']['nmatches']},{_e['candidate']['nmtchps']},"
                  f"{_e['candidate']['nneg']},{_e['candidate']['objectidps1']},{_e['candidate']['objectidps2']},"
                  f"{_e['candidate']['objectidps3']},{_e['candidate']['pdiffimfilename']},{_e['candidate']['pid']},"
                  f"{_e['candidate']['programid']},{_e['candidate']['programpi']},{_e['candidate']['ranr']},"
                  f"{_e['candidate']['rb']},{_e['candidate']['rbversion']},{_e['candidate']['rcid']},"
                  f"{_e['candidate']['rfid']},{_e['candidate']['scorr']},{_e['candidate']['seeratio']},"
                  f"{_e['candidate']['sgmag1']},{_e['candidate']['sgmag2']},{_e['candidate']['sgmag3']},"
                  f"{_e['candidate']['sgscore1']},{_e['candidate']['sgscore2']},{_e['candidate']['sgscore3']},"
                  f"{_e['candidate']['sharpnr']},{_e['candidate']['sigmagap']},{_e['candidate']['sigmagapbig']},"
                  f"{_e['candidate']['sigmagnr']},{_e['candidate']['sigmapsf']},{_e['candidate']['simag1']},"
                  f"{_e['candidate']['simag2']},{_e['candidate']['simag3']},{_e['candidate']['sky']},"
                  f"{_e['candidate']['srmag1']},{_e['candidate']['srmag2']},{_e['candidate']['srmag3']},"
                  f"{_e['candidate']['ssdistnr']},{_e['candidate']['ssmagnr']},{_e['candidate']['ssnamenr']},"
                  f"{_e['candidate']['ssnrms']},{_e['candidate']['sumrat']},{_e['candidate']['szmag1']},"
                  f"{_e['candidate']['szmag2']},{_e['candidate']['szmag3']},{_e['candidate']['tblid']},"
                  f"{_e['candidate']['tooflag']},{_e['candidate']['wall_time']},{_e['candidate']['xpos']},"
                  f"{_e['candidate']['ypos']},{_e['candidate']['zpclrcov']},{_e['candidate']['zpmed']}")


# +
# function: main()
# -
if __name__ == '__main__':

    # set default(s)
    max_jd = float(Time(Time.now().iso).jd)

    # get command line argument(s) alphabetically
    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description=f'Query ZTF database', formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument(f'--astrocone', help=f'Cone search by name <str, str>')
    _p.add_argument(f'--b__gte', help=f'Galactic b >= <float>')
    _p.add_argument(f'--b__lte', help=f'Galactic b <= <float>')
    _p.add_argument(f'--candid', help=f'Candidate ID <int>')
    _p.add_argument(f'--classtar__gte', help=f'Classification index >= <float>')
    _p.add_argument(f'--classtar__lte', help=f'Classification index <= <float>')
    _p.add_argument(f'--cone', help=f'Cone search <ra, dec, radius>')
    _p.add_argument(f'--dec__gte', help=f'Dec >= <float>')
    _p.add_argument(f'--dec__lte', help=f'Dec <= <float>')
    _p.add_argument(f'--deltamaglatest__gte', help=f'DeltaMagLatest >= <float>')
    _p.add_argument(f'--deltamaglatest__lte', help=f'DeltaMagLatest <= <float>')
    _p.add_argument(f'--deltamagref__gte', help=f'DeltaMagRef >= <float>')
    _p.add_argument(f'--deltamagref__lte', help=f'DeltaMagRef <= <float>')
    _p.add_argument(f'--distnr__gte', help=f'Distance to nearest object >= <float>')
    _p.add_argument(f'--distnr__lte', help=f'Distance to nearest object <= <float>')
    _p.add_argument(f'--drb__gte', help=f'Deep-Learning Real-Bogus score >= <float>')
    _p.add_argument(f'--drb__lte', help=f'Deep-Learning Real-Bogus score <= <float>')
    _p.add_argument(f'--exptime__gte', help=f'Exposire time >= <float>')
    _p.add_argument(f'--exptime__lte', help=f'Exposire time <= <float>')
    _p.add_argument(f'--filter', help=f'filter <str>')
    _p.add_argument(f'--fwhm__gte', help=f'FWHM >= <float>')
    _p.add_argument(f'--fwhm__lte', help=f'FWHM <= <float>')
    _p.add_argument(f'--jd__gte', help=f'Julian Day >= <float>')
    _p.add_argument(f'--jd__lte', help=f'Julian Day <= <float>')
    _p.add_argument(f'--l__gte', help=f'Galactic l >= <float>')
    _p.add_argument(f'--l__lte', help=f'Galactic l <= <float>')
    _p.add_argument(f'--magap__gte', help=f'Aperture magnitude >= <float>')
    _p.add_argument(f'--magap__lte', help=f'Aperture magnitude <= <float>')
    _p.add_argument(f'--magpsf__gte', help=f'Magnitude >= <float>')
    _p.add_argument(f'--magpsf__lte', help=f'Magnitude <= <float>')
    _p.add_argument(f'--objectcone', help=f'Cone search by name <str, str>')
    _p.add_argument(f'--objectidps', help=f'IDPS object <int>')
    _p.add_argument(f'--objectId', help=f'Object ID <str>')
    _p.add_argument(f'--ra__gte', help=f'RA >= <float>')
    _p.add_argument(f'--ra__lte', help=f'RA <= <float>')
    _p.add_argument(f'--rb__gte', help=f'Real-Bogus score >= <float>')
    _p.add_argument(f'--rb__lte', help=f'Real-Bogus score <= <float>')
    _p.add_argument(f'--sid', help=f'SASSy id <int>')
    _p.add_argument(f'--sid__gte', help=f'SASSy id >= <int>')
    _p.add_argument(f'--sid__lte', help=f'SASSy id <= <int>')
    _p.add_argument(f'--sigmagpsf__gte', help=f'Magnitude sigma >= <float>')
    _p.add_argument(f'--sigmagpsf__lte', help=f'Magnitude sigma <= <float>')
    _p.add_argument(f'--ssnamenr', help=f'Solar system name <str>')
    _p.add_argument(f'--time__gte', help=f'ISO time >= <str>')
    _p.add_argument(f'--time__lte', help=f'ISO time <= <str>')

    _p.add_argument(f'--output', default='', help=f'Output file <str>')
    _p.add_argument(f'--text', default=False, action='store_true', help=f'if present, describe the catalog')
    _p.add_argument(f'--verbose', default=False, action='store_true', help=f'if present, produce more verbose output')
    args = _p.parse_args()

    # execute
    if args:
        ztf_cli_db(args)
    else:
        raise Exception(f'Insufficient command line arguments specified\nUse: python {sys.argv[0]} --help') 
