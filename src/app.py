#!/usr/bin/env python3


# +
# import(s)
# -
# noinspection PyUnresolvedReferences
from src import *
from src.common import *
from src.utils.utils import *

# noinspection PyBroadException
try:
    from src.utils.sassy_bot import *
    from src.utils.sassy_cron import *
except:
    sassy_bot_read = None
    sassy_cron_read = None

from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from flask import send_file
from flask import send_from_directory
from urllib.parse import urlencode

# noinspection PyUnresolvedReferences
from src.forms.Forms import AstronomicalRadialQueryForm
from src.forms.Forms import AstronomicalEllipticalQueryForm
from src.forms.Forms import DigitalRadialQueryForm
from src.forms.Forms import DigitalEllipticalQueryForm
from src.forms.Forms import PsqlQueryForm
from src.forms.Forms import SexagisimalRadialQueryForm
from src.forms.Forms import SexagisimalEllipticalQueryForm
from src.forms.Forms import SassyBotForm

# noinspection PyUnresolvedReferences
from src.models.glade import GladeRecord
from src.models.glade import db as db_glade
from src.models.glade import glade_filters
from src.models.glade import glade_get_text
from src.models.glade_q3c import GladeQ3cRecord
from src.models.glade_q3c import db as db_glade_q3c
from src.models.glade_q3c import glade_q3c_filters
from src.models.glade_q3c import glade_q3c_get_text

# noinspection PyUnresolvedReferences
from src.models.gwgc import GwgcRecord
from src.models.gwgc import db as db_gwgc
from src.models.gwgc import gwgc_filters
from src.models.gwgc import gwgc_get_text
from src.models.gwgc_q3c import GwgcQ3cRecord
from src.models.gwgc_q3c import db as db_gwgc_q3c
from src.models.gwgc_q3c import gwgc_q3c_filters
from src.models.gwgc_q3c import gwgc_q3c_get_text

# noinspection PyUnresolvedReferences
from src.models.ligo import LigoRecord
from src.models.ligo import db as db_ligo
from src.models.ligo import ligo_filters
from src.models.ligo import ligo_get_text
from src.models.ligo_q3c import LigoQ3cRecord
from src.models.ligo_q3c import db as db_ligo_q3c
from src.models.ligo_q3c import ligo_q3c_filters
from src.models.ligo_q3c import ligo_q3c_get_text

# noinspection PyUnresolvedReferences
from src.models.psql import Psql

# noinspection PyUnresolvedReferences
from src.models.tns import TnsRecord
from src.models.tns import db as db_tns
from src.models.tns import tns_filters
from src.models.tns import tns_get_text
from src.models.tns_q3c import TnsQ3cRecord
from src.models.tns_q3c import db as db_tns_q3c
from src.models.tns_q3c import tns_q3c_filters
from src.models.tns_q3c import tns_q3c_get_text

# noinspection PyUnresolvedReferences
from src.models.ztf import ZtfAlert
from src.models.ztf import db as db_ztf
from src.models.ztf import ztf_filters
from src.models.ztf import ztf_get_text

import glob
import io
import pytz


# +
# constant(s)
# -
ARIZONA = pytz.timezone('America/Phoenix')
BOT_RESULTS_PER_PAGE = 25
COLUMNS = ['jd', 'filter', 'magpsf', 'sigmapsf', 'diffmaglim']
HEADERS = ['jd', 'filter', 'magpsf', 'sigmapsf', 'diffmaglim']
PSQL_CONNECT_MSG = f'{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME} using {SASSY_DB_USER}:{SASSY_DB_PASS}'
RESULTS_PER_PAGE = 50


# +
# logging
# -
logger = UtilsLogger('SassyFlaskAppLogger').logger
logger.debug('SASSY_APP_HOST = {}'.format(SASSY_APP_HOST))
logger.debug('SASSY_APP_PORT = {}'.format(SASSY_APP_PORT))
logger.debug('SASSY_APP_URL = {}'.format(SASSY_APP_URL))
logger.debug('SASSY_DB_HOST = {}'.format(SASSY_DB_HOST))
logger.debug('SASSY_DB_NAME = {}'.format(SASSY_DB_NAME))
logger.debug('SASSY_DB_PASS = {}'.format(SASSY_DB_PASS))
logger.debug('SASSY_DB_PORT = {}'.format(SASSY_DB_PORT))
logger.debug('SASSY_DB_USER = {}'.format(SASSY_DB_USER))
logger.debug('SASSY_HOME = {}'.format(SASSY_HOME))
logger.debug('SASSY_ZTF_ARCHIVE = {}'.format(SASSY_ZTF_ARCHIVE))
logger.debug('SASSY_ZTF_AVRO = {}'.format(SASSY_ZTF_AVRO))
logger.debug('SASSY_ZTF_DATA = {}'.format(SASSY_ZTF_DATA))
logger.debug('SASSY_APP_URL = {}'.format(SASSY_APP_URL))


# +
# initialize flask
# -
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'postgresql+psycopg2://{SASSY_DB_USER}:{SASSY_DB_PASS}@{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Steward Alerts For Science System!'


# +
# initialize sqlalchemy
# -
with app.app_context():
    db_glade.init_app(app)
    db_glade_q3c.init_app(app)
    db_gwgc.init_app(app)
    db_gwgc_q3c.init_app(app)
    db_ligo.init_app(app)
    db_ligo_q3c.init_app(app)
    db_tns.init_app(app)
    db_tns_q3c.init_app(app)
    db_ztf.init_app(app)


# +
# (hidden) function: _request_wants_json()
# -
def _request_wants_json():
    if request.args.get('format', 'html', type=str) == 'json':
        return True
    else:
        best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
        return best == 'application/json' and \
            request.accept_mimetypes[best] > \
            request.accept_mimetypes['text/html']


# +
# route(s): /, /sassy/
# -
@app.route('/sassy/')
@app.route('/')
def sassy_home():
    logger.debug(f'route /sassy/ entry')
    return render_template('sassy.html', url={'url': f'{SASSY_APP_URL}', 'page': ''})


# +
# route(s): /api/, /sassy/api/
# -
@app.route('/sassy/api/')
@app.route('/api/')
def sassy_api():
    logger.debug(f'route /sassy/api/ entry')
    return render_template('api.html', url={'url': f'{SASSY_APP_URL}'})


# +
# route(s): /astronomical_elliptical/, /sassy/astronomical_elliptical/
# -
# noinspection PyBroadException
@app.route('/sassy/astronomical_elliptical/', methods=['GET', 'POST'])
@app.route('/astronomical_elliptical/', methods=['GET', 'POST'])
def sassy_astronomical_elliptical():
    logger.debug(f'route /sassy/astronomical_elliptical/ entry')

    # report where request is coming from
    forwarded_ips = request.headers.getlist('X-Forwarded-For')
    client_ip = forwarded_ips[0].split(',')[0] if len(forwarded_ips) >= 1 else ''
    logger.info('incoming request', extra={'tags': {'requesting_ip': client_ip, 'request_args': request.args}})
    page = request.args.get('page', 1, type=int)

    # build form
    form = AstronomicalEllipticalQueryForm()

    # validate form (POST request)
    if form.validate_on_submit():

        # get data
        _nam = form.obj_name.data
        _ra, _dec = get_astropy_coords(_nam)
        _maj = float(form.majaxis.data)
        _rat = float(form.ratio.data)
        _pos = float(form.posang.data)
        _cat = form.catalog.data.lower()
        logger.debug(f'AstronomicalEllipticalQueryForm(), '
                     f'_nam={_nam}, _ra={_ra}, _dec={_dec}, _rat={_rat}, _pos={_pos}, _cat={_cat}')

        _dbh = None
        _fil = None
        _rec = None
        latest = None
        if _cat == 'glade_q3c':
            _dbh = db_glade_q3c
            _fil = glade_q3c_filters
            _rec = GladeQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.gwgc.desc()).first()
        elif _cat == 'gwgc_q3c':
            _dbh = db_gwgc_q3c
            _fil = gwgc_q3c_filters
            _rec = GwgcQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.name.desc()).first()
        elif _cat == 'ligo_q3c':
            _dbh = db_ligo_q3c
            _fil = ligo_q3c_filters
            _rec = LigoQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.name.desc()).first()
        elif _cat == 'tns_q3c':
            _dbh = db_tns_q3c
            _fil = tns_q3c_filters
            _rec = TnsQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.tns_name.desc()).first()

        query = _dbh.session.query(_rec)
        query = _fil(query, {"ellipse": f"{_ra},{_dec},{_maj},{_rat},{_pos}"})
        paginator = query.paginate(page, RESULTS_PER_PAGE, True)
        response = {
            'total': paginator.total,
            'pages': paginator.pages,
            'has_next': paginator.has_next,
            'has_prev': paginator.has_prev,
            'results': _rec.serialize_list(paginator.items)
        }
        if _request_wants_json() or request.method == 'GET':
            return jsonify(response)

        _args = request.args.copy()
        try:
            _args.pop('page')
        except:
            pass
        arg_str = urlencode(_args)
        return render_template(f'{_cat}.html', context=response, page=paginator.page, arg_str=arg_str, latest=latest,
                               url={'url': f'{SASSY_APP_URL}', 'page': f'{_cat}'})

    # return for GET
    return render_template('astronomical_elliptical_query.html', form=form)


