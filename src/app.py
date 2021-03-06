#!/usr/bin/env python3


# +
# import(s)
# -
# Sam's MMT API
try:
    import mmtapi.mmtapi as mmtapi
except Exception as _i:
    print(f"Unable to import mmtapi, error={_i}")


# noinspection PyUnresolvedReferences
from src import *
from src.common import *
from src.utils.combine_pngs import *
from src.utils.utils import *
from src.utils.plot_tel_airmass import *
from src.utils.plot_tel_finder import *

# noinspection PyBroadException
try:
    from src.utils.sassy_bot import *
except:
    sassy_bot_read = None

from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from flask import send_file
from flask import send_from_directory
from urllib.parse import urlencode
from urllib.parse import parse_qsl

# noinspection PyUnresolvedReferences
from src.forms.Forms import AstronomicalRadialQueryForm
from src.forms.Forms import AstronomicalEllipticalQueryForm
from src.forms.Forms import DigitalRadialQueryForm
from src.forms.Forms import DigitalEllipticalQueryForm
from src.forms.Forms import MMTImagingForm
from src.forms.Forms import MMTLongslitForm
from src.forms.Forms import PsqlQueryForm
from src.forms.Forms import SexagisimalRadialQueryForm
from src.forms.Forms import SexagisimalEllipticalQueryForm
from src.forms.Forms import SassyBotForm

# noinspection PyUnresolvedReferences
from src.models.sassy_cron import SassyCron
from src.models.sassy_cron import db as db_sassy
from src.models.sassy_cron import sassy_cron_filters

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
logger.debug('SASSY_AIRMASS = {}'.format(SASSY_AIRMASS))
logger.debug('SASSY_FINDERS = {}'.format(SASSY_FINDERS))


