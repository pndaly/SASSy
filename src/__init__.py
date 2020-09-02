#!/usr/bin/env python3


# +
# import(s)
# -
from astropy.time import Time
from astropy.coordinates import Angle
from astropy.coordinates import SkyCoord
from datetime import datetime
from datetime import timedelta

import math
import os
import hashlib
import random


# +
# constant(s)
# -
ISO_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
ISO_PATTERN = '[0-9]{4}-[0-9]{2}-[0-9]{2}[ T?][0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{6}'
ZTF_ZERO_NID = '2017-01-01T00:00:00.000000'
ZTF_ZERO_POINTS = {1: 26.325, 2: 26.275, 3: 25.660}
ZTF_ZERO_POINTS_R = {_v: _k for _k, _v in ZTF_ZERO_POINTS.items()}
ZTF_FILTERS = {1: 'green', 2: 'red', 3: 'indigo'}
ZTF_FILTERS_R = {_v: _k for _k, _v in ZTF_FILTERS.items()}
ZTF_WAVELENGTH = {1: 4804.8, 2: 6436.9, 3: 7968.2}
ZTF_WAVELENGTH_R = {_v: _k for _k, _v in ZTF_WAVELENGTH.items()}

TRUE_VALUES = [1, True, '1', 'true', 't', 'TRUE', 'T']
FALSE_VALUES = [0, False, '0', 'false', 'f', 'FALSE', 'F']


# +
# initialization
# -
random.seed(os.getpid())


# +
# function: get_isot()
# -
# noinspection PyBroadException
def get_isot(ndays=0):
    """ return date in isot format for any ndays offset """
    try:
        return (datetime.now() + timedelta(days=ndays)).isoformat()
    except:
        return None


# +
# function: get_jd()
# -
# noinspection PyBroadException
def get_jd(ndays=0):
    """ return date in jd format for any ndays offset """
    try:
        return Time(get_isot(ndays)).jd
    except:
        return math.nan


# +
# function: isot_to_jd()
# -
# noinspection PyBroadException
def isot_to_jd(isot=''):
    """ returns jd from isot date string """
    try:
        return Time(isot).jd
    except:
        return math.nan


# +
# function: isot_to_nid()
# -
# noinspection PyBroadException
def isot_to_nid(isot=''):
    """ returns ZTF night id from isot date string """
    try:
        return int(isot_to_jd(isot) - isot_to_jd(ZTF_ZERO_NID))
    except:
        return None


# +
# function: nid_to_isot()
# -
# noinspection PyBroadException
def nid_to_isot(nid=0):
    """ returns date string from ZTF night id """
    try:
        return jd_to_isot(isot_to_jd(ZTF_ZERO_NID) + nid)
    except:
        return None


# +
# function: jd_to_isot()
# -
# noinspection PyBroadException
def jd_to_isot(jd=math.nan):
    """ return isot from jd """
    try:
        return Time(jd, format='jd', precision=6).isot
    except:
        return None


# +
# function: get_hash()
# -
# noinspection PyBroadException
def get_hash():
    """ return unique 64-character string """
    try:
        return hashlib.sha256(get_isot().encode('utf-8')).hexdigest()
    except:
        return None


# +
# function: ra_to_decimal()
# -
# noinspection PyBroadException
def ra_to_decimal(_ra=''):

    # check input(s)
    if not isinstance(_ra, str) or _ra.strip() == '':
        return math.nan

    # convert
    try:
        if 'hours' not in _ra.lower():
            _ra = f'{_ra} hours'
        return float(Angle(_ra).degree)
    except Exception:
        return math.nan


# +
# function: dec_to_decimal()
# -
# noinspection PyBroadException
def dec_to_decimal(_dec=''):

    # check input(s)
    if not isinstance(_dec, str) or _dec.strip() == '':
        return math.nan

    # convert
    try:
        if 'degrees' not in _dec.lower():
            _dec = f'{_dec} degrees'
        return float(Angle(_dec).degree)
    except Exception:
        return math.nan


# +
# function: get_astropy_coords()
# -
# noinspection PyBroadException
def get_astropy_coords(_name=''):

    # check input(s)
    if not isinstance(_name, str) or _name.strip() == '':
        return math.nan

    # get co-ordinates
    try:
        _obj = SkyCoord.from_name(_name)
        return _obj.ra.value, _obj.dec.value
    except Exception:
        return math.nan, math.nan


# +
# function: dc_mag()
# -
def dc_mag(fid=-1, magpsf=math.nan, sigmapsf=math.nan, magnr=math.nan,
           sigmagnr=math.nan, magzpsci=math.nan, isdiffpos=None):
    """ compute apparent magnitude from difference magnitude supplied by ZTF """

    # check input(s)
    if not isinstance(fid, int) or fid not in ZTF_FILTERS.keys():
        return {'dc_mag': math.nan, 'dc_sigmag': math.nan}
    if not isinstance(magpsf, float) or magpsf is math.nan:
        return {'dc_mag': math.nan, 'dc_sigmag': math.nan}
    if not isinstance(sigmapsf, float) or sigmapsf is math.nan:
        return {'dc_mag': math.nan, 'dc_sigmag': math.nan}
    if not isinstance(magnr, float) or magnr is math.nan:
        return {'dc_mag': math.nan, 'dc_sigmag': math.nan}
    if not isinstance(sigmagnr, float) or sigmagnr is math.nan:
        return {'dc_mag': math.nan, 'dc_sigmag': math.nan}
    if not isinstance(magzpsci, float) or magzpsci is math.nan:
        return {'dc_mag': math.nan, 'dc_sigmag': math.nan}
    isdiffpos = isdiffpos in TRUE_VALUES

    # set default(s)
    magzpref = ZTF_ZERO_POINTS[fid]
    magdiff = magzpref - magnr
    if magdiff > 12.0:
        magdiff = 12.0

    # calculate reference flux
    ref_flux = 10**(0.4*magdiff)
    ref_sigflux = (sigmagnr/1.0857)*ref_flux

    # calculate difference flux and its error
    if magzpsci == 0.0:
        magzpsci = magzpref
    magdiff = magzpsci - magpsf
    if magdiff > 12.0:
        magdiff = 12.0
    difference_flux = 10**(0.4*magdiff)
    difference_sigflux = (sigmapsf/1.0857)*difference_flux

    # add or subtract difference flux based on isdiffpos
    if isdiffpos:
        dc_flux = ref_flux + difference_flux
    else:
        dc_flux = ref_flux - difference_flux

    # assumes errors are independent (maybe too conservative)
    dc_sigflux = math.sqrt(difference_sigflux**2 + ref_sigflux**2)

    # apparent mag and its error from fluxes
    if dc_flux > 0.0:
        _dc_mag = magzpsci - 2.5 * math.log10(dc_flux)
        _dc_sigmag = dc_sigflux/dc_flux*1.0857
    else:
        _dc_mag = magzpsci
        _dc_sigmag = sigmapsf

    # return result
    return {'dc_mag': _dc_mag, 'dc_sigmag': _dc_sigmag}