# +
# route(s): /astronomical_radial/, /sassy/astronomical_radial/
# -
# noinspection PyBroadException
@app.route('/sassy/astronomical_radial/', methods=['GET', 'POST'])
@app.route('/astronomical_radial/', methods=['GET', 'POST'])
def sassy_astronomical_radial():
    logger.debug(f'route /sassy/astronomical_radial/ entry')

    # report where request is coming from
    forwarded_ips = request.headers.getlist('X-Forwarded-For')
    client_ip = forwarded_ips[0].split(',')[0] if len(forwarded_ips) >= 1 else ''
    logger.info('incoming request', extra={'tags': {'requesting_ip': client_ip, 'request_args': request.args}})
    page = request.args.get('page', 1, type=int)

    # build form
    form = AstronomicalRadialQueryForm()

    # validate form (POST request)
    if form.validate_on_submit():

        # get data
        _nam = form.obj_name.data
        _rad = float(form.radius.data)
        _cat = form.catalog.data.lower()
        logger.debug(f'AstronomicalRadialQueryForm(), _nam={_nam}, _rad={_rad}, _cat={_cat}')

        _dbh = None
        _fil = None
        _rec = None
        latest = None
        if _cat == 'glade_q3c':
            _dbh = db_glade_q3c
            _fil = glade_q3c_filters
            _rec = GladeQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.gwgc.desc()).first()
        elif _cat == 'gwgc_q3c':
            _dbh = db_gwgc_q3c
            _fil = gwgc_q3c_filters
            _rec = GwgcQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.name.desc()).first()
        elif _cat == 'ligo_q3c':
            _dbh = db_ligo_q3c
            _fil = ligo_q3c_filters
            _rec = LigoQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.name.desc()).first()
        elif _cat == 'tns_q3c':
            _dbh = db_tns_q3c
            _fil = tns_q3c_filters
            _rec = TnsQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.tns_name.desc()).first()

        query = _dbh.session.query(_rec)
        query = _fil(query, {"astrocone": f"{_nam},{_rad}"})
        paginator = query.paginate(page, RESULTS_PER_PAGE, True)
        response = {
            'total': paginator.total,
            'pages': paginator.pages,
            'has_next': paginator.has_next,
            'has_prev': paginator.has_prev,
            'results': _rec.serialize_list(paginator.items)
        }
        if _request_wants_json() or request.method == 'GET':
            return jsonify(response)

        _args = request.args.copy()
        try:
            _args.pop('page')
        except:
            pass
        arg_str = urlencode(_args)
        return render_template(f'{_cat}.html', context=response, page=paginator.page, arg_str=arg_str, latest=latest,
                               url={'url': f'{SASSY_APP_URL}', 'page': f'{_cat}'})

    # return for GET
    return render_template('astronomical_radial_query.html', form=form)


# +
# route(s): /bot/, /sassy/bot/
# -
# noinspection PyBroadException
@app.route('/sassy/bot/', methods=['GET', 'POST'])
@app.route('/bot/', methods=['GET', 'POST'])
def sassy_bot():
    logger.debug(f'route /sassy/bot/ entry')

    # report where request is coming from
    forwarded_ips = request.headers.getlist('X-Forwarded-For')
    client_ip = forwarded_ips[0].split(',')[0] if len(forwarded_ips) >= 1 else ''
    logger.info('incoming request', extra={'tags': {'requesting_ip': client_ip, 'request_args': request.args}})
    # page = request.args.get('page', 1, type=int)

    # build form
    form = SassyBotForm()

    # validate form (POST request)
    if form.validate_on_submit():

        # get data
        _radius = float(form.radius.data)
        _begin_iso = form.begin_date.data.strip()
        _end_iso = form.end_date.data.strip()
        _rb_min = float(form.rb_min.data)
        _rb_max = float(form.rb_max.data)
        logger.debug(f'_radius={_radius}, _begin_iso={_begin_iso}, _end_iso={_end_iso}, '
                     f'_rb_min={_rb_min}, _rb_max={_rb_max}')

        # paginate
        _history = []
        _total = 0
        if sassy_bot_read is not None:
            _history = sassy_bot_read(_radius, _begin_iso, _end_iso, _rb_min, _rb_max, logger)
            _total = len(_history)

        # return result(s)
        return render_template('sassy_bot_results.html', history=_history, total=_total)

    # return for GET
    return render_template('sassy_bot.html', form=form)


# +
# route(s): /cron/, /sassy/cron/
# -
@app.route('/sassy/cron/<float:radius>', methods=['GET', 'POST'])
@app.route('/cron/<float:radius>', methods=['GET', 'POST'])
def sassy_cron_query(radius=0.0):
    logger.debug(f'route /sassy/cron/{radius}/ entry')

    # connect to database
    _cron = None
    try:
        _cron = sassy_cron_read(radius, logger)
    except Exception as e:
        logger.error(f'failed reading SassyCron, error={e}')

    # return
    response = {'total': len(_cron), 'results': _cron}
    return render_template('sassy_cron_results.html', context=response)


# +
# route(s): /digital_elliptical/, /sassy/digital_elliptical/
# -
# noinspection PyBroadException
@app.route('/sassy/digital_elliptical/', methods=['GET', 'POST'])
@app.route('/digital_elliptical/', methods=['GET', 'POST'])
def sassy_digital_elliptical():
    logger.debug(f'route /sassy/digital_elliptical/ entry')

    # report where request is coming from
    forwarded_ips = request.headers.getlist('X-Forwarded-For')
    client_ip = forwarded_ips[0].split(',')[0] if len(forwarded_ips) >= 1 else ''
    logger.info('incoming request', extra={'tags': {'requesting_ip': client_ip, 'request_args': request.args}})
    page = request.args.get('page', 1, type=int)

    # build form
    form = DigitalEllipticalQueryForm()

    # validate form (POST request)
    if form.validate_on_submit():

        # get data
        _ra = float(form.ra.data)
        _dec = float(form.dec.data)
        _maj = float(form.majaxis.data)
        _rat = float(form.ratio.data)
        _pos = float(form.posang.data)
        _cat = form.catalog.data.lower()
        logger.debug(f'DigitalEllipticalQueryForm(), _ra={_ra}, _dec={_dec}, '
                     f'_rat={_rat}, _pos={_pos}, _cat={_cat}')

        _dbh = None
        _fil = None
        _rec = None
        latest = None
        if _cat == 'glade_q3c':
            _dbh = db_glade_q3c
            _fil = glade_q3c_filters
            _rec = GladeQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.gwgc.desc()).first()
        elif _cat == 'gwgc_q3c':
            _dbh = db_gwgc_q3c
            _fil = gwgc_q3c_filters
            _rec = GwgcQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.name.desc()).first()
        elif _cat == 'ligo_q3c':
            _dbh = db_ligo_q3c
            _fil = ligo_q3c_filters
            _rec = LigoQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.name.desc()).first()
        elif _cat == 'tns_q3c':
            _dbh = db_tns_q3c
            _fil = tns_q3c_filters
            _rec = TnsQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.tns_name.desc()).first()

        query = _dbh.session.query(_rec)
        query = _fil(query, {"ellipse": f"{_ra},{_dec},{_maj},{_rat},{_pos}"})
        paginator = query.paginate(page, RESULTS_PER_PAGE, True)
        response = {
            'total': paginator.total,
            'pages': paginator.pages,
            'has_next': paginator.has_next,
            'has_prev': paginator.has_prev,
            'results': _rec.serialize_list(paginator.items)
        }
        if _request_wants_json() or request.method == 'GET':
            return jsonify(response)

        _args = request.args.copy()
        try:
            _args.pop('page')
        except:
            pass
        arg_str = urlencode(_args)
        return render_template(f'{_cat}.html', context=response, page=paginator.page, arg_str=arg_str, latest=latest,
                               url={'url': f'{SASSY_APP_URL}', 'page': f'{_cat}'})

    # return for GET
    return render_template('digital_elliptical_query.html', form=form)


# +
# route(s): /digital_radial/, /sassy/digital_radial/
# -
# noinspection PyBroadException
@app.route('/sassy/digital_radial/', methods=['GET', 'POST'])
@app.route('/digital_radial/', methods=['GET', 'POST'])
def sassy_digital_radial():
    logger.debug(f'route /sassy/digital_radial/ entry')

    # report where request is coming from
    forwarded_ips = request.headers.getlist('X-Forwarded-For')
    client_ip = forwarded_ips[0].split(',')[0] if len(forwarded_ips) >= 1 else ''
    logger.info('incoming request', extra={'tags': {'requesting_ip': client_ip, 'request_args': request.args}})
    page = request.args.get('page', 1, type=int)

    # build form
    form = DigitalRadialQueryForm()

    # validate form (POST request)
    if form.validate_on_submit():

        # get data
        _ra = float(form.ra.data)
        _dec = float(form.dec.data)
        _rad = float(form.radius.data)
        _cat = form.catalog.data.lower()
        logger.debug(f'DigitalRadialQueryForm(), _ra={_ra}, _dec={_dec}, _rad={_rad}, _cat={_cat}')

        _dbh = None
        _fil = None
        _rec = None
        latest = None
        if _cat == 'glade_q3c':
            _dbh = db_glade_q3c
            _fil = glade_q3c_filters
            _rec = GladeQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.gwgc.desc()).first()
        elif _cat == 'gwgc_q3c':
            _dbh = db_gwgc_q3c
            _fil = gwgc_q3c_filters
            _rec = GwgcQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.name.desc()).first()
        elif _cat == 'ligo_q3c':
            _dbh = db_ligo_q3c
            _fil = ligo_q3c_filters
            _rec = LigoQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.name.desc()).first()
        elif _cat == 'tns_q3c':
            _dbh = db_tns_q3c
            _fil = tns_q3c_filters
            _rec = TnsQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.tns_name.desc()).first()

        query = _dbh.session.query(_rec)
        query = _fil(query, {"cone": f"{_ra},{_dec},{_rad}"})
        paginator = query.paginate(page, RESULTS_PER_PAGE, True)
        response = {
            'total': paginator.total,
            'pages': paginator.pages,
            'has_next': paginator.has_next,
            'has_prev': paginator.has_prev,
            'results': _rec.serialize_list(paginator.items)
        }
        if _request_wants_json() or request.method == 'GET':
            return jsonify(response)

        _args = request.args.copy()
        try:
            _args.pop('page')
        except:
            pass
        arg_str = urlencode(_args)
        return render_template(f'{_cat}.html', context=response, page=paginator.page, arg_str=arg_str, latest=latest,
                               url={'url': f'{SASSY_APP_URL}', 'page': f'{_cat}'})

    # return for GET
    return render_template('digital_radial_query.html', form=form)