# +
# initialize flask
# -
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'postgresql+psycopg2://{SASSY_DB_USER}:{SASSY_DB_PASS}@{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Steward Alerts For Science System!'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


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
    db_sassy.init_app(app)
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
# noinspection PyBroadException
@app.route('/sassy/cron/', methods=['GET', 'POST'])
@app.route('/cron/', methods=['GET', 'POST'])
def cron_records():
    logger.debug(f'route /sassy/cron/ entry')

    # report where request is coming from
    forwarded_ips = request.headers.getlist('X-Forwarded-For')
    client_ip = forwarded_ips[0].split(',')[0] if len(forwarded_ips) >= 1 else ''
    logger.info('incoming request', extra={'tags': {'requesting_ip': client_ip, 'request_args': request.args}})
    page = request.args.get('page', 1, type=int)

    # set default(s)
    zjd_min, zjd_max, iso_min, iso_max = math.nan, -math.nan, '', ''
    paginator = None
    latest = None
    response = {}
    _args = request.args.copy()
    if 'sort_order' not in _args:
        _args['sort_order'] = 'ascending'
    if 'sort_value' not in _args:
        _args['sort_value'] = 'zjd'

    # GET request
    if request.method == 'GET':

        # query database
        query = db_sassy.session.query(SassyCron)
        query = sassy_cron_filters(query, _args)

        # get latest alert
        latest = db_sassy.session.query(SassyCron).order_by(SassyCron.zjd.desc()).first()

        # paginate
        paginator = query.paginate(page, RESULTS_PER_PAGE, True)

        # set response dictionary
        response = {
            'total': paginator.total,
            'pages': paginator.pages,
            'has_next': paginator.has_next,
            'has_prev': paginator.has_prev,
            'results': SassyCron.serialize_list(paginator.items)
        }
        try:
            zjd_min = min([_k['zjd'] for _k in response['results']])
            zjd_max = max([_k['zjd'] for _k in response['results']])
            iso_min, iso_max = jd_to_isot(zjd_min), jd_to_isot(zjd_max)
        except:
            pass

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
            query = db_sassy.session.query(SassyCron)
            query = sassy_cron_filters(query, search_args)

            # extract, transform and load (ETL) into result(s)
            search_result['query'] = search_args
            search_result['num_alerts'] = query.count()
            search_result['results'] = SassyCron.serialize_list(query.all())
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
        return render_template('sassy_cron.html', context=response, page=paginator.page, arg_str=arg_str, latest=latest,
                               iso_min=iso_min, iso_max=iso_max, zjd_min=zjd_min, zjd_max=zjd_max,
                               url={'url': f'{SASSY_APP_URL}', 'page': 'sassy_cron'})


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
    logger.debug(f"route /sassy/gwgc/ _args={_args}")

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
        logger.debug(f'route /sassy/gwgc/ searchs={searchs}')

        # initialize output(s)
        search_results = []
        total = 0

        # iterate over searches
        for search_args in searches:

            # initialize result(s)
            search_result = {}

            # query database
            query = db_gwgc.session.query(GwgcRecord)
            logger.debug(f'route /sassy/gwgc/ search_args={search_args}')
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
# (hidden) function: mmt_get()
# -
def _mmt_get(_dbrec=None, _form=None, _obstype='imaging'):

    # check input(s)
    if _dbrec is None or _form is None or _obstype.strip().lower() not in ['imaging', 'longslit']:
        return

    # populate form depending on type
    if isinstance(_dbrec, SassyCron):
        _form.ra_hms.data = ra_to_hms(_dbrec.zra).strip()
        _form.dec_dms.data = dec_to_dms(_dbrec.zdec).strip()
        _form.filter_name.data = ZTF_FILTERS.get(_dbrec.zfid)[0]
        _form.magnitude.data = round((_dbrec.zmagap + _dbrec.zmagpsf) / 2.0, 3)
        _form.notes.data = f"{_dbrec.spng.split('.')[0].replace('_science', '')}: {_dbrec.altype}"
        if _obstype.strip().lower() == 'imaging':
            _form.zoid.data = f"i{_dbrec.zoid}"
        else:
            _form.zoid.data = f"s{_dbrec.zoid}"

    elif isinstance(_dbrec, TnsQ3cRecord):
        _ra_str = ra_to_hms(_dbrec.ra).replace('.', '').replace(':', '').replace(' ', '').strip()[:6]
        _dec_str = dec_to_dms(_dbrec.dec).replace('.', '').replace(':', '').replace(' ', '').replace('-', '').replace('+', '').strip()[:6]
        _form.ra_hms.data = ra_to_hms(_dbrec.ra).strip()
        _form.dec_dms.data = dec_to_dms(_dbrec.dec).strip()
        _form.filter_name.data = _dbrec.filter_name
        _form.magnitude.data = round(_dbrec.discovery_mag, 3)
        _form.zoid.data = f"{_dbrec.tns_name.replace(' ', '')}"
        if _obstype.strip().lower() == 'imaging':
            _form.notes.data = f"i{_dbrec.tns_name.replace(' ', '_')}_{_ra_str}_{_dec_str}"
        else:
            _form.notes.data = f"s{_dbrec.tns_name.replace(' ', '_')}_{_ra_str}_{_dec_str}"

    elif isinstance(_dbrec, dict):
        if not _dbrec or _dbrec == {}:
            pass
        elif all(_k in ['ra', 'dec', 'filter_name', 'magnitude', 'name'] for _k in _dbrec.keys()):
            _ra_str, _dec_str = '', ''
            if isinstance(_dbrec['ra'], float):
                _ra_str = ra_to_hms(_dbrec['ra']).replace('.', '').replace(':', '').replace(' ', '').strip()[:6]
                _form.ra_hms.data = ra_to_hms(_dbrec['ra']).strip()
            if isinstance(_dbrec['dec'], float):
                _dec_str = dec_to_dms(_dbrec['dec']).replace('.', '').replace(':', '').replace(' ', '').replace('-', '').replace('+', '').strip()[:6]
                _form.dec_dms.data = dec_to_dms(_dbrec['dec']).strip()
            _form.filter_name.data = _dbrec['filter_name']
            if isinstance(_dbrec['magnitude'], float):
                _form.magnitude.data = round(float(_dbrec['magnitude']), 3)
            else:
                _form.magnitude.data = -900.0
            _form.zoid.data = f"{_dbrec['name'].replace(' ', '_')}"
            if _obstype.strip().lower() == 'imaging':
                _form.notes.data = f"i{_dbrec['name'].replace(' ', '_')}_{_ra_str}_{_dec_str}"
            else:
                _form.notes.data = f"s{_dbrec['name'].replace(' ', '_')}_{_ra_str}_{_dec_str}"

    else:
        pass

    # common item(s)
    _form.epoch.data = 2000.0
    _form.token.data = ''
    _form.visits.data = 1
    if _obstype.strip().lower() == 'imaging':
        _form.exposuretime.data = 100.0
        _form.numexposures.data = 5
    else:
        _form.exposuretime.data = 900.0
        _form.numexposures.data = 2
        _form.central_lambda.data = 6500.0
        _form.grating.data = 270

    # return form
    return _form


