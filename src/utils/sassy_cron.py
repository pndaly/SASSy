#!/usr/bin/env python3


# +
# import(s)
# -
# noinspection PyUnresolvedReferences
from sqlalchemy import create_engine
from src.common import *
from src.models.sassy_cron import *
from src.utils.Alerce import *
from src.utils.avro_plot_cutout import *


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
        engine = create_engine(
            f'postgresql+psycopg2://{SASSY_DB_USER}:{SASSY_DB_PASS}@{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}')
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
# function: get_avro_filename()
# -
# noinspection PyBroadException
def get_avro_filename(_jd=0.0, _candid=0, _dirs=os.getenv("SASSY_ZTF_AVRO", "/dataraid6/ztf:/dataraid0/ztf")):
    try:
        _ts = jd_to_isot(_jd).split('T')[0].split('-')
        for _h in _dirs.split(':'):
            _f = os.path.join(f'{_h}', f'{_ts[0]}', f'{_ts[1]}', f'{_ts[2]}', f'{_candid}.avro')
            if os.path.exists(_f):
                return f"{_f}"
    except Exception:
        return


# +
# function: sassy_cron()
# -
# noinspection PyBroadException
def sassy_cron(_log=None):

    # check input(s)
    _log = _log if isinstance(_log, logging.Logger) else None

    # connect to database
    _s = db_connect()
    if _log:
        _log.info(f'_s={_s}, type(_s)={type(_s)}')

    # get Alerce class
    _alerce = Alerce(_log)

    # get data
    _query = _s.query(SassyCron)
    for _q in _query.all():
        if _log:
            _log.info(f"_q={_q}, type(_q)={type(_q)}")

        # get classifier(s)
        _ignore, _aetype, _aeprob = _alerce.get_classifier(oid=f'{_q.zoid}', classifier='early')
        _ignore, _altype, _alprob = _alerce.get_classifier(oid=f'{_q.zoid}', classifier='late')
        if _log:
            _log.info(f"_aetype={_aetype}, _aeprob={_aeprob}")
            _log.info(f"_altype={_altype}, _alprob={_alprob}")

        # get filename and plot cutouts
        _file = get_avro_filename(_jd=_q.zjd, _candid=_q.zcandid)
        if _file is not None:
            try:
                _q.dpng = avro_plot_cutout(_avro_file=_file, _cutout='difference', _oid=_q.zoid, _jd=_q.zjd, _gid=int(_q.gid), _log=_log)
            except:
                _q.dpng = ''
            try:
                _q.spng = avro_plot_cutout(_avro_file=_file, _cutout='science', _oid=_q.zoid, _jd=_q.zjd, _gid=int(_q.gid), _log=_log)
            except:
                _q.spng = ''
            try:
                _q.tpng = avro_plot_cutout(_avro_file=_file, _cutout='template', _oid=_q.zoid, _jd=_q.zjd, _gid=int(_q.gid), _log=_log)
            except:
                _q.tpng = ''
        if _log:
            _log.info(f"_file={_file}")
            _log.info(f"_q.dpng={_q.dpng}")
            _log.info(f"_q.dsng={_q.spng}")
            _log.info(f"_q.tpng={_q.tpng}")

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
                _log.info(f"committing {_q.__repr__()} with _aetype={_aetype}, _aeprob={_aeprob}, _altype={_altype}, "
                          f"_alprob={_alprob}")
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
    sassy_cron(_log=UtilsLogger('SassyCron').logger)