# +
# route(s): /sexagisimal_elliptical/, /sassy/sexagisimal_elliptical/
# -
# noinspection PyBroadException
@app.route('/sassy/sexagisimal_elliptical/', methods=['GET', 'POST'])
@app.route('/sexagisimal_elliptical/', methods=['GET', 'POST'])
def sassy_sexagisimal_elliptical():
    logger.debug(f'route /sassy/sexagisimal_elliptical/ entry')

    # report where request is coming from
    forwarded_ips = request.headers.getlist('X-Forwarded-For')
    client_ip = forwarded_ips[0].split(',')[0] if len(forwarded_ips) >= 1 else ''
    logger.info('incoming request', extra={'tags': {'requesting_ip': client_ip, 'request_args': request.args}})
    page = request.args.get('page', 1, type=int)

    # build form
    form = SexagisimalEllipticalQueryForm()

    # validate form (POST request)
    if form.validate_on_submit():

        # get data
        _ra = form.ra.data
        _dra = ra_to_decimal(_ra)
        _dec = form.dec.data
        _ddec = dec_to_decimal(_dec)
        _maj = float(form.majaxis.data)
        _rat = float(form.ratio.data)
        _pos = float(form.posang.data)
        _cat = form.catalog.data.lower()
        logger.debug(f'SexagisimalEllipticalQueryForm(), _ra={_ra} ({_dra}), _dec={_dec} ({_ddec}), '
                     f'_rat={_rat}, _pos={_pos}, _cat={_cat}')

        _dbh = None
        _fil = None
        _rec = None
        latest = None
        if _cat == 'glade_q3c':
            _dbh = db_glade_q3c
            _fil = glade_q3c_filters
            _rec = GladeQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.gwgc.desc()).first()
        elif _cat == 'gwgc_q3c':
            _dbh = db_gwgc_q3c
            _fil = gwgc_q3c_filters
            _rec = GwgcQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.name.desc()).first()
        elif _cat == 'ligo_q3c':
            _dbh = db_ligo_q3c
            _fil = ligo_q3c_filters
            _rec = LigoQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.name.desc()).first()
        elif _cat == 'tns_q3c':
            _dbh = db_tns_q3c
            _fil = tns_q3c_filters
            _rec = TnsQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.tns_name.desc()).first()

        query = _dbh.session.query(_rec)
        query = _fil(query, {"ellipse": f"{_dra},{_ddec},{_maj},{_rat},{_pos}"})
        paginator = query.paginate(page, RESULTS_PER_PAGE, True)
        response = {
            'total': paginator.total,
            'pages': paginator.pages,
            'has_next': paginator.has_next,
            'has_prev': paginator.has_prev,
            'results': _rec.serialize_list(paginator.items)
        }
        if _request_wants_json() or request.method == 'GET':
            return jsonify(response)

        _args = request.args.copy()
        try:
            _args.pop('page')
        except:
            pass
        arg_str = urlencode(_args)
        return render_template(f'{_cat}.html', context=response, page=paginator.page, arg_str=arg_str, latest=latest,
                               url={'url': f'{SASSY_APP_URL}', 'page': f'{_cat}'})

    # return for GET
    return render_template('sexagisimal_elliptical_query.html', form=form)


# +
# route(s): /sexagisimal_radial/, /sassy/sexagisimal_radial/
# -
# noinspection PyBroadException
@app.route('/sassy/sexagisimal_radial/', methods=['GET', 'POST'])
@app.route('/sexagisimal_radial/', methods=['GET', 'POST'])
def sassy_sexagisimal_radial():
    logger.debug(f'route /sassy/sexagisimal_radial/ entry')

    # report where request is coming from
    forwarded_ips = request.headers.getlist('X-Forwarded-For')
    client_ip = forwarded_ips[0].split(',')[0] if len(forwarded_ips) >= 1 else ''
    logger.info('incoming request', extra={'tags': {'requesting_ip': client_ip, 'request_args': request.args}})
    page = request.args.get('page', 1, type=int)

    # build form
    form = SexagisimalRadialQueryForm()

    # validate form (POST request)
    if form.validate_on_submit():

        # get data
        _ra = form.ra.data
        _dra = ra_to_decimal(_ra)
        _dec = form.dec.data
        _ddec = dec_to_decimal(_dec)
        _rad = float(form.radius.data)
        _cat = form.catalog.data.lower()
        logger.debug(f'SexagisimalRadialQueryForm(), _ra={_ra} ({_dra}), _dec={_dec} ({_ddec}), '
                     f'_rad={_rad}, _cat={_cat}')

        _dbh = None
        _fil = None
        _rec = None
        latest = None
        if _cat == 'glade_q3c':
            _dbh = db_glade_q3c
            _fil = glade_q3c_filters
            _rec = GladeQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.gwgc.desc()).first()
        elif _cat == 'gwgc_q3c':
            _dbh = db_gwgc_q3c
            _fil = gwgc_q3c_filters
            _rec = GwgcQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.name.desc()).first()
        elif _cat == 'ligo_q3c':
            _dbh = db_ligo_q3c
            _fil = ligo_q3c_filters
            _rec = LigoQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.name.desc()).first()
        elif _cat == 'tns_q3c':
            _dbh = db_tns_q3c
            _fil = tns_q3c_filters
            _rec = TnsQ3cRecord
            latest = _dbh.session.query(_rec).order_by(_rec.tns_name.desc()).first()

        query = _dbh.session.query(_rec)
        query = _fil(query, {"cone": f"{_dra},{_ddec},{_rad}"})
        paginator = query.paginate(page, RESULTS_PER_PAGE, True)
        response = {
            'total': paginator.total,
            'pages': paginator.pages,
            'has_next': paginator.has_next,
            'has_prev': paginator.has_prev,
            'results': _rec.serialize_list(paginator.items)
        }
        if _request_wants_json() or request.method == 'GET':
            return jsonify(response)

        _args = request.args.copy()
        try:
            _args.pop('page')
        except:
            pass
        arg_str = urlencode(_args)
        return render_template(f'{_cat}.html', context=response, page=paginator.page, arg_str=arg_str, latest=latest,
                               url={'url': f'{SASSY_APP_URL}', 'page': f'{_cat}'})

    # return for GET
    return render_template('sexagisimal_radial_query.html', form=form)


# +
# route(s): /glade/, /sassy/glade/
# -
# noinspection PyBroadException
@app.route('/sassy/glade/', methods=['GET', 'POST'])
@app.route('/glade/', methods=['GET', 'POST'])
def glade_records():
    logger.debug(f'route /sassy/glade/ entry')

    # report where request is coming from
    forwarded_ips = request.headers.getlist('X-Forwarded-For')
    client_ip = forwarded_ips[0].split(',')[0] if len(forwarded_ips) >= 1 else ''
    logger.info('incoming request', extra={'tags': {'requesting_ip': client_ip, 'request_args': request.args}})
    page = request.args.get('page', 1, type=int)

    # set default(s)
    paginator = None
    latest = None
    response = {}
    _args = request.args.copy()
    if 'sort_order' not in _args:
        _args['sort_order'] = 'ascending'
    if 'sort_value' not in _args:
        _args['sort_value'] = 'id'

    # GET request
    if request.method == 'GET':

        # query database
        query = db_glade.session.query(GladeRecord)
        query = glade_filters(query, _args)

        # get latest alert
        latest = db_glade.session.query(GladeRecord).order_by(GladeRecord.gwgc.desc()).first()

        # paginate
        paginator = query.paginate(page, RESULTS_PER_PAGE, True)

        # set response dictionary
        response = {
            'total': paginator.total,
            'pages': paginator.pages,
            'has_next': paginator.has_next,
            'has_prev': paginator.has_prev,
            'results': GladeRecord.serialize_list(paginator.items)
        }

    # POST request
    if request.method == 'POST':

        # get search criteria
        searches = request.get_json().get('queries')

        # initialize output(s)
        search_results = []
        total = 0

        # iterate over searches
        for search_args in searches:

            # initialize result(s)
            search_result = {}

            # query database
            query = db_glade.session.query(GladeRecord)
            query = glade_filters(query, search_args)

            # extract, transform and load (ETL) into result(s)
            search_result['query'] = search_args
            search_result['num_alerts'] = query.count()
            search_result['results'] = GladeRecord.serialize_list(query.all())
            search_results.append(search_result)
            total += search_result['num_alerts']

        # set response dictionary
        response = {
            'total': total,
            'results': search_results
        }

    # return response in desired format
    if _request_wants_json() or request.method == 'POST':
        return jsonify(response)
    else:
        _args = request.args.copy()
        try:
            _args.pop('page')
        except:
            pass
        arg_str = urlencode(_args)
        return render_template('glade.html', context=response, page=paginator.page, arg_str=arg_str, latest=latest,
                               url={'url': f'{SASSY_APP_URL}', 'page': 'glade'})