# +
# (hidden) function: mmt_post()
# -
def _mmt_post(_dbrec=None, _form=None, _obstype='imaging'):

    # check input(s)
    if _dbrec is None or _form is None or _obstype.strip().lower() not in ['imaging', 'longslit']:
        return

    # get RA, Dec
    _ra = f"{_form.ra_hms.data.strip()}"
    _dec = f"{_form.dec_dms.data.strip()}".replace("+", "")

    # get path(s)
    _mmt, _mmt_loc = None, None
    if isinstance(_dbrec, SassyCron):
        _mmt = f"{_dbrec.spng.split('.')[0].replace('_science', '_mmt')}.jpg"

    elif isinstance(_dbrec, TnsQ3cRecord):
        _ra_str = ra_to_hms(_dbrec.ra).replace('.', '').replace(':', '').replace(' ', '').strip()[:6]
        _dec_str = dec_to_dms(_dbrec.dec).replace('.', '').replace(':', '').replace(' ', '').replace('-', '').replace('+', '').strip()[:6]
        _oid = f"{_dbrec.tns_name.replace(' ', '_')}"
        _mmt = f"{_oid}_{_ra_str}_{_dec_str}_mmt.jpg"

    elif isinstance(_dbrec, dict):
        if not _dbrec or _dbrec == {}:
            pass
        elif all(_k in ['ra', 'dec', 'name'] for _k in _dbrec.keys()):
            _ra_str = ra_to_hms(_dbrec['ra']).replace('.', '').replace(':', '').replace(' ', '').strip()[:6]
            _dec_str = dec_to_dms(_dbrec['dec']).replace('.', '').replace(':', '').replace(' ', '').replace('-', '').replace('+', '').strip()[:6]
            _oid = f"{_dbrec['name']}"
            _mmt = f"{_oid}_{_ra_str}_{_dec_str}_mmt.jpg"

    else:
        pass

    _mmt_loc = f"{SASSY_FINDERS}/{_mmt}"
    logger.debug(f'_mmt={_mmt}, _mmt_loc={_mmt_loc}')

    # return payload
    if _obstype.strip().lower() == 'imaging':
        return {
            "dec": _dec, 
            "epoch": float(_form.epoch.data), 
            "exposuretime": float(_form.exposuretime.data), 
            "filter": f"{_form.filter_name.data.strip()}", 
            "findingchartfilename": os.path.basename(_mmt_loc) if _mmt_loc is not None else "",
            "instrumentid": 16,
            "magnitude": float(_form.magnitude.data), 
            "maskid": 110, 
            "notes": f"{_form.notes.data.strip()}",
            "numberexposures": int(_form.numexposures.data), 
            "objectid": f"{_form.zoid.data.strip()}".replace("_", ""),
            "observationtype": "imaging", 
            "priority": 1, 
            "ra": _ra,
            "token": f"{_form.token.data.strip()}", 
            "targetofopportunity": 1, 
            "visits": int(_form.visits.data)
        }
    else:
        return {
            "centralwavelength": float(_form.central_lambda.data),
            "dec": _dec, 
            "epoch": float(_form.epoch.data),
            "exposuretime": float(_form.exposuretime.data), 
            "filter": f"{_form.filter_name.data.strip()}",
            "findingchartfilename": os.path.basename(_mmt_loc) if _mmt_loc is not None else "",
            "grating": f"{_form.grating.data.strip()}", 
            "instrumentid": 16,
            "magnitude": float(_form.magnitude.data), 
            "maskid": {'Longslit0_75': 113, 'Longslit1': 111, 'Longslit1_25': 131, 'Longslit1_5': 114, 'Longslit5': 112}.get(f"{_form.slitwidth.data.strip()}", 111),
            "notes": f"{_form.notes.data.strip()}",
            "numberexposures": int(_form.numexposures.data), 
            "objectid": f"{_form.zoid.data.strip()}".replace("_", ""),
            "observationtype": "longslit", 
            "priority": 1, 
            "ra": _ra,
            "slitwidth": f"{_form.slitwidth.data.strip()}",
            "token": f"{_form.token.data.strip()}", 
            "targetofopportunity": 1, 
            "visits": int(_form.visits.data)
        }


