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