# +
# route(s): /glade/<int:id>/, /sassy/glade/<int:id>/
# -
# noinspection PyShadowingBuiltins
@app.route('/sassy/glade/<int:dbid>/')
@app.route('/glade/<int:dbid>/')
def glade_detail(dbid=0):
    logger.debug(f'route /sassy/glade/{dbid}/ entry')

    # get observation request
    _record = GladeRecord.query.filter_by(id=dbid).first_or_404()

    # show record
    if _record:
        _format = request.args.get('?format', None)
        if _format is not None and _format.lower() == 'json':
            return jsonify(_record.serialized())
        else:
            _format = request.args.get('format', None)
            if _format is not None and _format.lower() == 'json':
                return jsonify(_record.serialized())
            else:
                return render_template('glade_record.html', record=_record)


# +
# route(s): /glade/text/, /sassy/glade/text/
# -
# noinspection PyShadowingBuiltins
@app.route('/sassy/glade/text/')
@app.route('/glade/text/')
def glade_text():
    logger.debug(f'route /sassy/glade/text/ entry')
    return render_template('glade_text.html', text=glade_get_text())


# +
# route(s): /glade_q3c/, /sassy/glade_q3c/
# -
# noinspection PyBroadException
@app.route('/sassy/glade_q3c/', methods=['GET', 'POST'])
@app.route('/glade_q3c/', methods=['GET', 'POST'])
def glade_q3c_records():
    logger.debug(f'route /sassy/glade_q3c/ entry')

    # report where request is coming from
    forwarded_ips = request.headers.getlist('X-Forwarded-For')
    client_ip = forwarded_ips[0].split(',')[0] if len(forwarded_ips) >= 1 else ''
    logger.info('incoming request', extra={'tags': {'requesting_ip': client_ip, 'request_args': request.args}})
    page = request.args.get('page', 1, type=int)
    response = {}

    # set default(s)
    latest = None
    paginator = None
    _args = request.args.copy()
    if 'sort_order' not in _args:
        _args['sort_order'] = 'ascending'
    if 'sort_value' not in _args:
        _args['sort_value'] = 'id'

    # GET request
    if request.method == 'GET':

        # query database
        query = db_glade_q3c.session.query(GladeQ3cRecord)
        query = glade_q3c_filters(query, _args)

        # get latest alert
        latest = db_glade_q3c.session.query(GladeQ3cRecord).order_by(GladeQ3cRecord.gwgc.desc()).first()

        # paginate
        paginator = query.paginate(page, RESULTS_PER_PAGE, True)

        # set response dictionary
        response = {
            'total': paginator.total,
            'pages': paginator.pages,
            'has_next': paginator.has_next,
            'has_prev': paginator.has_prev,
            'results': GladeQ3cRecord.serialize_list(paginator.items)
        }

    # POST request
    if request.method == 'POST':

        # get search criteria
        searches = request.get_json().get('queries')

        # initialize output(s)
        search_results = []
        total = 0

        # iterate over searches
        for search_args in searches:

            # initialize result(s)
            search_result = {}

            # query database
            query = db_glade_q3c.session.query(GladeQ3cRecord)
            query = glade_q3c_filters(query, search_args)

            # extract,transform and load (ETL) into result(s)
            search_result['query'] = search_args
            search_result['num_alerts'] = query.count()
            search_result['results'] = GladeQ3cRecord.serialize_list(query.all())
            search_results.append(search_result)
            total += search_result['num_alerts']

        # set response dictionary
        response = {
            'total': total,
            'results': search_results
        }

    # return response in desired format
    if _request_wants_json() or request.method == 'POST':
        return jsonify(response)
    else:
        _args = request.args.copy()
        try:
            _args.pop('page')
        except:
            pass
        arg_str = urlencode(_args)
        return render_template('glade_q3c.html', context=response, page=paginator.page, arg_str=arg_str, latest=latest,
                               url={'url': f'{SASSY_APP_URL}', 'page': 'glade_q3c'})


# +
# route(s): /glade_q3c/<int:id>/, /sassy/glade_q3c/<int:id>/
# -
# noinspection PyShadowingBuiltins
@app.route('/sassy/glade_q3c/<int:dbid>/')
@app.route('/glade_q3c/<int:dbid>/')
def glade_q3c_detail(dbid=0):
    logger.debug(f'route /sassy/glade_q3c/{dbid}/ entry')

    # get observation request
    _record = GladeQ3cRecord.query.filter_by(id=dbid).first_or_404()

    # show record
    if _record:
        _format = request.args.get('?format', None)
        if _format is not None and _format.lower() == 'json':
            return jsonify(_record.serialized())
        else:
            _format = request.args.get('format', None)
            if _format is not None and _format.lower() == 'json':
                return jsonify(_record.serialized())
            else:
                return render_template('glade_q3c_record.html', record=_record)


# +
# route(s): /glade_q3c/text/, /sassy/glade_q3c/text/
# -
# noinspection PyShadowingBuiltins
@app.route('/sassy/glade_q3c/text/')
@app.route('/glade_q3c/text/')
def glade_q3c_text():
    logger.debug(f'route /sassy/glade_q3c/text/ entry')
    return render_template('glade_q3c_text.html', text=glade_q3c_get_text())


# +
# route(s): /gwgc/, /sassy/gwgc/
# -
# noinspection PyBroadException
@app.route('/sassy/gwgc/', methods=['GET', 'POST'])
@app.route('/gwgc/', methods=['GET', 'POST'])
def gwgc_records():
    logger.debug(f'route /sassy/gwgc/ entry')

    # report where request is coming from
    forwarded_ips = request.headers.getlist('X-Forwarded-For')
    client_ip = forwarded_ips[0].split(',')[0] if len(forwarded_ips) >= 1 else ''
    logger.info('incoming request', extra={'tags': {'requesting_ip': client_ip, 'request_args': request.args}})
    page = request.args.get('page', 1, type=int)
    response = {}

    # set default(s)
    latest = None
    paginator = None
    _args = request.args.copy()
    if 'sort_order' not in _args:
        _args['sort_order'] = 'ascending'
    if 'sort_value' not in _args:
        _args['sort_value'] = 'id'

    # GET request
    if request.method == 'GET':

        # query database
        query = db_gwgc.session.query(GwgcRecord)
        query = gwgc_filters(query, _args)

        # get latest alert
        latest = db_gwgc.session.query(GwgcRecord).order_by(GwgcRecord.name.desc()).first()

        # paginate
        paginator = query.paginate(page, RESULTS_PER_PAGE, True)

        # set response dictionary
        response = {
            'total': paginator.total,
            'pages': paginator.pages,
            'has_next': paginator.has_next,
            'has_prev': paginator.has_prev,
            'results': GwgcRecord.serialize_list(paginator.items)
        }

    # POST request
    if request.method == 'POST':

        # get search criteria
        searches = request.get_json().get('queries')

        # initialize output(s)
        search_results = []
        total = 0

        # iterate over searches
        for search_args in searches:

            # initialize result(s)
            search_result = {}

            # query database
            query = db_gwgc.session.query(GwgcRecord)
            query = gwgc_filters(query, search_args)

            # extract,transform and load (ETL) into result(s)
            search_result['query'] = search_args
            search_result['num_alerts'] = query.count()
            search_result['results'] = GwgcRecord.serialize_list(query.all())
            search_results.append(search_result)
            total += search_result['num_alerts']

        # set response dictionary
        response = {
            'total': total,
            'results': search_results
        }

    # return response in desired format
    if _request_wants_json() or request.method == 'POST':
        return jsonify(response)
    else:
        _args = request.args.copy()
        try:
            _args.pop('page')
        except:
            pass
        arg_str = urlencode(_args)
        return render_template('gwgc.html', context=response, page=paginator.page, arg_str=arg_str, latest=latest,
                               url={'url': f'{SASSY_APP_URL}', 'page': 'gwgc'})


# +
# route(s): /gwgc/<int:id>/, /sassy/gwgc/<int:id>/
# -
# noinspection PyShadowingBuiltins
@app.route('/sassy/gwgc/<int:dbid>/')
@app.route('/gwgc/<int:dbid>/')
def gwgc_detail(dbid=0):
    logger.debug(f'route /sassy/gwgc/{dbid}/ entry')

    # get observation request
    _record = GwgcRecord.query.filter_by(id=dbid).first_or_404()

    # show record
    if _record:
        _format = request.args.get('?format', None)
        if _format is not None and _format.lower() == 'json':
            return jsonify(_record.serialized())
        else:
            _format = request.args.get('format', None)
            if _format is not None and _format.lower() == 'json':
                return jsonify(_record.serialized())
            else:
                return render_template('gwgc_record.html', record=_record)