# +
# function: _mmt_create_finder()
# -
def _mmt_create_finder(_dbrec=None):

    # check input(s)
    if _dbrec is None:
        return

    # get base name(s)
    _dif, _sci, _tmp, _fnd, _air, _mmt_jpg, _mmt_png, _oid = '', '', '', '', '', '', '', ''
    if isinstance(_dbrec, SassyCron):
        _dif = f"{_dbrec.dpng}"
        _sci = f"{_dbrec.spng}"
        _tmp = f"{_dbrec.tpng}"
        _fnd = f"{_dbrec.spng.split('.')[0].replace('_science', '_finder')}.png"
        _air = f"{_dbrec.spng.split('.')[0].replace('_science', '_airmass')}.png"
        _oid = f"{_dbrec.zoid}"
        _mmt_jpg = f"{_dbrec.spng.split('.')[0].replace('_science', '_mmt')}.jpg"
        _mmt_png = f"{_dbrec.spng.split('.')[0].replace('_science', '_mmt')}.png"

    elif isinstance(_dbrec, TnsQ3cRecord):
        _ra_str = ra_to_hms(_dbrec.ra).replace('.', '').replace(':', '').replace(' ', '').strip()[:6]
        _dec_str = dec_to_dms(_dbrec.dec).replace('.', '').replace(':', '').replace(' ', '').replace('-', '').replace('+', '').strip()[:6]
        _oid = f"{_dbrec.tns_name.replace(' ', '_')}"
        _dif = f"{_oid}_{_ra_str}_{_dec_str}_difference.png"
        _sci = f"{_oid}_{_ra_str}_{_dec_str}_science.png"
        _tmp = f"{_oid}_{_ra_str}_{_dec_str}_template.png"
        _fnd = f"{_oid}_{_ra_str}_{_dec_str}_finder.png"
        _air = f"{_oid}_{_ra_str}_{_dec_str}_airmass.png"
        _mmt_jpg = f"{_oid}_{_ra_str}_{_dec_str}_mmt.jpg"
        _mmt_png = f"{_oid}_{_ra_str}_{_dec_str}_mmt.png"

    elif isinstance(_dbrec, dict):
        _ra_str = ra_to_hms(_dbrec['ra']).replace('.', '').replace(':', '').replace(' ', '').strip()[:6]
        _dec_str = dec_to_dms(_dbrec['dec']).replace('.', '').replace(':', '').replace(' ', '').replace('-', '').replace('+', '').strip()[:6]
        _oid = f"{_dbrec['name']}"
        _dif = f"{_oid}_{_ra_str}_{_dec_str}_difference.png"
        _sci = f"{_oid}_{_ra_str}_{_dec_str}_science.png"
        _tmp = f"{_oid}_{_ra_str}_{_dec_str}_template.png"
        _fnd = f"{_oid}_{_ra_str}_{_dec_str}_finder.png"
        _air = f"{_oid}_{_ra_str}_{_dec_str}_airmass.png"
        _mmt_jpg = f"{_oid}_{_ra_str}_{_dec_str}_mmt.jpg"
        _mmt_png = f"{_oid}_{_ra_str}_{_dec_str}_mmt.png"

    else:
        pass

    logger.debug(f'_dif={_dif}, _sci={_sci}, _tmp={_tmp}, _oid={_oid}')
    logger.debug(f'_fnd={_fnd}, _air={_air}, _mmt_png={_mmt_png}, _mmt_jpg={_mmt_jpg}')

    # get full path(s)
    _dif_loc = f"{app.static_folder}/img/{_dif}"
    _sci_loc = f"{app.static_folder}/img/{_sci}"
    _tmp_loc = f"{app.static_folder}/img/{_tmp}"
    _fnd_loc = f"{SASSY_FINDERS}/{_fnd}"
    _air_loc = f"{SASSY_AIRMASS}/{_air}"
    _mmt_jpg_loc = f"{SASSY_FINDERS}/{_mmt_jpg}"
    _mmt_png_loc = f"{SASSY_FINDERS}/{_mmt_png}"

    logger.debug(f'_dif_loc={_dif_loc}, _sci_loc={_sci_loc}, _tmp_loc={_tmp_loc}')
    logger.debug(f'_fnd_loc={_fnd_loc}, _air_loc={_air_loc}')
    logger.debug(f'_mmt_jpg_loc={_mmt_jpg_loc}, _mmt_png_loc={_mmt_png_loc}')

    # get airmass
    if _air_loc is not None and not os.path.exists(f"{_air_loc}"):
        if isinstance(_dbrec, SassyCron):
            _air_loc = plot_tel_airmass(_ra=_dbrec.zra, _dec=_dbrec.zdec, _oid=_oid, _tel='mmt', _img=_air_loc, _log=logger)
        elif isinstance(_dbrec, TnsQ3cRecord):
            _air_loc = plot_tel_airmass(_ra=_dbrec.ra, _dec=_dbrec.dec, _oid=_oid, _tel='mmt', _img=_air_loc, _log=logger)
        elif isinstance(_dbrec, dict):
            _air_loc = plot_tel_airmass(_ra=ra_to_decimal(_dbrec['ra']), _dec=dec_to_decimal(_dbrec['dec']), _oid=_oid, _tel='mmt', _img=_air_loc, _log=logger)
    logger.debug(f'_air_loc={_air_loc}')

    # get finder
    if _fnd_loc is not None and not os.path.exists(f"{_fnd_loc}"):
        if isinstance(_dbrec, SassyCron):
            _fnd_loc = plot_tel_finder(_ra=_dbrec.zra, _dec=_dbrec.zdec, _oid=_oid, _img=_fnd_loc, _log=logger)
        elif isinstance(_dbrec, TnsQ3cRecord):
            _fnd_loc = plot_tel_finder(_ra=_dbrec.ra, _dec=_dbrec.dec, _oid=_oid, _img=_fnd_loc, _log=logger)
        elif isinstance(_dbrec, dict):
            _fnd_loc = plot_tel_finder(_ra=_dbrec['ra'], _dec=_dbrec['dec'], _oid=_oid, _img=_fnd_loc, _log=logger)
    logger.debug(f'_fnd_loc={_fnd_loc}')

    # combine image(s)
    _images = []
    logger.debug(f'_fnd_loc={_fnd_loc}, _air_loc={_air_loc}, _images={_images}')
    if _fnd_loc is not None and os.path.exists(f"{_fnd_loc}"):
        _images.append(f"{_fnd_loc}")
    if _air_loc is not None and os.path.exists(f"{_air_loc}"):
        _images.append(f"{_air_loc}")
    if _dif_loc is not None and os.path.exists(f"{_dif_loc}"):
        _images.append(f"{_dif_loc}")
    if _sci_loc is not None and os.path.exists(f"{_sci_loc}"):
        _images.append(f"{_sci_loc}")
    if _tmp_loc is not None and os.path.exists(f"{_tmp_loc}"):
        _images.append(f"{_tmp_loc}")
    logger.info(f"_images={_images}")

    if len(_images) == 0:
        if _air_loc is not None and os.path.exists(_air_loc):
            _mmt_png_loc = f"{_air_loc}"
        elif _fnd_loc is not None and os.path.exists(_fnd_loc):
            _mmt_png_loc = f"{_fnd_loc}"
        else:
            _mmt_png_loc = f"${SASSY_FINDERS}/KeepCalm.png"
    elif len(_images) == 1:
        if os.path.exists(_images[0]):
            _mmt_png_loc = _images[0]
        else:
            _mmt_png_loc = f"${SASSY_FINDERS}/KeepCalm.png"
    else:
        try:
            _mmt_png_loc = combine_pngs(_files=_images, _output=_mmt_png_loc, _log=logger)
        except Exception as _eo1:
            _mmt_png_loc = f"${SASSY_FINDERS}/KeepCalm.png"
            logger.error(f'Failed to combine image(s), error={_eo1}')

    # convert final image to jpg
    logger.debug(f'_mmt_jpg_loc={_mmt_jpg_loc}, _mmt_png_loc={_mmt_png_loc}')
    _mmt_jpg_loc = png_to_jpg(_png=f'{_mmt_png_loc}')
    logger.debug(f'_mmt_jpg_loc={_mmt_jpg_loc}, _mmt_png_loc={_mmt_png_loc}')

    # return path
    if _mmt_jpg_loc is not None and os.path.exists(_mmt_jpg_loc):
        return _mmt_jpg_loc
    elif _mmt_png_loc is not None and os.path.exists(_mmt_png_loc):
        return _mmt_png_loc
    else:
        return f"{SASSY_FINDERS}/KeepCalm.jpg"


