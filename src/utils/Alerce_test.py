#!/usr/bin/env python3


# +
# import(s)
# -
from src.utils.Alerce import *
from datetime import datetime
from datetime import timedelta

import hashlib
import random


# +
# __doc__
# -
__doc__ = """
    % python3 -m pytest -p no:warnings Alerce_test.py
"""


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
# constant(s)
# -
TEST_API = ['crossmatch', 'crossmatch_all', 'get_classifier', 'get_detections', 'get_features', 'get_non_detections',
            'get_probabilities', 'get_query', 'get_sql', 'get_stamp', 'get_stats', 'oidmatch', 'oidmatch_all']
TEST_BYTES = 9223372036854775807
TEST_INVALID_INPUTS = [get_hash(), {get_hash(): TEST_BYTES}, [TEST_BYTES], (TEST_BYTES,), math.nan, -TEST_BYTES, None]


# +
# variable(s)
# -
_alerce = Alerce()


# +
# Alerce()
# -
def test_alerce_0():
    """ test instantiation for invalid input(s) """
    assert all(Alerce(log=_k).log is None for _k in TEST_INVALID_INPUTS)


def test_alerce_1():
    """ test instantiation for valid input(s) """
    assert isinstance(Alerce(log=True).log, logging.Logger)


def test_alerce_2():
    """ test instantiation for valid input(s) """
    assert Alerce(log=False).log is None


def test_alerce_3():
    """ test instantiation for valid input(s) """
    assert isinstance(Alerce(log=UtilsLogger(get_hash()).logger).log, logging.Logger)


def test_alerce_4():
    """ test instantiation for valid input(s) """
    assert all(hasattr(Alerce(), _k) for _k in TEST_API)


def test_alerce_5():
    """ test instantiation for valid input(s) """
    assert all(hasattr(Alerce(log=False), _k) for _k in TEST_API)


def test_alerce_6():
    """ test instantiation for valid input(s) """
    assert all(hasattr(Alerce(log=True), _k) for _k in TEST_API)


def test_alerce_7():
    """ test instantiation for valid input(s) """
    assert all(hasattr(Alerce(log=UtilsLogger(get_hash()).logger), _k) for _k in TEST_API)


def test_alerce_8():
    """ test instantiation returns correct type """
    assert isinstance(_alerce, Alerce)


# +
# Alerce().crossmatch(self, catalog='GAIADR2', ra=math.nan, dec=math.nan, radius=math.nan)
# -
def test_alerce_10():
    """ test crossmatch() for invalid input(s) """
    assert all(_alerce.crossmatch(catalog=_k) is None for _k in TEST_INVALID_INPUTS)


def test_alerce_11():
    """ test crossmatch() for invalid input(s) """
    _cat = random.choice(_alerce.alerce_catalogs)
    assert all(_alerce.crossmatch(catalog=_cat, ra=_k) is None for _k in TEST_INVALID_INPUTS)


def test_alerce_12():
    """ test crossmatch() for invalid input(s) """
    _cat = random.choice(_alerce.alerce_catalogs)
    _ra = random.uniform(-360.0, 360.0)
    assert all(_alerce.crossmatch(catalog=_cat, ra=_ra, dec=_k) is None for _k in TEST_INVALID_INPUTS)


def test_alerce_13():
    """ test crossmatch() for invalid input(s) """
    _cat = random.choice(_alerce.alerce_catalogs)
    _ra = random.uniform(-360.0, 360.0)
    _dec = random.uniform(-90.0, 90.0)
    assert all(_alerce.crossmatch(catalog=_cat, ra=_ra, dec=_dec, radius=_k) is None for _k in TEST_INVALID_INPUTS)


def test_alerce_14():
    """ test crossmatch() for valid input(s) """
    _cat = random.choice(_alerce.alerce_catalogs)
    _ra = random.uniform(-360.0, 360.0)
    _dec = random.uniform(-90.0, 90.0)
    _radius = random.uniform(0.0, 360.0)
    assert _alerce.crossmatch(catalog=_cat, ra=_ra, dec=_dec, radius=_radius) is not None


# +
# Alerce().crossmatch_all(self, ra=math.nan, dec=math.nan, radius=math.nan)
# -
def test_alerce_20():
    """ test crossmatch_all() for invalid input(s) """
    assert all(_alerce.crossmatch_all(ra=_k) is None for _k in TEST_INVALID_INPUTS)


def test_alerce_21():
    """ test crossmatch_all() for invalid input(s) """
    _ra = random.uniform(-360.0, 360.0)
    assert all(_alerce.crossmatch_all(ra=_ra, dec=_k) is None for _k in TEST_INVALID_INPUTS)