# +
# route(s): /gwgc/text/, /sassy/gwgc/text/
# -
# noinspection PyShadowingBuiltins
@app.route('/sassy/gwgc/text/')
@app.route('/gwgc/text/')
def gwgc_text():
    logger.debug(f'route /sassy/gwgc/text/ entry')
    return render_template('gwgc_text.html', text=gwgc_get_text())


# +
# route(s): /gwgc_q3c/, /sassy/gwgc_q3c/
# -
# noinspection PyBroadException
@app.route('/sassy/gwgc_q3c/', methods=['GET', 'POST'])
@app.route('/gwgc_q3c/', methods=['GET', 'POST'])
def gwgc_q3c_records():
    logger.debug(f'route /sassy/gwgc_q3c/ entry')

    # report where request is coming from
    forwarded_ips = request.headers.getlist('X-Forwarded-For')
    client_ip = forwarded_ips[0].split(',')[0] if len(forwarded_ips) >= 1 else ''
    logger.info('incoming request', extra={'tags': {'requesting_ip': client_ip, 'request_args': request.args}})
    page = request.args.get('page', 1, type=int)
    response = {}

    # set default(s)
    latest = None
    paginator = None
    _args = request.args.copy()
    if 'sort_order' not in _args:
        _args['sort_order'] = 'ascending'
    if 'sort_value' not in _args:
        _args['sort_value'] = 'id'

    # GET request
    if request.method == 'GET':

        # query database
        query = db_gwgc_q3c.session.query(GwgcQ3cRecord)
        query = gwgc_q3c_filters(query, _args)

        # get latest alert
        latest = db_gwgc_q3c.session.query(GwgcQ3cRecord).order_by(GwgcQ3cRecord.name.desc()).first()

        # paginate
        paginator = query.paginate(page, RESULTS_PER_PAGE, True)

        # set response dictionary
        response = {
            'total': paginator.total,
            'pages': paginator.pages,
            'has_next': paginator.has_next,
            'has_prev': paginator.has_prev,
            'results': GwgcQ3cRecord.serialize_list(paginator.items)
        }

    # POST request
    if request.method == 'POST':

        # get search criteria
        searches = request.get_json().get('queries')

        # initialize output(s)
        search_results = []
        total = 0

        # iterate over searches
        for search_args in searches:

            # initialize result(s)
            search_result = {}

            # query database
            query = db_gwgc_q3c.session.query(GwgcQ3cRecord)
            query = gwgc_q3c_filters(query, search_args)

            # extract,transform and load (ETL) into result(s)
            search_result['query'] = search_args
            search_result['num_alerts'] = query.count()
            search_result['results'] = GwgcQ3cRecord.serialize_list(query.all())
            search_results.append(search_result)
            total += search_result['num_alerts']

        # set response dictionary
        response = {
            'total': total,
            'results': search_results
        }

    # return response in desired format
    if _request_wants_json() or request.method == 'POST':
        return jsonify(response)
    else:
        _args = request.args.copy()
        try:
            _args.pop('page')
        except:
            pass
        arg_str = urlencode(_args)
        return render_template('gwgc_q3c.html', context=response, page=paginator.page, arg_str=arg_str, latest=latest,
                               url={'url': f'{SASSY_APP_URL}', 'page': 'gwgc_q3c'})


# +
# route(s): /gwgc_q3c/<int:id>/, /sassy/gwgc_q3c/<int:id>/
# -
# noinspection PyShadowingBuiltins
@app.route('/sassy/gwgc_q3c/<int:dbid>/')
@app.route('/gwgc_q3c/<int:dbid>/')
def gwgc_q3c_detail(dbid=0):
    logger.debug(f'route /sassy/gwgc_q3c/{dbid}/ entry')

    # get observation request
    _record = GwgcQ3cRecord.query.filter_by(id=dbid).first_or_404()

    # show record
    if _record:
        _format = request.args.get('?format', None)
        if _format is not None and _format.lower() == 'json':
            return jsonify(_record.serialized())
        else:
            _format = request.args.get('format', None)
            if _format is not None and _format.lower() == 'json':
                return jsonify(_record.serialized())
            else:
                return render_template('gwgc_q3c_record.html', record=_record)


# +
# route(s): /gwgc_q3c/text/, /sassy/gwgc_q3c/text/
# -
# noinspection PyShadowingBuiltins
@app.route('/sassy/gwgc_q3c/text/')
@app.route('/gwgc_q3c/text/')
def gwgc_q3c_text():
    logger.debug(f'route /sassy/gwgc_q3c/text/ entry')
    return render_template('gwgc_q3c_text.html', text=gwgc_q3c_get_text())


# +
# route(s): /help/, /sassy/help/
# -
@app.route('/sassy/help/')
@app.route('/help/')
def sassy_help():
    logger.debug(f'route /sassy/help/ entry')
    return render_template('help.html', url={'url': f'{SASSY_APP_URL}'})


# +
# route(s): /ligo/, /sassy/ligo/
# -
# noinspection PyBroadException
@app.route('/sassy/ligo/', methods=['GET', 'POST'])
@app.route('/ligo/', methods=['GET', 'POST'])
def ligo_records():
    logger.debug(f'route /sassy/ligo/ entry')

    # report where request is coming from
    forwarded_ips = request.headers.getlist('X-Forwarded-For')
    client_ip = forwarded_ips[0].split(',')[0] if len(forwarded_ips) >= 1 else ''
    logger.info('incoming request', extra={'tags': {'requesting_ip': client_ip, 'request_args': request.args}})
    page = request.args.get('page', 1, type=int)
    response = {}

    # set default(s)
    latest = None
    paginator = None
    _args = request.args.copy()
    if 'sort_order' not in _args:
        _args['sort_order'] = 'descending'
    if 'sort_value' not in _args:
        _args['sort_value'] = 'discovery_date'

    # GET request
    if request.method == 'GET':

        # query database
        query = db_ligo.session.query(LigoRecord)
        query = ligo_filters(query, _args)

        # get latest alert
        latest = db_ligo.session.query(LigoRecord).order_by(LigoRecord.name.desc()).first()

        # paginate
        paginator = query.paginate(page, RESULTS_PER_PAGE, True)

        # set response dictionary
        response = {
            'total': paginator.total,
            'pages': paginator.pages,
            'has_next': paginator.has_next,
            'has_prev': paginator.has_prev,
            'results': LigoRecord.serialize_list(paginator.items)
        }
        logger.debug(f'response={response}')

    # POST request
    if request.method == 'POST':

        # get search criteria
        searches = request.get_json().get('queries')

        # initialize output(s)
        search_results = []
        total = 0

        # iterate over searches
        for search_args in searches:

            # initialize result(s)
            search_result = {}

            # query database
            query = db_ligo.session.query(LigoRecord)
            query = ligo_filters(query, search_args)

            # extract,transform and load (ETL) into result(s)
            search_result['query'] = search_args
            search_result['num_alerts'] = query.count()
            search_result['results'] = LigoRecord.serialize_list(query.all())
            search_results.append(search_result)
            total += search_result['num_alerts']

        # set response dictionary
        response = {
            'total': total,
            'results': search_results
        }

    # return response in desired format
    if _request_wants_json() or request.method == 'POST':
        return jsonify(response)
    else:
        _args = request.args.copy()
        try:
            _args.pop('page')
        except:
            pass
        arg_str = urlencode(_args)
        return render_template('ligo.html', context=response, page=paginator.page, arg_str=arg_str, latest=latest,
                               url={'url': f'{SASSY_APP_URL}', 'page': 'ligo'})


# +
# route(s): /ligo/<int:id>/, /sassy/ligo/<int:id>/
# -
# noinspection PyShadowingBuiltins
@app.route('/sassy/ligo/<int:dbid>/')
@app.route('/ligo/<int:dbid>/')
def ligo_detail(dbid=0):
    logger.debug(f'route /sassy/ligo/{dbid}/ entry')

    # get observation request
    _record = LigoRecord.query.filter_by(id=dbid).first_or_404()

    # show record
    if _record:
        _format = request.args.get('?format', None)
        if _format is not None and _format.lower() == 'json':
            return jsonify(_record.serialized())
        else:
            _format = request.args.get('format', None)
            if _format is not None and _format.lower() == 'json':
                return jsonify(_record.serialized())
            else:
                return render_template('ligo_record.html', record=_record)


# +
# route(s): /ligo/text/, /sassy/ligo/text/
# -
@app.route('/sassy/ligo/text/')
@app.route('/ligo/text/')
def ligo_text():
    logger.debug(f'route /sassy/ligo/text/ entry')
    return render_template('ligo_text.html', text=ligo_get_text())