# +
# route(s): /mmt/imaging/<zoid>, /sassy/mmt/imaging/<zoid>
# -
@app.route('/sassy/mmt/imaging/<zoid>', methods=['GET', 'POST'])
@app.route('/mmt/imaging/<zoid>', methods=['GET', 'POST'])
def mmt_imaging(zoid=''):
    logger.debug(f'route /sassy/mmt/imaging/{zoid} entry')

    # get observation request
    _cronrec, _mmt = None, None
    if zoid.upper().startswith('ZTF'):
        _cronrec = SassyCron.query.filter_by(zoid=zoid).first_or_404()
        _mmt = _mmt_create_finder(_dbrec=_cronrec)
    elif zoid.upper().startswith('TNS') or zoid.upper().startswith('AT') or zoid.upper().startswith('SN'):
        _tns_name = str(zoid).replace("_", " ")
        _cronrec = TnsQ3cRecord.query.filter_by(tns_name=_tns_name).first_or_404()
        _mmt = _mmt_create_finder(_dbrec=_cronrec)
    else:
        _cronrec = dict(parse_qsl(zoid))
        _mmt = None
    logger.debug(f'route /sassy/mmt/imaging/{zoid} _mmt={_mmt}, _cronrec={repr(_cronrec)}')

    # form
    form = MMTImagingForm()

    # GET method
    if request.method == 'GET':
        _form = _mmt_get(_dbrec=_cronrec, _form=form, _obstype='imaging')
        return render_template('mmt_imaging.html', form=_form, record=_cronrec, img=_mmt)

    # validate form (POST request)
    if form.validate_on_submit():
        _payload = _mmt_post(_dbrec=_cronrec, _form=form, _obstype='imaging')
        logger.info(f'route /sassy/mmt/imaging/{zoid} _payload={_payload}')
        if zoid.upper().startswith('ZTF'):
            pass
        elif zoid.upper().startswith('TNS') or zoid.upper().startswith('AT') or zoid.upper().startswith('SN'):
            pass
        else:
            _mmt = _mmt_create_finder(_dbrec={**_payload, **{'name': _payload['objectid']}})
            logger.info(f'route /sassy/mmt/imaging/{zoid} _mmt={_mmt}')
            _payload['findingchartfilename'] = os.path.basename(_mmt) if _mmt is not None else "KeepCalm.png"
        return render_template('mmt_request.html', url={'url': ''}, img=_mmt, payload=_payload)

    # return for GET
    return render_template('mmt_imaging.html', form=form)