def test_alerce_22():
    """ test crossmatch_all() for invalid input(s) """
    _ra = random.uniform(-360.0, 360.0)
    _dec = random.uniform(-90.0, 90.0)
    assert all(_alerce.crossmatch_all(ra=_ra, dec=_dec, radius=_k) is None for _k in TEST_INVALID_INPUTS)


def test_alerce_23():
    """ test crossmatch_all() for valid input(s) """
    _ra = random.uniform(-360.0, 360.0)
    _dec = random.uniform(-90.0, 90.0)
    _radius = random.uniform(0.0, 60.0)
    assert _alerce.crossmatch_all(ra=_ra, dec=_dec, radius=_radius) is not None


# +
# Alerce().get_classifier(self, oid='', classifier='early')
# -
def test_alerce_30():
    """ test get_classifier() for invalid input(s)"""
    assert all(_alerce.get_classifier(oid=_k)[0] is None for _k in TEST_INVALID_INPUTS)


def test_alerce_31():
    """ test get_classifier() for invalid input(s)"""
    assert all(_alerce.get_classifier(oid=_k)[1] is None for _k in TEST_INVALID_INPUTS)


def test_alerce_32():
    """ test get_classifier() for invalid input(s)"""
    assert all(_alerce.get_classifier(oid=_k)[2] is math.nan for _k in TEST_INVALID_INPUTS)


def test_alerce_33():
    """ test get_classifier() for invalid input(s)"""
    assert all(_alerce.get_classifier(oid=get_hash(), classifier=_k)[0] is None for _k in TEST_INVALID_INPUTS)


def test_alerce_34():
    """ test get_classifier() for invalid input(s)"""
    assert all(_alerce.get_classifier(oid=get_hash(), classifier=_k)[1] is None for _k in TEST_INVALID_INPUTS)


def test_alerce_35():
    """ test get_classifier() for invalid input(s)"""
    assert all(_alerce.get_classifier(oid=get_hash(), classifier=_k)[2] is math.nan for _k in TEST_INVALID_INPUTS)


def test_alerce_36():
    """ test get_classifier() for valid input(s)"""
    assert _alerce.get_classifier(oid='ZTF20aaccyfe', classifier='early')[0] is not None


def test_alerce_37():
    """ test get_classifier() for valid input(s)"""
    assert _alerce.get_classifier(oid='ZTF20aaccyfe', classifier='early')[1] is not None


def test_alerce_38():
    """ test get_classifier() for valid input(s)"""
    assert _alerce.get_classifier(oid='ZTF20aaccyfe', classifier='early')[2] is not math.nan


def test_alerce_39():
    """ test get_classifier() for valid input(s)"""
    assert isinstance(_alerce.get_classifier(oid='ZTF20aaccyfe', classifier='early')[2], float)


def test_alerce_40():
    """ test get_classifier() for valid input(s)"""
    _val = _alerce.get_classifier(oid='ZTF20aaccyfe', classifier='early')[2]
    assert 0.0 <= _val <= 1.0


def test_alerce_41():
    """ test get_classifier() for valid input(s)"""
    assert _alerce.get_classifier(oid='ZTF20aaccyfe', classifier='late')[0] is not None


def test_alerce_42():
    """ test get_classifier() for valid input(s)"""
    assert _alerce.get_classifier(oid='ZTF20aaccyfe', classifier='late')[1] is not None


def test_alerce_43():
    """ test get_classifier() for valid input(s)"""
    assert _alerce.get_classifier(oid='ZTF20aaccyfe', classifier='late')[2] is not math.nan


def test_alerce_44():
    """ test get_classifier() for valid input(s)"""
    assert isinstance(_alerce.get_classifier(oid='ZTF20aaccyfe', classifier='late')[2], float)


def test_alerce_45():
    """ test get_classifier() for valid input(s)"""
    _val = _alerce.get_classifier(oid='ZTF20aaccyfe', classifier='late')[2]
    assert 0.0 <= _val <= 1.0


def test_alerce_46():
    """ test get_classifier() for valid input(s)"""
    assert isinstance(_alerce.get_classifier(oid='ZTF20aaccyfe', classifier='early'), tuple)


def test_alerce_47():
    """ test get_classifier() for valid input(s)"""
    assert isinstance(_alerce.get_classifier(oid='ZTF20aaccyfe', classifier='late'), tuple)