# +
# route(s): /ligo_q3c/, /sassy/ligo_q3c/
# -
# noinspection PyBroadException
@app.route('/sassy/ligo_q3c/', methods=['GET', 'POST'])
@app.route('/ligo_q3c/', methods=['GET', 'POST'])
def ligo_q3c_records():
    logger.debug(f'route /sassy/ligo_q3c/ entry')

    # report where request is coming from
    forwarded_ips = request.headers.getlist('X-Forwarded-For')
    client_ip = forwarded_ips[0].split(',')[0] if len(forwarded_ips) >= 1 else ''
    logger.info('incoming request', extra={'tags': {'requesting_ip': client_ip, 'request_args': request.args}})
    page = request.args.get('page', 1, type=int)
    response = {}

    # set default(s)
    latest = None
    paginator = None
    _args = request.args.copy()
    if 'sort_order' not in _args:
        _args['sort_order'] = 'descending'
    if 'sort_value' not in _args:
        _args['sort_value'] = 'discovery_date'

    # GET request
    if request.method == 'GET':

        # query database
        query = db_ligo_q3c.session.query(LigoQ3cRecord)
        query = ligo_q3c_filters(query, _args)

        # get latest alert
        latest = db_ligo_q3c.session.query(LigoQ3cRecord).order_by(LigoQ3cRecord.name.desc()).first()

        # paginate
        paginator = query.paginate(page, RESULTS_PER_PAGE, True)

        # set response dictionary
        response = {
            'total': paginator.total,
            'pages': paginator.pages,
            'has_next': paginator.has_next,
            'has_prev': paginator.has_prev,
            'results': LigoQ3cRecord.serialize_list(paginator.items)
        }
        logger.debug(f'response={response}')

    # POST request
    if request.method == 'POST':

        # get search criteria
        searches = request.get_json().get('queries')

        # initialize output(s)
        search_results = []
        total = 0

        # iterate over searches
        for search_args in searches:

            # initialize result(s)
            search_result = {}

            # query database
            query = db_ligo_q3c.session.query(LigoQ3cRecord)
            query = ligo_q3c_filters(query, search_args)

            # extract,transform and load (ETL) into result(s)
            search_result['query'] = search_args
            search_result['num_alerts'] = query.count()
            search_result['results'] = LigoQ3cRecord.serialize_list(query.all())
            search_results.append(search_result)
            total += search_result['num_alerts']

        # set response dictionary
        response = {
            'total': total,
            'results': search_results
        }

    # return response in desired format
    if _request_wants_json() or request.method == 'POST':
        return jsonify(response)
    else:
        _args = request.args.copy()
        try:
            _args.pop('page')
        except:
            pass
        arg_str = urlencode(_args)
        return render_template('ligo_q3c.html', context=response, page=paginator.page, arg_str=arg_str, latest=latest,
                               url={'url': f'{SASSY_APP_URL}', 'page': 'ligo_q3c'})


# +
# route(s): /ligo_q3c/<int:id>/, /sassy/ligo_q3c/<int:id>/
# -
# noinspection PyShadowingBuiltins
@app.route('/sassy/ligo_q3c/<int:dbid>/')
@app.route('/ligo_q3c/<int:dbid>/')
def ligo_q3c_detail(dbid=0):
    logger.debug(f'route /sassy/ligo_q3c/{dbid}/ entry')

    # get observation request
    _record = LigoQ3cRecord.query.filter_by(id=dbid).first_or_404()

    # show record
    if _record:
        _format = request.args.get('?format', None)
        if _format is not None and _format.lower() == 'json':
            return jsonify(_record.serialized())
        else:
            _format = request.args.get('format', None)
            if _format is not None and _format.lower() == 'json':
                return jsonify(_record.serialized())
            else:
                return render_template('ligo_q3c_record.html', record=_record)


# +
# route(s): /ligo_q3c/text/, /sassy/ligo_q3c/text/
# -
@app.route('/sassy/ligo_q3c/text/')
@app.route('/ligo_q3c/text/')
def ligo_q3c_text():
    logger.debug(f'route /sassy/ligo_q3c/text/ entry')
    return render_template('ligo_q3c_text.html', text=ligo_q3c_get_text())


# +
# route(s): /psql/, /sassy/psql/
# -
@app.route('/sassy/psql/', methods=['GET', 'POST'])
@app.route('/psql/', methods=['GET', 'POST'])
def psql_query():
    logger.debug(f'route /sassy/psql/ entry')

    # connect to database
    db_psql = None
    try:
        db_psql = Psql(f'{SASSY_DB_USER}:{SASSY_DB_PASS}', f'{SASSY_DB_NAME}',
                       int(f'{SASSY_DB_PORT}'), f'{SASSY_DB_HOST}', logger)
        db_psql.connect()
    except Exception as e:
        logger.error(f'failed connecting via Psql({PSQL_CONNECT_MSG}), error={e}')

    # build form
    form = PsqlQueryForm()

    # validate form (POST request)
    search_results = []
    if form.validate_on_submit():

        # get data
        _sql_query = form.sql_query.data
        logger.debug(f'query=\"{_sql_query}\"')

        # execute query
        if db_psql and hasattr(db_psql, 'fetchall'):
            _results = db_psql.fetchall(_sql_query)
            logger.debug(f'_results={_results}')
            for _e in _results:
                search_results.append(_e)

        response = {
            'total': len(search_results),
            'results': search_results
        }
        return render_template('psql_query_results.html', context=response)

    # return for GET
    return render_template('psql_query.html', form=form)


# +
# route(s): /tns/, /sassy/tns/
# -
# noinspection PyBroadException
@app.route('/sassy/tns/', methods=['GET', 'POST'])
@app.route('/tns/', methods=['GET', 'POST'])
def tns_records():
    logger.debug(f'route /sassy/tns/ entry')

    # report where request is coming from
    forwarded_ips = request.headers.getlist('X-Forwarded-For')
    client_ip = forwarded_ips[0].split(',')[0] if len(forwarded_ips) >= 1 else ''
    logger.info('incoming request', extra={'tags': {'requesting_ip': client_ip, 'request_args': request.args}})
    page = request.args.get('page', 1, type=int)
    response = {}

    # set default(s)
    latest = None
    paginator = None
    _args = request.args.copy()
    if 'sort_order' not in _args:
        _args['sort_order'] = 'descending'
    if 'sort_value' not in _args:
        _args['sort_value'] = 'discovery_date'

    # GET request
    if request.method == 'GET':

        # query database
        query = db_tns.session.query(TnsRecord)
        query = tns_filters(query, _args)

        # get latest alert
        latest = db_tns.session.query(TnsRecord).order_by(TnsRecord.tns_name.desc()).first()

        # paginate
        paginator = query.paginate(page, RESULTS_PER_PAGE, True)

        # set response dictionary
        response = {
            'total': paginator.total,
            'pages': paginator.pages,
            'has_next': paginator.has_next,
            'has_prev': paginator.has_prev,
            'results': TnsRecord.serialize_list(paginator.items)
        }
        logger.debug(f'response={response}')

    # POST request
    if request.method == 'POST':

        # get search criteria
        searches = request.get_json().get('queries')

        # initialize output(s)
        search_results = []
        total = 0

        # iterate over searches
        for search_args in searches:

            # initialize result(s)
            search_result = {}

            # query database
            query = db_tns.session.query(TnsRecord)
            query = tns_filters(query, search_args)

            # extract,transform and load (ETL) into result(s)
            search_result['query'] = search_args
            search_result['num_alerts'] = query.count()
            search_result['results'] = TnsRecord.serialize_list(query.all())
            search_results.append(search_result)
            total += search_result['num_alerts']

        # set response dictionary
        response = {
            'total': total,
            'results': search_results
        }

    # return response in desired format
    if _request_wants_json() or request.method == 'POST':
        return jsonify(response)
    else:
        _args = request.args.copy()
        try:
            _args.pop('page')
        except:
            pass
        arg_str = urlencode(_args)
        return render_template('tns.html', context=response, page=paginator.page, arg_str=arg_str, latest=latest,
                               url={'url': f'{SASSY_APP_URL}', 'page': 'tns'})


# +
# route(s): /tns/<int:id>/, /sassy/tns/<int:id>/
# -
# noinspection PyShadowingBuiltins
@app.route('/sassy/tns/<int:dbid>/')
@app.route('/tns/<int:dbid>/')
def tns_detail(dbid=0):
    logger.debug(f'route /sassy/tns/{dbid}/ entry')

    # get observation request
    _record = TnsRecord.query.filter_by(id=dbid).first_or_404()

    # show record
    if _record:
        _format = request.args.get('?format', None)
        if _format is not None and _format.lower() == 'json':
            return jsonify(_record.serialized())
        else:
            _format = request.args.get('format', None)
            if _format is not None and _format.lower() == 'json':
                return jsonify(_record.serialized())
            else:
                return render_template('tns_record.html', record=_record)
    else:
        logger.debug(f'no record found')


# +
# route(s): /tns/text/, /sassy/tns/text/
# -
@app.route('/sassy/tns/text/')
@app.route('/tns/text/')
def tns_text():
    logger.debug(f'route /sassy/tns/text/ entry')
    return render_template('tns_text.html', text=tns_get_text())