# +
# route(s): /mmt/longslit/<zoid>, /sassy/mmt/longslit/<zoid>
# -
@app.route('/sassy/mmt/longslit/<zoid>', methods=['GET', 'POST'])
@app.route('/mmt/longslit/<zoid>', methods=['GET', 'POST'])
def mmt_longslit(zoid=''):
    logger.debug(f'route /sassy/mmt/longslit/{zoid} entry')

    # get observation request and image
    _cronrec, _mmt = None, None
    if zoid.upper().startswith('ZTF'):
        _cronrec = SassyCron.query.filter_by(zoid=zoid).first_or_404()
        _mmt = _mmt_create_finder(_dbrec=_cronrec)
    elif zoid.upper().startswith('TNS') or zoid.upper().startswith('AT') or zoid.upper().startswith('SN'):
        _tns_name = str(zoid).replace("_", " ")
        _cronrec = TnsQ3cRecord.query.filter_by(tns_name=_tns_name).first_or_404()
        _mmt = _mmt_create_finder(_dbrec=_cronrec)
    else:
        _cronrec = dict(parse_qsl(zoid))
        _mmt = None
    logger.debug(f'route /sassy/mmt/longslit/{zoid} _mmt={_mmt}, _cronrec={repr(_cronrec)}')

    # form
    form = MMTLongslitForm()

    # GET method
    if request.method == 'GET':
        _form = _mmt_get(_dbrec=_cronrec, _form=form, _obstype='longslit')
        return render_template('mmt_longslit.html', form=_form, record=_cronrec, img=os.path.basename(_mmt))

    # validate form (POST request)
    if form.validate_on_submit():
        _payload = _mmt_post(_dbrec=_cronrec, _form=form, _obstype='longslit')
        logger.info(f'route /sassy/mmt/longslit/{zoid} _payload={_payload}')
        if zoid.upper().startswith('ZTF'):
            pass
        elif zoid.upper().startswith('TNS') or zoid.upper().startswith('AT') or zoid.upper().startswith('SN'):
            pass
        else:
            _mmt = _mmt_create_finder(_dbrec={**_payload, **{'name': _payload['objectid']}})
            logger.info(f'route /sassy/mmt/longslit/{zoid} _mmt={_mmt}')
            _payload['findingchartfilename'] = os.path.basename(_mmt) if _mmt is not None else "KeepCalm.png"
        return render_template('mmt_request.html', url={'url': ''}, img=os.path.basename(_mmt), payload=_payload)

    # return for GET
    return render_template('mmt_longslit.html', form=form)


