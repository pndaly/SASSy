#!/usr/bin/env python3


# +
# import(s)
# -
# noinspection PyUnresolvedReferences
from sqlalchemy import create_engine
from src.common import *
from src.models.sassy_cron import *
from src.utils.Alerce import *


# +
# constant(s)
# -
SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PORT = os.getenv('SASSY_DB_PORT', None)


# +
# function: db_connect()
# -
# noinspection PyBroadException
def db_connect():
    try:
        engine = create_engine(f'postgresql+psycopg2://{SASSY_DB_USER}:{SASSY_DB_PASS}@{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}')
        get_session = sessionmaker(bind=engine)
        return get_session()
    except Exception as e:
        print(f'Failed to connect to database, error={e}')
        return None


# +
# function: db_disconnect()
# -
# noinspection PyBroadException
def db_disconnect(_session=None):
    try:
        _session.close()
        _session.close_all_sessions()
    except Exception:
        pass


# +
# function: sassy_cron_2()
# -
# noinspection PyBroadException
def sassy_cron_2(_log=None):

    # check input(s)
    _log = _log if isinstance(_log, logging.Logger) else None

    # connect to database
    _s = db_connect()
    if _log:
        _log.info(f'_s={_s}, type(_s)={type(_s)}')

    # get Alerce class
    _alerce = Alerce()

    # get data
    _query = _s.query(SassyCron)
    for _q in _query.all():
        if _log:
            _log.info(f"_q={_q}, type(_q)={type(_q)}")
        _ignore, _aetype, _aeprob = _alerce.get_classifier(oid=f'{_q.zoid}', classifier='early')
        _ignore, _altype, _alprob = _alerce.get_classifier(oid=f'{_q.zoid}', classifier='late')
        if _log:
            _log.info(f"_aetype={_aetype}, _aeprob={_aeprob}")
            _log.info(f"_altype={_altype}, _alprob={_alprob}")

        # update database
        try:
            _q.aeprob = float(_aeprob)
            _q.aetype = str(_aetype).strip()
        except:
            _q.aeprob = math.nan
            _q.aetype = '?'
        try:
            _q.alprob = float(_alprob)
            _q.altype = str(_altype).strip()
        except:
            _q.alprob = math.nan
            _q.altype = '?'
        try:
            if _log:
                _log.info(f"commiting {_q.__repr__()} with _aetype={_aetype}, _aeprob={_aeprob}, _altype={_altype}, _alprob={_alprob}")
            _s.commit()
            _s.flush()
        except Exception as _f:
            _s.rollback()
            if _log:
                _log.error(f"failed to commit record, _e={_q}, error={_f}")

    # disconnect from database
    db_disconnect(_s)


# +
# main()
# -
if __name__ == '__main__':
    sassy_cron_2(_log=UtilsLogger('SassyCron').logger)