# +
# route(s): /tns_q3c/, /sassy/tns_q3c/
# -
# noinspection PyBroadException
@app.route('/sassy/tns_q3c/', methods=['GET', 'POST'])
@app.route('/tns_q3c/', methods=['GET', 'POST'])
def tns_q3c_records():
    logger.debug(f'route /sassy/tns_q3c/ entry')

    # report where request is coming from
    forwarded_ips = request.headers.getlist('X-Forwarded-For')
    client_ip = forwarded_ips[0].split(',')[0] if len(forwarded_ips) >= 1 else ''
    logger.info('incoming request', extra={'tags': {'requesting_ip': client_ip, 'request_args': request.args}})
    page = request.args.get('page', 1, type=int)
    response = {}

    # set default(s)
    latest = None
    paginator = None
    _args = request.args.copy()
    if 'sort_order' not in _args:
        _args['sort_order'] = 'descending'
    if 'sort_value' not in _args:
        _args['sort_value'] = 'discovery_date'

    # GET request
    if request.method == 'GET':

        # query database
        query = db_tns_q3c.session.query(TnsQ3cRecord)
        query = tns_q3c_filters(query, _args)

        # get latest alert
        latest = db_tns_q3c.session.query(TnsQ3cRecord).order_by(TnsQ3cRecord.tns_name.desc()).first()

        # paginate
        paginator = query.paginate(page, RESULTS_PER_PAGE, True)

        # set response dictionary
        response = {
            'total': paginator.total,
            'pages': paginator.pages,
            'has_next': paginator.has_next,
            'has_prev': paginator.has_prev,
            'results': TnsQ3cRecord.serialize_list(paginator.items)
        }
        logger.debug(f'response={response}')

    # POST request
    if request.method == 'POST':

        # get search criteria
        searches = request.get_json().get('queries')

        # initialize output(s)
        search_results = []
        total = 0

        # iterate over searches
        for search_args in searches:

            # initialize result(s)
            search_result = {}

            # query database
            query = db_tns_q3c.session.query(TnsQ3cRecord)
            query = tns_q3c_filters(query, search_args)

            # extract,transform and load (ETL) into result(s)
            search_result['query'] = search_args
            search_result['num_alerts'] = query.count()
            search_result['results'] = TnsQ3cRecord.serialize_list(query.all())
            search_results.append(search_result)
            total += search_result['num_alerts']

        # set response dictionary
        response = {
            'total': total,
            'results': search_results
        }

    # return response in desired format
    if _request_wants_json() or request.method == 'POST':
        return jsonify(response)
    else:
        _args = request.args.copy()
        try:
            _args.pop('page')
        except:
            pass
        arg_str = urlencode(_args)
        return render_template('tns_q3c.html', context=response, page=paginator.page, arg_str=arg_str, latest=latest,
                               url={'url': f'{SASSY_APP_URL}', 'page': 'tns_q3c'})


# +
# route(s): /tns_q3c/<int:id>/, /sassy/tns_q3c/<int:id>/
# -
# noinspection PyShadowingBuiltins
@app.route('/sassy/tns_q3c/<int:dbid>/')
@app.route('/tns_q3c/<int:dbid>/')
def tns_q3c_detail(dbid=0):
    logger.debug(f'route /sassy/tns_q3c/{dbid}/ entry')

    # get observation request
    _record = TnsQ3cRecord.query.filter_by(id=dbid).first_or_404()

    # show record
    if _record:
        _format = request.args.get('?format', None)
        if _format is not None and _format.lower() == 'json':
            return jsonify(_record.serialized())
        else:
            _format = request.args.get('format', None)
            if _format is not None and _format.lower() == 'json':
                return jsonify(_record.serialized())
            else:
                return render_template('tns_q3c_record.html', record=_record)
    else:
        logger.debug(f'no record found')


# +
# route(s): /tns_q3c/text/, /sassy/tns_q3c/text/
# -
@app.route('/sassy/tns_q3c/text/')
@app.route('/tns_q3c/text/')
def tns_q3c_text():
    logger.debug(f'route /sassy/tns_q3c/text/ entry')
    return render_template('tns_q3c_text.html', text=tns_q3c_get_text())


# +
# route(s): /ztf/<int:id>/, /sassy/ztf/<int:id>/
# -
# noinspection PyShadowingBuiltins,PyBroadException
@app.route('/sassy/ztf/<int:id>/')
@app.route('/ztf/<int:id>/')
def ztf_detail(id=0):
    logger.debug(f'route /sassy/ztf/{id}/ entry')

    # check input(s)
    details = [{'format': '<number>', 'line': '', 'name': 'id', 'route': f'/sassy/ztf/{id}',
                'type': 'int', 'url': f'{SASSY_APP_URL}/ztf/{id}/', 'value': f'{id}'}]
    if not isinstance(id, int) or id <= 0:
        logger.warning(f'input(s) are invalid')
        details[0]['line'] = 'at entry'
        return render_template('error.html', details=details)

    # get data
    alert = None
    try:
        alert = db_ztf.session.query(ZtfAlert).get(id)
    except Exception as _e:
        logger.warning(f'alert not found, alert={alert}, error={_e}')
        details[0]['line'] = 'at db.session.query()'
        return render_template('error.html', details=details)
    else:
        logger.info(f'alert={alert} is OK, type={type(alert)}')

    # return data
    if alert is not None:
        if _request_wants_json():
            logger.info(f'rendering ztf_record.html as JSON alert={alert}')
            return jsonify(alert.serialized(prv_candidate=True))
        else:
            logger.info(f'rendering ztf_record.html alert={alert}')
            return render_template('ztf_record.html', alert=alert)

    # return error
    else:
        logger.error(f'failed to read database')
        details[0]['line'] = 'at exit'
        return render_template('error.html', details=details)


# +
# route(s): /ztf/<int:id>/csvhtml/, /sassy/<int:id>/csvhtml/
# -
# noinspection PyShadowingBuiltins
@app.route('/sassy/ztf/<int:id>/csvhtml/')
@app.route('/ztf/<int:id>/csvhtml/')
def ztf_get_csvhtml(id=0):
    logger.debug(f'route /sassy/ztf/{id}/csvhtml/ entry')

    # check input(s)
    details = [{'format': '<number>', 'line': '', 'name': 'id', 'route': f'/sassy/ztf/{id}',
                'type': 'int', 'url': f'{SASSY_APP_URL}/ztf/{id}/csvhtml/', 'value': f'{id}'}]
    if not isinstance(id, int) or id <= 0:
        logger.warning(f'input(s) are invalid')
        details[0]['line'] = 'at entry'
        return render_template('error.html', details=details)

    # get data
    alert = None
    try:
        alert = db_ztf.session.query(ZtfAlert).get(id)
    except Exception as _e:
        logger.error(f'alert not found, alert={alert}, error={_e}')
        details[0]['line'] = 'at db.session.query()'
        return render_template('error.html', details=details)
    else:
        logger.info(f'alert={alert} is OK, type={type(alert)}')

    # write file
    return alert.get_csv().to_html()


# +
# route(s): /ztf/<int:id>/csv/, /sassy/<int:id>/csv/
# -
# noinspection PyShadowingBuiltins
@app.route('/sassy/ztf/<int:id>/csv/')
@app.route('/ztf/<int:id>/csv/')
def ztf_get_csv(id=0):
    logger.debug(f'route /sassy/ztf/{id}/csv/ entry')

    # check input(s)
    details = [{'format': '<number>', 'line': '', 'name': 'id', 'route': f'/sassy/ztf/{id}',
                'type': 'int', 'url': f'{SASSY_APP_URL}/ztf/{id}/csv/', 'value': f'{id}'}]
    if not isinstance(id, int) or id <= 0:
        logger.warning(f'input(s) are invalid')
        details[0]['line'] = 'at entry'
        return render_template('error.html', details=details)

    # get data
    alert = None
    try:
        alert = db_ztf.session.query(ZtfAlert).get(id)
    except Exception as _e:
        logger.error(f'alert not found, alert={alert}, error={_e}')
        details[0]['line'] = 'at db.session.query()'
        return render_template('error.html', details=details)
    else:
        logger.info(f'alert={alert} is OK, type={type(alert)}')

    # write file
    _csv = alert.get_csv()
    _header = ['jd', 'isot', 'filter', 'magpsf', 'sigmapsf', 'diffmaglim']
    _of = f'/tmp/{id}.csv'
    try:
        _csv.to_csv(f'{_of}', index=False, columns=_header, header=_header)
    except Exception as _f:
        logger.error(f'alert={alert}, error={_e}')
        details[0]['line'] = 'at _csv.to_csv()'
        return render_template('error.html', details=details)

    # serve file
    if os.path.isfile(_of):
        logger.info(f'{_of} exists')
        return send_from_directory(os.path.dirname(_of), os.path.basename(_of), as_attachment=True)

    # return error
    logger.error(f'{_of} not found')
    details[0]['line'] = 'at exit'
    return render_template('error.html', details=details)


# +
# route(s): /ztf/files/<path:filename>, /sassy/ztf/files/<path:filename>
# -
@app.route('/sassy/ztf/files/<path:filename>')
@app.route('/ztf/files/<path:filename>')
def ztf_get_file(filename=''):
    logger.debug(f'route /sassy/ztf/files/{filename}/ entry')

    # record incoming IP
    forwarded_ips = request.headers.getlist('X-Forwarded-For')
    client_ip = forwarded_ips[0].split(',')[0] if len(forwarded_ips) >= 1 else ''
    logger.info('incoming request', extra={'tags': {'requesting_ip': client_ip, 'request_args': request.args}})

    # check input(s)
    details = [{'format': '<path>', 'line': '', 'name': 'filename', 'route': f'/ztf/files/{filename}',
                'type': 'path', 'url': f'{SASSY_APP_URL}/ztf/files/{filename}/', 'value': f'{filename}'}]
    if not isinstance(filename, str) or filename.strip() == '':
        logger.warning(f'input(s) are invalid')
        details[0]['line'] = 'at entry'
        return render_template('error.html', details=details)

    # return data
    for _d in SASSY_ZTF_AVRO.split(':'):
        _f = os.path.join(_d, filename)
        logger.info(f'_f={_f}')
        if os.path.isfile(_f):
            logger.info(f'{_f} exists')
            return send_from_directory(_d, filename, as_attachment=True)

    # return error
    logger.error(f'{filename} not found in {SASSY_ZTF_AVRO}')
    details[0]['line'] = 'at exit'
    return render_template('error.html', details=details)