# +
# route(s): /mmt/request/, /sassy/mmt/request/
# -
# noinspection PyBroadException
@app.route('/sassy/mmt/request/', methods=['GET'])
@app.route('/mmt/request/', methods=['GET'])
def mmt_request():
    logger.debug(f'route /sassy/mmt/request/ entry')

    # get payload
    _payload = request.args.get('payload', None)
    if logger:
        logger.debug(f"_payload={_payload}, type(_payload)={type(_payload)}")

    # convert payload from string to dictionary
    try:
        _payload = json.loads(_payload.replace("'", '"'))
    except:
        _payload = None
    if logger:
        logger.debug(f"_payload={_payload}, type(_payload)={type(_payload)}")

    # return error if we cannot parse it
    if _payload is None or not isinstance(_payload, dict):
        if logger:
            logger.error(f"_payload={_payload}, type(_payload)={type(_payload)}")
        details = [{'format': '<dict>', 'line': '', 'name': 'payload', 'route': f'/sassy/mmt/request/?{_payload}',
                    'type': 'dict', 'url': f'{SASSY_APP_URL}/mmt/request/?{_payload}/', 'value': f'{_payload}'}]
        return render_template('error.html', details=details)

    # create request
    _target = None
    _token = _payload['token']
    if logger:
        logger.debug(f"creating MMT target, _target={_target}")
    try:
        _target = mmtapi.Target(token=_token, verbose=True, payload=_payload)
    except Exception as _ec:
        if logger:
            logger.error(f"failed to create MMT target, _target={_target}, error={_ec}")
        details = [{'format': '<dict>', 'line': '', 'name': 'payload', 'route': f'/sassy/mmt/request/?{_payload}',
                    'type': 'dict', 'url': f'{SASSY_APP_URL}/mmt/request/?{_payload}/', 'value': f'{_ec}'}]
        return render_template('error.html', details=details)
    else:
        if logger:
            logger.debug(f"created MMT target, _target={_target}")
            logger.debug(f"_target.__dict__={_target.__dict__}")

    # post request
    _json = {}
    if logger:
        logger.debug(f"posting MMT target, _target={_target}")
    try:
        _target.post()
    except Exception as _ep:
        if logger:
            logger.error(f"failed to post MMT target, _target={_target}, error={_ep}")
        details = [{'format': '<dict>', 'line': '', 'name': 'payload', 'route': f'/sassy/mmt/request/?{_payload}',
                    'type': 'dict', 'url': f'{SASSY_APP_URL}/mmt/request/?{_payload}/', 'value': f'{_ep}'}]
        return render_template('error.html', details=details)
    else:
        if logger:
            logger.debug(f"posted MMT target, _target={_target}")
            logger.debug(f"_target.__dict__={_target.__dict__}")
        _status = int(_target.__dict__['request'].status_code)
        if _status == 200:
            _json = json.loads(_target.__dict__['request'].text)
            if logger:
                logger.debug(f"posted MMT target reponse OK, _status={_status}, _json={_json}")

    # upload finder
    _finder_path = f"{SASSY_FINDERS}/{_payload['findingchartfilename']}"
    if logger:
        logger.debug(f"uploading MMT finder, _finder_path={_finder_path}")
    try:
        _target.upload_finder(finder_path=f"{_finder_path}")
    except Exception as _eu:
        if logger:
            logger.error(f"failed to upload MMT finder, _finder_path={_finder_path}, error={_eu}")
        details = [{'format': '<dict>', 'line': '', 'name': 'payload', 'route': f'/sassy/mmt/request/?{_payload}',
                    'type': 'dict', 'url': f'{SASSY_APP_URL}/mmt/request/?{_payload}/', 'value': f'{_eu}'}]
        return render_template('error.html', details=details)
    else:
        if logger:
            logger.debug(f"uploaded MMT finder, _finder_path={_finder_path}")
            logger.debug(f"_target.__dict__={_target.__dict__}")

    # check response
    _status = int(_target.__dict__['request'].status_code)
    if _status == 200:
        if logger:
            logger.debug(f"MMT request reponse OK, _status={_status}")
        _json = json.loads(_target.__dict__['request'].text)
        _targetid = _json['id']
        return render_template('mmt_request_ok.html', targetid=_targetid, obstype=f"{_payload['observationtype']}")
    else:
        if logger:
            logger.error(f"MMT request reponse NOT OK, _status={_status}")
        return render_template('mmt_request_notok.html', status=_status, obstype=f"{_payload['observationtype']}")


# +
# route(s): /plot_airmass/<img>, /sassy/plot_airmass/<img>
# -
@app.route('/sassy/plot_airmass/<img>', methods=['GET'])
@app.route('/plot_airmass/<img>', methods=['GET'])
def plot_airmass(img=''):
    logger.debug(f'route /sassy/plot_airmass/{img} entry')

    # return
    if os.path.exists(f"{SASSY_AIRMASS}/{img}"):
        return send_from_directory(f"{SASSY_AIRMASS}", img, as_attachment=False)
    else:
        _airmass = f"{SASSY_AIRMASS}/{img}"
        logger.debug(f'img={img}, _ra={_ra}, _dec={_dec}, _oid={_oid}, _tel={_tel}, _airmass={_airmass}')
        _ra = request.args.get('ra', math.nan)
        _dec = request.args.get('dec', math.nan)
        _oid = request.args.get('oid', get_hash())
        _tel = request.args.get('tel', 'mmt')
        _airmass = plot_tel_airmass(_ra=float(_ra), _dec=float(_dec), _oid=_oid, _tel=_tel, _img=_airmass, _log=logger)
        return send_from_directory(f"{SASSY_AIRMASS}", os.path.basename(_airmass), as_attachment=False)


# +
# route(s): /plot_finder/<img>, /sassy/plot_finder/<img>
# -
@app.route('/sassy/plot_finder/<img>', methods=['GET'])
@app.route('/plot_finder/<img>', methods=['GET'])
def plot_finder(img=''):
    logger.debug(f'route /sassy/plot_finder/{img} entry')

    # return
    if os.path.exists(f"{SASSY_FINDERS}/{img}"):
        return send_from_directory(f"{SASSY_FINDERS}", img, as_attachment=False)
    else:
        _finder = f"{SASSY_FINDERS}/{img}"
        logger.debug(f'img={img}, _ra={_ra}, _dec={_dec}, _oid={_oid}, _tel={_tel}, _finder={_finder}')
        _ra = request.args.get('ra', math.nan)
        _dec = request.args.get('dec', math.nan)
        _oid = request.args.get('oid', get_hash())
        _finder = plot_tel_finder(_ra=float(_ra), _dec=float(_dec), _oid=_oid, _img=_finder, _log=logger)
        return send_from_directory(f"{SASSY_FINDERS}", os.path.basename(_finder), as_attachment=False)


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
# route(s): /finder/<img>, /sassy/finder/<img>
# -
@app.route('/sassy/finder/<img>', methods=['GET'])
@app.route('/finder/<img>', methods=['GET'])
def show_finder(img=''):
    logger.debug(f'route /sassy/finder/{img} entry')
    img = img if '/' not in img else os.path.basename(img)
    return send_from_directory(f"{SASSY_FINDERS}", img, as_attachment=False)