def test_alerce_48():
    """ test get_classifier() for invalid input(s)"""
    assert all(isinstance(_alerce.get_classifier(oid=_k), tuple) for _k in TEST_INVALID_INPUTS)


def test_alerce_49():
    """ test get_classifier() for invalid input(s)"""
    assert all(isinstance(_alerce.get_classifier(oid=get_hash(), classifier=_k), tuple) for _k in TEST_INVALID_INPUTS)


# +
# Alerce().get_detections(self, oid='')
# -
def test_alerce_50():
    """ test get_detections() for invalid input(s)"""
    assert all(_alerce.get_detections(oid=_k) is None for _k in TEST_INVALID_INPUTS[1:])


def test_alerce_51():
    """ test get_detections() for valid input(s)"""
    assert isinstance(_alerce.get_detections(oid='ZTF20aaccyfe'), dict)


def test_alerce_52():
    """ test get_detections() for valid input(s)"""
    assert _alerce.get_detections(oid='ZTF20aaccyfe') is not {}


# +
# Alerce().get_features(self, oid='')
# -
def test_alerce_60():
    """ test get_features() for invalid input(s)"""
    assert all(_alerce.get_features(oid=_k) is None for _k in TEST_INVALID_INPUTS[1:])


def test_alerce_61():
    """ test get_features() for valid input(s)"""
    assert isinstance(_alerce.get_features(oid='ZTF20aaccyfe'), dict)


def test_alerce_62():
    """ test get_features() for valid input(s)"""
    assert _alerce.get_features(oid='ZTF20aaccyfe') is not {}


# +
# Alerce().get_non_detections(self, oid='')
# -
def test_alerce_70():
    """ test get_non_detections() for invalid input(s)"""
    assert all(_alerce.get_non_detections(oid=_k) is None for _k in TEST_INVALID_INPUTS[1:])


def test_alerce_71():
    """ test get_non_detections() for valid input(s)"""
    assert isinstance(_alerce.get_non_detections(oid='ZTF20aaccyfe'), dict)


def test_alerce_72():
    """ test get_non_detections() for valid input(s)"""
    assert _alerce.get_non_detections(oid='ZTF20aaccyfe') is not {}


# +
# Alerce().get_probabilities(self, oid='')
# -
def test_alerce_80():
    """ test get_probabilities() for invalid input(s)"""
    assert all(_alerce.get_probabilities(oid=_k) is None for _k in TEST_INVALID_INPUTS[1:])


def test_alerce_81():
    """ test get_probabilities() for valid input(s)"""
    assert isinstance(_alerce.get_probabilities(oid='ZTF20aaccyfe'), dict)


def test_alerce_82():
    """ test get_probabilities() for valid input(s)"""
    assert _alerce.get_probabilities(oid='ZTF20aaccyfe') is not {}


# +
# Alerce().query(self, payload=None)
# -
def test_alerce_90():
    """ test get_query() for invalid input(s)"""
    assert all(_alerce.get_query(payload=_k) is None for _k in TEST_INVALID_INPUTS[2:])


def test_alerce_91():
    """ test get_query() for valid input(s)"""
    assert isinstance(_alerce.get_query(payload={"query_parameters": {"dates": {"firstmjd": {"min": 58682}}}}), dict)


def test_alerce_92():
    """ test get_probabilities() for valid input(s)"""
    assert _alerce.get_query(payload={"query_parameters": {"dates": {"firstmjd": {"min": 58682}}}}) is not {}


# +
# Alerce().get_sql(self, payload=None)
# -
def test_alerce_100():
    """ test get_sql() for invalid input(s)"""
    assert all(_alerce.get_sql(payload=_k) is None for _k in TEST_INVALID_INPUTS[2:])


def test_alerce_101():
    """ test get_sql() for valid input(s)"""
    assert isinstance(_alerce.get_sql(payload={"query_parameters": {"dates": {"firstmjd": {"min": 58682}}}}), str)


def test_alerce_102():
    """ test get_sql() for valid input(s)"""
    assert 'SELECT' in _alerce.get_sql(payload={"query_parameters": {"dates": {"firstmjd": {"min": 58682}}}})


# +
# Alerce().get_stats(self, oid='')
# -
def test_alerce_110():
    """ test get_stats() for invalid input(s)"""
    assert all(_alerce.get_stats(oid=_k) is None for _k in TEST_INVALID_INPUTS[1:])


def test_alerce_111():
    """ test get_stats() for valid input(s)"""
    assert isinstance(_alerce.get_stats(oid='ZTF20aaccyfe'), dict)