# +
# route(s): /ztf/avros/<int:idate>/, /sassy/ztf/avros/<int:idate>/
# -
@app.route('/sassy/ztf/avros/<int:idate>/')
@app.route('/ztf/avros/<int:idate>/')
def ztf_list_avros(idate=0):
    logger.debug(f'route /sassy/ztf/avros/{idate}/ entry')

    # check input(s)
    details = [{'format': '<yyyymmdd>', 'line': '', 'name': 'idate', 'route': f'/sassy/ztf/avros/{idate}',
                'type': 'int', 'url': f'{SASSY_APP_URL}/ztf/avros/{idate}/', 'value': f'{idate}'}]
    if not isinstance(idate, int) or idate <= 0 or len(f'{idate}') != 8:
        logger.warning(f'input(s) are invalid')
        details[0]['line'] = 'at entry'
        return render_template('error.html', details=details)

    # parse input(s)
    _y, _m, _d = f'{idate}'[:4], f'{idate}'[4:6], f'{idate}'[6:]
    logger.info(f'y={_y} m={_m} d={_d}')

    # return data
    if int(_y) > 0 and (0 < int(_m) < 13) and (0 < int(_d) < 32):
        _files = []
        for _d in SASSY_ZTF_AVRO.split(':'):
            logger.info(f'_d={_d}')
            _f = os.path.join(_d, _y, _m, _d)
            logger.info(f'_f={_f}')
            for _glob in glob.glob(f'{_f}/*.avro'):
                if os.path.isfile(_glob):
                    _files.append(_glob)
        return jsonify(_files)

    # return error
    else:
        details[0]['line'] = 'at exit'
        return render_template('error.html', details=details)


# +
# route(s): /ztf/<int:id>/cutout/<stamp>/, /sassy/ztf/<int:id>/cutout/<stamp>/
# -
# noinspection PyShadowingBuiltins,PyBroadException
@app.route('/sassy/ztf/<int:id>/cutout/<stamp>/')
@app.route('/ztf/<int:id>/cutout/<stamp>/')
def ztf_alert_stamp(id=0, stamp=''):
    logger.debug(f'route /sassy/ztf/{id}/cutout/{stamp}/ entry')

    # why does this route get the following sample argument?
    #   ?r=0.9228713425306879

    # check input(s)
    details = [
        # integer id
        {'format': '<number>', 'line': '', 'name': 'id', 'route': f'/ztf/{id}/cutout/{stamp}',
         'type': 'int', 'url': f'{SASSY_APP_URL}/ztf/{id}/cutout/{stamp}', 'value': f'{id}'},
        # string cutout
        {'format': '<str>', 'line': '', 'name': 'stamp', 'route': f'/ztf/{id}/cutout/{stamp}',
         'type': 'str', 'url': f'{SASSY_APP_URL}/ztf/{id}/cutout/{stamp}', 'value': f'{stamp}'}
    ]
    if not isinstance(id, int) or id < 0 or not isinstance(stamp, str) or stamp.strip() == '' or \
            stamp.strip() not in ['Difference', 'Science', 'Template']:
        logger.warning(f'input(s) are invalid')
        details[0]['line'] = 'at entry'
        details[1]['line'] = 'at entry'
        return render_template('error.html', details=details)

    # get data
    alert = None
    try:
        alert = db_ztf.session.query(ZtfAlert).get(id)
    except Exception as _e:
        logger.error(f'alert={alert} not found, error={_e}')
        details[0]['line'] = 'at db.session.query()'
        details[1]['line'] = 'at db.session.query()'
        return render_template('error.html', details=details)
    logger.debug(f'alert={alert}')

    # return data
    if hasattr(alert, f'cutout{stamp}'):
        _sf = getattr(alert, f'cutout{stamp}')
        return send_file(
            io.BytesIO(_sf['stampData']),
            mimetype='image/fits',
            as_attachment=True,
            attachment_filename=_sf['fileName']
        )

    # return error
    else:
        details[0]['line'] = 'at exit'
        details[1]['line'] = 'at exit'
        return render_template('error.html', details=details)


# +
# route(s): /ztf/<int:id>/photometry/, /sassy/ztf/<int:id>/photometry/
# -
# noinspection PyShadowingBuiltins,PyBroadException
@app.route('/sassy/ztf/<int:id>/photometry/')
@app.route('/ztf/<int:id>/photometry/')
def ztf_photometry(id=0):
    logger.debug(f'route /sassy/ztf/{id}/photometry/ entry')

    # check input(s)
    details = [{'format': '<number>', 'line': '', 'name': 'id', 'route': f'/sassy/ztf/{id}',
                'type': 'int', 'url': f'{SASSY_APP_URL}/ztf/{id}/photometry/', 'value': f'{id}'}]
    if not isinstance(id, int) or id <= 0:
        logger.warning(f'input(s) are invalid')
        details[0]['line'] = 'at entry'
        return render_template('error.html', details=details)

    # get data
    alert = None
    try:
        alert = db_ztf.session.query(ZtfAlert).get(id)
    except Exception as _e:
        logger.error(f'alert not found, alert={alert}, error={_e}')
        details[0]['line'] = 'at db.session.query()'
        return render_template('error.html', details=details)
    else:
        logger.info(f'alert={alert} is OK, type={type(alert)}')

    # return
    return jsonify(alert.get_photometry())


# +
# route(s): /ztf/, /sassy/ztf/
# -
# noinspection PyBroadException
@app.route('/sassy/ztf/', methods=['GET', 'POST'])
@app.route('/ztf/', methods=['GET', 'POST'])
def ztf_alerts():
    logger.debug(f'route /sassy/ztf/ entry')

    # report where request is coming from
    forwarded_ips = request.headers.getlist('X-Forwarded-For')
    client_ip = forwarded_ips[0].split(',')[0] if len(forwarded_ips) >= 1 else ''
    logger.info('incoming request', extra={'tags': {'requesting_ip': client_ip, 'request_args': request.args}})
    page = request.args.get('page', 1, type=int)
    response = {}

    # set default(s)
    latest = None
    paginator = None

    logger.debug(f'requests.args={request.args}')

    # GET request
    if request.method == 'GET':

        # default to 1 month ago
        _jd = get_jd() - 30.0

        # query database
        query = db_ztf.session.query(ZtfAlert)
        query = ztf_filters(query, request.args)

        # get latest alert
        latest = db_ztf.session.query(ZtfAlert).order_by(ZtfAlert.jd.desc()).first()

        # paginate
        paginator = query.paginate(page, RESULTS_PER_PAGE, True)

        # set response dictionary
        response = {
            'total': paginator.total,
            'pages': paginator.pages,
            'has_next': paginator.has_next,
            'has_prev': paginator.has_prev,
            'results': ZtfAlert.serialize_list(paginator.items)
        }

    # POST request
    if request.method == 'POST':

        # get search criteria
        searches = request.get_json().get('queries')
        logger.debug(f'searches={searches}')

        # initialize output(s)
        search_results = []
        total = 0

        # iterate over searches
        for search_args in searches:

            # initialize result(s)
            search_result = {}

            # query database
            query = db_ztf.session.query(ZtfAlert)
            query = ztf_filters(query, search_args)

            # extract,transform and load (ETL) into result(s)
            search_result['query'] = search_args
            search_result['num_alerts'] = query.count()
            search_result['results'] = ZtfAlert.serialize_list(query.all())
            search_results.append(search_result)
            total += search_result['num_alerts']

        # set response dictionary
        response = {
            'total': total,
            'results': search_results
        }

    # return response in desired format
    if _request_wants_json() or request.method == 'POST':
        return jsonify(response)
    else:
        _args = request.args.copy()
        try:
            _args.pop('page')
        except:
            pass
        arg_str = urlencode(_args)
        return render_template('ztf.html', context=response, page=paginator.page, arg_str=arg_str, latest=latest,
                               url={'url': f'{SASSY_APP_URL}', 'page': 'ztf'})


# +
# route(s): /ztf/text/, /sassy/ztf/text/
# -
# noinspection PyShadowingBuiltins
@app.route('/sassy/ztf/text/')
@app.route('/ztf/text/')
def ztf_text():
    logger.debug(f'route /sassy/ztf/text/ entry')
    return render_template('ztf_text.html', text=ztf_get_text())


# +
# route(s): /ztf_q3c/, /sassy/ztf_q3c/
# -
@app.route('/sassy/ztf_q3c/')
@app.route('/ztf_q3c/')
def ztf_q3c():
    logger.debug(f'route /sassy/ztf_q3c/ entry')
    return render_template('ztf_q3c.html')


# +
# main()
# -
if __name__ == '__main__':
    app.run(host=os.getenv('SASSY_APP_HOST', '0.0.0.0'), port=int(os.getenv('SASSY_APP_PORT', 5000)),
            threaded=True, debug=False)