# +
# route(s): /image/<img>, /sassy/image/<img>
# -
@app.route('/sassy/image/<img>', methods=['GET'])
@app.route('/image/<img>', methods=['GET'])
def show_image(img=''):
    logger.debug(f'route /sassy/image/{img} entry')

    # return
    _finder = f"{app.static_folder}/img/{img}"
    if os.path.exists(_finder):
        return render_template('show_image.html', img=img)
    else:
        return render_template('show_image.html', img='')


# +
# route(s): /sassy_cron/<oid>, /sassy/sassy_cron/<oid>
# -
@app.route('/sassy_cron/<oid>', methods=['GET'])
@app.route('/sassy_cron/<oid>', methods=['GET'])
def sassy_cron_page(oid=''):
    logger.debug(f'route /sassy_cron/{oid} entry')
    logger.debug(f'ahahadsfjk;ahsdfa')
    _cronrec = SassyCron.query.filter_by(zoid=oid).first_or_404()
    filter_name = ZTF_FILTERS.get(_cronrec.zfid)[0]
    ra_hms = ra_to_hms(_cronrec.zra).strip()
    dec_dms = dec_to_dms(_cronrec.zdec).strip()

    tns_info = {
            'available':_cronrec.alias is not None,
            'alias':_cronrec.alias,
            'discovery_date':_cronrec.discovery_date,
            'discovery_mag':_cronrec.discovery_mag,
            'discovery_inst':_cronrec.discovery_instrument,
            'source_group':_cronrec.source_group,
            'tns_link':_cronrec.tns_link,
            'host':_cronrec.host,
            'host_z':_cronrec.host_z,
            }

    ztf_info = {
            'oid':oid,
            'filter':filter_name,
            'ra_hms':ra_hms,
            'dec_dms':dec_dms,
            'jd':round(_cronrec.zjd,3),
            'magap':round(_cronrec.zmagap,2),
            'magpsf':round(_cronrec.zmagpsf,2),
            'magdiff':round(_cronrec.zmagdiff,2)
            }

    alerce_info = {
            'available':_cronrec.aetype is not None,
            'aetype':_cronrec.aetype,
            'altype':_cronrec.altype,
            'aeprob':_cronrec.aeprob,
            'alprob':_cronrec.alprob,
            'dpng':_cronrec.dpng,
            'spng':_cronrec.spng,
            'tpng':_cronrec.tpng,
            }
    
    glade_info = {
            'available':_cronrec.gid is not None,
            'id':_cronrec.gid,
            'distance': round(_cronrec.gdist, 3),
            'redshift': round(_cronrec.gz, 3),
            }


    payload = {
            'ztf':ztf_info,
            'tns':tns_info,
            'alerce':alerce_info,
            'glade':glade_info
            }

    logger.debug('{}'.format(payload))

    return render_template('sassy_cron_page.html', ztf=ztf_info, tns=tns_info, alerce=alerce_info, glade=glade_info)


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
        logger.error(f'alert={alert}, error={_f}')
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
# route(s): /ztf/<int:id>/non_detections/, /sassy/ztf/<int:id>/non_detections/
# -
# noinspection PyShadowingBuiltins,PyBroadException
@app.route('/sassy/ztf/<int:id>/non_detections/')
@app.route('/ztf/<int:id>/non_detections/')
def ztf_non_detections(id=0):
    logger.debug(f'route /sassy/ztf/{id}/non_detections/ entry')

    # check input(s)
    details = [{'format': '<number>', 'line': '', 'name': 'id', 'route': f'/sassy/ztf/{id}',
                'type': 'int', 'url': f'{SASSY_APP_URL}/ztf/{id}/non_detections/', 'value': f'{id}'}]
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
    _non_det = alert.get_non_detections()
    _non_det_dict = {}
    for _x, _y in enumerate(_non_det):
        _non_det_dict[f"{_x}"] = _y
    return jsonify(_non_det_dict)


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


#@app.after_request
#def add_header(response):
#    """
#    Add headers to both force latest IE rendering engine or Chrome Frame,
#    and also to cache the rendered page for 10 minutes.
#    """
#    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
#    response.headers['Cache-Control'] = 'public, max-age=0'
#    return response


# +
# main()
# -
if __name__ == '__main__':
    app.run(host=os.getenv('SASSY_APP_HOST', '0.0.0.0'), port=int(os.getenv('SASSY_APP_PORT', 5000)),
            threaded=True, debug=False)
