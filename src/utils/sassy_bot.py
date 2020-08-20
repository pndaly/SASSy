#!/usr/bin/env python3


# +
# import(s)
# -
from astropy.time import Time
from datetime import datetime
from datetime import timedelta

# noinspection PyUnresolvedReferences
from pg import DB

from src.common import *
from src.utils.Alerce import *
from src.utils.utils import *
from src.utils.avro_plot import avro_plot

import argparse
import os
import math
import re
import sys


# +
# function(s)
# -
# noinspection PyBroadException
def get_iso(offset=0):
    try:
        return (datetime.now() + timedelta(days=offset)).isoformat()
    except Exception:
        return None


# noinspection PyBroadException
def iso_to_jd(_iso=''):
    try:
        return float(Time(_iso).mjd)+2400000.5
    except Exception:
        return float(math.nan)


# noinspection PyBroadException
def jd_to_iso(_jd=0.0):
    try:
        return Time(_jd, format='jd', precision=6).isot
    except Exception:
        return None


# noinspection PyBroadException
def get_avro_filename(_jd=0.0, _avro=0, _dirs=os.getenv("SASSY_ZTF_AVRO", "/dataraid6/ztf:/dataraid0/ztf")):
    try:
        _ts = jd_to_iso(_jd).split('T')[0].split('-')
        for _h in _dirs.split(':'):
            _f = os.path.join(f'{_h}', f'{_ts[0]}', f'{_ts[1]}', f'{_ts[2]}', f'{_avro}.avro')
            if os.path.exists(_f):
                return f"{_f}"
    except Exception:
        pass
    return f""


# +
# constant(s)
# -
ASTRO_ISO = get_iso()
ASTRO_JD = iso_to_jd(ASTRO_ISO)
BEGIN_JD = ASTRO_JD - 1.0
BEGIN_ISO = jd_to_iso(BEGIN_JD)
END_JD = ASTRO_JD
END_ISO = jd_to_iso(END_JD)
DATE_RULE = re.compile("\d{4}-\d{2}-\d{2}[ T]?\d{2}:\d{2}:\d")
RB_MIN = 0.75
RB_MAX = 0.95
RADIUS = 30.0