def test_alerce_112():
    """ test get_stats() for valid input(s)"""
    assert _alerce.get_stats(oid='ZTF20aaccyfe') is not {}


# +
# Alerce() documentation
# -
def test_alerce_120():
    assert Alerce().__doc__() != ''


def test_alerce_121():
    assert Alerce().alerce_catalogs != ''


def test_alerce_122():
    assert Alerce().alerce_payload is not {}


def test_alerce_123():
    assert all(getattr(_alerce, _k).__doc__ != '' for _k in TEST_API)


# +
# Alerce().oidmatch(self, catalog='GAIADR2', oid='', radius=math.nan)
# -
def test_alerce_130():
    """ test oidmatch() for invalid input(s) """
    assert all(_alerce.oidmatch(catalog=_k) is None for _k in TEST_INVALID_INPUTS)


def test_alerce_131():
    """ test oidmatch() for invalid input(s) """
    _cat = random.choice(_alerce.alerce_catalogs)
    assert all(_alerce.oidmatch(catalog=_cat, oid=_k) is None for _k in TEST_INVALID_INPUTS[1:])


def test_alerce_132():
    """ test oidmatch() for invalid input(s) """
    _cat = random.choice(_alerce.alerce_catalogs)
    assert all(_alerce.oidmatch(catalog=_cat, oid=get_hash(), radius=_k) is None for _k in TEST_INVALID_INPUTS)


def test_alerce_133():
    """ test oidmatch() for valid input(s) """
    _cat = random.choice(_alerce.alerce_catalogs)
    _radius = random.uniform(0.0, 360.0)
    assert _alerce.oidmatch(catalog=_cat, oid='ZTF20aaccyfe', radius=_radius) is not None


# +
# Alerce().oidmatch_all(self, oid='', radius=math.nan)
# -
def test_alerce_140():
    """ test oidmatch_all() for invalid input(s) """
    assert all(_alerce.oidmatch_all(oid=_k) is None for _k in TEST_INVALID_INPUTS[1:])


def test_alerce_141():
    """ test oidmatch_all() for invalid input(s) """
    assert all(_alerce.oidmatch_all(oid=get_hash(), radius=_k) is None for _k in TEST_INVALID_INPUTS)


def test_alerce_142():
    """ test oidmatch_all() for valid input(s) """
    _radius = random.uniform(0.0, 60.0)
    assert _alerce.oidmatch_all(oid='ZTF20aaccyfe', radius=_radius) is not None


# +
# Alerce().get_stamp(self, oid='', candid=0, stamp='science', output='png')
# -
def test_alerce_150():
    """ test get_stamp() for invalid input(s) """
    assert all(_alerce.get_stamp(oid=_k) is None for _k in TEST_INVALID_INPUTS[1:])


def test_alerce_151():
    """ test get_stamp() for invalid input(s) """
    assert all(_alerce.get_stamp(oid=get_hash(), candid=_k) is None for _k in TEST_INVALID_INPUTS)


def test_alerce_152():
    """ test get_stamp() for invalid input(s) """
    assert all(_alerce.get_stamp(oid=get_hash(), candid=random.randint(0, 1000), stamp=_k) is None
               for _k in TEST_INVALID_INPUTS[1:])


def test_alerce_153():
    """ test get_stamp() for invalid input(s) """
    _oid = get_hash()
    _stp = random.choice(_alerce.alerce_stamps)
    assert all(_alerce.get_stamp(oid=_oid, candid=random.randint(0, 1000), stamp=_stp, output=_k) is None
               for _k in TEST_INVALID_INPUTS)


def test_alerce_154():
    """ test get_stamp() for valid input(s) """
    assert _alerce.get_stamp(oid='ZTF20aaccyfe', candid=0, stamp='science', output='fits') is not None


def test_alerce_155():
    """ test get_stamp() for valid input(s) """
    _stamp = random.choice(_alerce.alerce_stamps)
    _output = random.choice(_alerce.alerce_outputs)
    assert _alerce.get_stamp(oid='ZTF20aaccyfe', candid=1098447070015010011, stamp=_stamp, output=_output) is not None


def test_alerce_156():
    """ test get_stamp() for valid input(s) """
    _oid = 'ZTF20aaccyfe'
    _candid = 1098447070015010011
    _stamp = random.choice(_alerce.alerce_stamps)
    _output = random.choice(_alerce.alerce_outputs)
    _file = _alerce.get_stamp(oid=_oid, candid=_candid, stamp=_stamp, output=_output)
    assert _file is not None and os.path.exists(_alerce.output)
