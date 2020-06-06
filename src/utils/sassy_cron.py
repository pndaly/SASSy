#!/usr/bin/env python3


# +
# import(s)
# -
# noinspection PyUnresolvedReferences
from src import *
from src.common import *
from src.utils.utils import *

# noinspection PyUnresolvedReferences
from pg import DB

import argparse
import math
import re
import sys


# +
# constant(s)
# -
ASTRO_ISO = get_isot()
ASTRO_JD = isot_to_jd(ASTRO_ISO)
BEGIN_JD = ASTRO_JD - 1.0
BEGIN_ISO = jd_to_isot(BEGIN_JD)
END_JD = ASTRO_JD
END_ISO = jd_to_isot(END_JD)
RB_MIN = 0.50
RB_MAX = 1.00
RADIUS = 60.0


# +
# function: sassy_cron()
# -
# noinspection PyBroadException
def sassy_cron(_radius=RADIUS, _begin=BEGIN_ISO, _end=END_ISO, _rb_min=RB_MIN, _rb_max=RB_MAX, _logger=None):

    # check input(s)
    _radius = _radius/3600.0 if (isinstance(_radius, float) and _radius >= 0.0) else RADIUS/3600.0
    _begin_iso = _begin if (re.match(ISO_PATTERN, _begin) is not None and
                            isot_to_jd(_begin) is not math.nan) else BEGIN_ISO
    _end_iso = _end if (re.match(ISO_PATTERN, _end) is not None and isot_to_jd(_end) is not math.nan) else END_ISO
    _rb_min = _rb_min if (isinstance(_rb_min, float) and 0.0 < _rb_min <= 1.0) else RB_MIN
    _rb_max = _rb_max if (isinstance(_rb_max, float) and 0.0 < _rb_max <= 1.0) else RB_MAX

    # set default(s)
    if _rb_max < _rb_min:
        _rb_min, _rb_max = _rb_max, _rb_min
    _begin_jd = isot_to_jd(_begin_iso)
    _end_jd = isot_to_jd(_end_iso)

    # message
    if _logger:
        _logger.info(f"_radius = {_radius}")
        _logger.info(f"_begin_iso = {_begin_iso}")
        _logger.info(f"_begin_jd = {_begin_jd}")
        _logger.info(f"_end_iso = {_end_iso}")
        _logger.info(f"_end_jd = {_end_jd}")
        _logger.info(f"_rb_min = {_rb_min}")
        _logger.info(f"_rb_max = {_rb_max}")

    # connect to database
    if _logger:
        _logger.info(f"connecting to database")
    try:
        db = DB(dbname=SASSY_DB_NAME, host=SASSY_DB_HOST, port=int(SASSY_DB_PORT),
                user=SASSY_DB_USER, passwd=SASSY_DB_PASS)
    except Exception as e:
        if _logger:
            _logger.error(f"failed connecting to database, error={e}")
        return
    else:
        if _logger:
            _logger.info(f"connected to database OK")

    # drop any existing view
    _cmd_drop = 'DROP VIEW IF EXISTS SassyCron;'
    if _logger:
        _logger.info(f'executing {_cmd_drop}')
    try:
        db.query(_cmd_drop)
    except Exception as e:
        if _logger:
            _logger.error(f'failed to execute {_cmd_drop}, e={e}')
        if db is not None:
            db.close()
        return
    else:
        if _logger:
            _logger.info(f'executed {_cmd_drop} OK')

    # create new view
    _cmd_view = f'CREATE OR REPLACE VIEW SassyCron ("objectId", jd, drb, rb, sid, candid, ssnamenr, ra, dec) ' \
                f'AS WITH e AS (SELECT "objectId", jd, rb, drb, id, candid, ssnamenr, ' \
                f'(CASE WHEN ST_X(ST_AsText(location)) < 0.0 THEN ST_X(ST_AsText(location))+360.0 ELSE ' \
                f'ST_X(ST_AsText(location)) END), ST_Y(ST_AsText(location)) FROM alert WHERE ' \
                f'(("objectId" LIKE \'%ZTF2%\') AND (jd BETWEEN {_begin_jd} AND {_end_jd}) AND ' \
                f'((rb BETWEEN {_rb_min} AND {_rb_max}) OR (drb BETWEEN {_rb_min} AND {_rb_max})))) SELECT * FROM e;'
    if _logger:
        _logger.info(f'executing {_cmd_view}')
    try:
        db.query(_cmd_view)
    except Exception as e:
        if _logger:
            _logger.error(f'failed to execute {_cmd_view}, e={e}')
    else:
        if _logger:
            _logger.info(f'executed {_cmd_view} OK')

    # close and exit
    if db is not None:
        db.close()


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
                    help=f"""Search radius, defaults to %(default)s\u2033""")
    _p.add_argument(f'--rb-max', default=RB_MAX,
                    help=f"""Deep-Learning real-bogus score maximum, defaults to %(default)s""")
    _p.add_argument(f'--rb-min', default=RB_MIN,
                    help=f"""Deep-Learning real-bogus score minimum, defaults to %(default)s""")
    _p.add_argument(f'--verbose', default=False, action='store_true',
                    help='if present, produce more verbose output')
    args = _p.parse_args()

    # execute
    if args:
        sassy_cron(_radius=float(args.radius), _begin=args.begin, _end=args.end,
                   _rb_min=float(args.rb_min), _rb_max=float(args.rb_max),
                   _logger=UtilsLogger('SassyCron').logger if bool(args.verbose) else None)
    else:
        print(f'Insufficient command line arguments specified\nUse: python {sys.argv[0]} --help')