# +
# function: sassy_bot_read()
# -
# noinspection PyBroadException
def sassy_bot_read(_radius=RADIUS, _begin=BEGIN_ISO, _end=END_ISO, _rb_min=RB_MIN, _rb_max=RB_MAX, _logger=None):

    # check input(s)
    _radius = _radius/3600.0 if (isinstance(_radius, float) and 0.0 <= _radius) else RADIUS/3600.0
    _begin_iso = _begin if (re.match(DATE_RULE, _begin) is not None and
                            iso_to_jd(_begin) is not float(math.nan)) else BEGIN_ISO
    _end_iso = _end if (re.match(DATE_RULE, _end) is not None and iso_to_jd(_end) is not float(math.nan)) else END_ISO
    _rb_min = _rb_min if (isinstance(_rb_min, float) and 0.0 <= _rb_min <= 1.0) else RB_MIN
    _rb_max = _rb_max if (isinstance(_rb_max, float) and 0.0 <= _rb_max <= 1.0) else RB_MAX

    # entry
    if _logger:
        _logger.info(f"_radius = {_radius}")
        _logger.info(f"_begin_iso = {_begin_iso}")
        _logger.info(f"_end_iso = {_end_iso}")
        _logger.info(f"_rb_min = {_rb_min}")
        _logger.info(f"_rb_max = {_rb_max}")

    # set default(s)
    _alerce = Alerce(_logger)
    _res = None
    _results = []
    _begin_jd = iso_to_jd(_begin_iso)
    _end_jd = iso_to_jd(_end_iso)
    if _logger:
        _logger.info(f"_begin_jd = {_begin_jd}")
        _logger.info(f"_end_jd = {_end_jd}")

    # connect to database
    if _logger:
        _logger.info(f"Connecting to database")
    try:
        db = DB(dbname=SASSY_DB_NAME, host=SASSY_DB_HOST, port=int(SASSY_DB_PORT),
                user=SASSY_DB_USER, passwd=SASSY_DB_PASS)
    except Exception as e:
        if _logger:
            _logger.error(f"Failed connecting to database, error={e}")
        return
    if _logger:
        _logger.info(f"Connected to database OK")

    # drop any existing view
    _cmd_drop = 'DROP VIEW IF EXISTS sassy_bot;'
    if _logger:
        _logger.info(f'Executing {_cmd_drop}')
    try:
        db.query(_cmd_drop)
    except Exception as e:
        if _logger:
            _logger.error(f'Failed to execute {_cmd_drop}, e={e}')
        if db is not None:
            db.close()
        return
    if _logger:
        _logger.info(f'Executed {_cmd_drop} OK')

    # create new view
    _cmd_view = f'CREATE OR REPLACE VIEW sassy_bot ("objectId", jd, drb, rb, sid, candid, ssnamenr, ra, dec) ' \
                f'AS WITH e AS (SELECT "objectId", jd, rb, drb, id, candid, ssnamenr, ' \
                f'(CASE WHEN ST_X(ST_AsText(location)) < 0.0 THEN ST_X(ST_AsText(location))+360.0 ELSE ' \
                f'ST_X(ST_AsText(location)) END), ST_Y(ST_AsText(location)) FROM alert WHERE ' \
                f'(("objectId" LIKE \'%ZTF2%\') AND (jd BETWEEN {_begin_jd} AND {_end_jd}) AND ' \
                f'((rb BETWEEN {_rb_min} AND {_rb_max}) OR (drb BETWEEN {_rb_min} AND {_rb_max})))) SELECT * FROM e;'
    if _logger:
        _logger.info(f'Executing {_cmd_view}')
    try:
        db.query(_cmd_view)
    except Exception as e:
        if _logger:
            _logger.error(f'Failed to execute {_cmd_view}, e={e}')
    if _logger:
        _logger.info(f'Executed {_cmd_view} OK')

    # select
    _cmd_select = f"WITH x AS (SELECT * FROM sassy_bot), y AS (SELECT x.*, " \
                  f"(g.id, g.ra, g.dec, g.z, g.dist, q3c_dist(x.ra, x.dec, g.ra, g.dec)) " \
                  f"FROM x, glade_q3c AS g WHERE q3c_join(x.ra, x.dec, g.ra, g.dec, {_radius:.5f})), z AS " \
                  f"(SELECT * FROM y LEFT OUTER JOIN tns_q3c AS t ON " \
                  f"q3c_join(y.ra, y.dec, t.ra, t.dec, {_radius:.5f})) SELECT * FROM z WHERE tns_id IS null;"
    if _logger:
        _logger.info(f'Executing {_cmd_select}')
    try:
        _res = db.query(_cmd_select)
    except Exception as e:
        if _logger:
            _logger.error(f'Failed to execute {_cmd_select}, e={e}')
    if _logger:
        _logger.info(f'Executed {_cmd_select} OK')

    # close and exit
    if db is not None:
        db.close()

    # create output(s)
    for _e in _res:
        if _logger:
            _logger.info(f'_e={_e}')
        _gid, _gra, _gdec, _gz, _gdist, _gdelta = _e[9][1:-1].split(",")
        _d = {"objectId": f"{_e[0]}"}

        try:
            _classifier = _alerce.get_classifier(oid=_d['objectId'], classifier='early')
            _d['early_classifier'] = _classifier[1]
            _d['early_percent'] = _classifier[2] * 100.0
        except Exception:
            _d['early_classifier'] = 'n/a'
            _d['early_percent'] = math.nan

        try:
            _classifier = _alerce.get_classifier(oid=_d['objectId'], classifier='late')
            _d['late_classifier'] = _classifier[1]
            _d['late_percent'] = _classifier[2] * 100.0
        except Exception:
            _d['late_classifier'] = 'n/a'
            _d['late_percent'] = math.nan

        try:
            _d["jd"] = float(f"{_e[1]}")
        except Exception:
            _d["jd"] = float(math.nan)
        try:
            _d["drb"] = float(f"{_e[2]}")
        except Exception:
            _d["drb"] = float(math.nan)
        try:
            _d["rb"] = float(f"{_e[3]}")
        except Exception:
            _d["rb"] = float(math.nan)
        try:
            _d["sid"] = int(f"{_e[4]}")
        except Exception:
            _d["sid"] = -1
        try:
            _d["candid"] = int(f"{_e[5]}")
        except Exception:
            _d["candid"] = -1
        try:
            _d["ssnamenr"] = '' if f"{_e[6]}".lower() == 'null' else f"{_e[6]}"
        except Exception:
            _d["ssnamenr"] = ''
        try:
            _d["RA"] = float(f"{_e[7]}")
        except Exception:
            _d["RA"] = float(math.nan)
        try:
            _d["Dec"] = float(f"{_e[8]}")
        except Exception:
            _d["Dec"] = float(math.nan)
        try:
            _d["gid"] = int(f"{_gid}")
        except Exception:
            _d["gid"] = -1
        try:
            _d["gRA"] = float(f"{_gra}")
        except Exception:
            _d["gRA"] = float(math.nan)
        try:
            _d["gDec"] = float(f"{_gdec}")
        except Exception:
            _d["gDec"] = float(math.nan)
        try:
            _d["gDist"] = float(f"{_gdist}")
        except Exception:
            _d["gDist"] = float(math.nan)
        try:
            _d["gRedshift"] = float(f"{_gz}")
        except Exception:
            _d["gRedshift"] = float(math.nan)
        try:
            _d["gDelta"] = float(f"{_gdelta}")*3600.0
        except Exception:
            _d["gDelta"] = float(math.nan)

        try:
            _d["file"] = get_avro_filename(_d["jd"], _d["candid"])
        except Exception:
            _d["file"] = ""

        try:
            _d["png"] = avro_plot(_d["file"], True)[0]
        except Exception:
            _d["png"] = ""

        if _logger:
            _logger.info(f'_d={_d}')

        try:
            if _d["ssnamenr"] != '':
                if _logger:
                    _logger.debug(f'ignoring solar system object, _d={_d}')
            else:
                _results.append(_d)
        except Exception:
            continue

    # return
    return _results


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s)
    # noinspection PyTypeChecker
    _p = argparse.ArgumentParser(description=f'SASSy Bot', formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument(f'--begin', default=BEGIN_ISO,
                    help=f"""Begin date, defaults to %(default)s""")
    _p.add_argument(f'--end', default=END_ISO,
                    help=f"""End date, defaults to %(default)s""")
    _p.add_argument(f'--radius', default=RADIUS,
                    help=f"""Search radius, defaults to %(default)s''""")
    _p.add_argument(f'--rb-max', default=RB_MAX,
                    help=f"""Deep-Learning real-bogus score maximum, defaults to %(default)s""")
    _p.add_argument(f'--rb-min', default=RB_MIN,
                    help=f"""Deep-Learning real-bogus score minimum, defaults to %(default)s""")
    _p.add_argument(f'--verbose', default=False, action='store_true',
                    help='if present, produce more verbose output')
    args = _p.parse_args()

    # execute
    if args:
        _l = UtilsLogger('SassyBot').logger if bool(args.verbose) else None
        _r = sassy_bot_read(_radius=float(args.radius), _begin=args.begin, _end=args.end,
                            _rb_min=float(args.rb_min), _rb_max=float(args.rb_max), _logger=_l)
        if _l:
            _l.info(f"{len(_r)} records found")
    else:
        print(f'Insufficient command line arguments specified\nUse: python {sys.argv[0]} --help')
