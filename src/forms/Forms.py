#!/usr/bin/env python3


# +
# import(s)
# -
from astropy.time import Time
from datetime import datetime
from datetime import timedelta
from flask_wtf import FlaskForm
from wtforms import FloatField
from wtforms import IntegerField
from wtforms import SelectField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import NumberRange
from wtforms.validators import Regexp

import re
import math


# +
# function(s)
# -
def forms_get_iso(offset=0):
    return (datetime.now() + timedelta(days=offset)).isoformat()


# noinspection PyBroadException
def forms_iso_to_jd(_iso=''):
    try:
        return float(Time(_iso).mjd)+2400000.5
    except Exception:
        return float(math.nan)


# noinspection PyBroadException
def forms_jd_to_iso(_jd=0.0):
    try:
        return Time(_jd, format='jd', precision=6).isot
    except Exception:
        return None


# +
# constant(s)
# -
ASTRO_ISO = forms_get_iso()
ASTRO_JD = forms_iso_to_jd(ASTRO_ISO)
BEGIN_JD = ASTRO_JD - 1.0
BEGIN_ISO = forms_jd_to_iso(BEGIN_JD)
END_JD = ASTRO_JD
END_ISO = forms_jd_to_iso(END_JD)
DATE_RULE = re.compile("\d{4}-\d{2}-\d{2}[ T]?\d{2}:\d{2}:\d")
DEFAULT_COMMAND = 'SELECT * FROM glade_q3c WHERE q3c_radial_query(ra, dec, 23.5, 29.2, 5.0);'
CATALOGS = [('Glade_q3c', 'Glade_q3c'), ('Gwgc_q3c', 'Gwgc_q3c'), ('Ligo_q3c', 'Ligo_q3c'), ('Tns_q3c', 'Tns_q3c')]
REGEXP_DEC = re.compile("[+-]?[0-9]{2}:[0-9]{2}:[0-9]{2}")
REGEXP_RA = re.compile("[0-9]{2}:[0-9]{2}:[0-9]{2}")

MMT_IMAGING_FILTERS = [('g', 'g'), ('r', 'r'), ('i', 'i'), ('z', 'z')]
MMT_LONGSLIT_FILTERS = [('LP3800', 'LP3800'), ('LP3500', 'LP3500')]
MMT_LONGSLIT_WIDTHS = [('Longslit1', 'Longslit1'), ('Longslit0_75', 'Longslit0_75'),
                      ('Longslit1_25', 'Longslit1_25'), ('Longslit1_5', 'Longslit1_5'), ('Longslit5', 'Longslit5')]
MMT_LONGSLIT_GRATINGS = [('270', '270'), ('600', '600'), ('1000', '1000')]


# +
# class: PsqlQueryForm(), inherits from FlaskForm
# -
class PsqlQueryForm(FlaskForm):

    # fields
    sql_query = StringField('SQL Query', default=DEFAULT_COMMAND, validators=[DataRequired()])

    # submit
    submit = SubmitField('Submit')


# +
# class: CustomQueryForm(), inherits from FlaskForm
# -
class CustomQueryForm(FlaskForm):

    # fields
    ra_hms = StringField('RA', default='13:30:00.0', validators=[
        DataRequired(), Regexp(regex=REGEXP_RA, flags=re.IGNORECASE, message='RA format is HH:MM:SS.S')])
    dec_dms = StringField('Dec', default='47:11:00.0', validators=[
        DataRequired(), Regexp(regex=REGEXP_DEC, flags=re.IGNORECASE, message='Dec format is +/-dd:mm:ss.s')])
    radius = FloatField('Cone Radius', default=5.0, validators=[
        DataRequired(), NumberRange(min=0.0, max=180.0, message=f'0.0 < cone radius < 180.0')])
    catalog = SelectField('Catalog', choices=CATALOGS, default=CATALOGS[0][0], validators=[DataRequired()])

    # submit
    submit = SubmitField('Submit')


# +
# class: AstronomicalRadialQueryForm(), inherits from FlaskForm
# -
class AstronomicalRadialQueryForm(FlaskForm):

    # fields
    obj_name = StringField('Name', default='M51', validators=[DataRequired()])
    radius = FloatField('Radius', default=5.0, validators=[
        DataRequired(), NumberRange(min=0.0, max=180.0, message=f'0.0 < cone radius < 180.0')])
    catalog = SelectField('Catalog', choices=CATALOGS, default=CATALOGS[0][0], validators=[DataRequired()])

    # submit
    submit = SubmitField('Submit')


# +
# class: DigitalRadialQueryForm(), inherits from FlaskForm
# -
class DigitalRadialQueryForm(FlaskForm):

    # fields
    ra = FloatField('RA', default=202.4696, validators=[
        DataRequired(), NumberRange(min=0.0, max=360.0, message=f'0.0 < RA < 360.0')])
    dec = FloatField('Dec', default=47.1953, validators=[
        DataRequired(), NumberRange(min=-90.0, max=90.0, message=f'-90.0 < Dec < 90.0')])
    radius = FloatField('Radius', default=5.0, validators=[
        DataRequired(), NumberRange(min=0.0, max=180.0, message=f'0.0 < cone radius < 180.0')])
    catalog = SelectField('Catalog', choices=CATALOGS, default=CATALOGS[0][0], validators=[DataRequired()])

    # submit
    submit = SubmitField('Submit')


# +
# class: SexagisimalRadialQueryForm(), inherits from FlaskForm
# -
class SexagisimalRadialQueryForm(FlaskForm):

    # fields
    ra = StringField('RA', default='13:30:00.0', validators=[
        DataRequired(), Regexp(regex=REGEXP_RA, flags=re.IGNORECASE, message='RA format is HH:MM:SS.S')])
    dec = StringField('Dec', default='47:11:00.0', validators=[
        DataRequired(), Regexp(regex=REGEXP_DEC, flags=re.IGNORECASE, message='Dec format is +/-dd:mm:ss.s')])
    radius = FloatField('Radius', default=5.0, validators=[
        DataRequired(), NumberRange(min=0.0, max=180.0, message=f'0.0 < cone radius < 180.0')])
    catalog = SelectField('Catalog', choices=CATALOGS, default=CATALOGS[0][0], validators=[DataRequired()])

    # submit
    submit = SubmitField('Submit')


# +
# class: AstronomicalEllipticalQueryForm(), inherits from FlaskForm
# -
class AstronomicalEllipticalQueryForm(FlaskForm):

    # fields
    obj_name = StringField('Name', default='M51', validators=[DataRequired()])
    majaxis = FloatField('Major Axis', default=5.0, validators=[
        DataRequired(), NumberRange(min=0.0, max=180.0, message=f'0.0 < major axis < 180.0')])
    ratio = FloatField('Axis Ratio', default=0.5, validators=[
        DataRequired(), NumberRange(min=0.0, max=180.0, message=f'0.0 < axis ratio < 1.0')])
    posang = FloatField('Position Angle', default=25.0, validators=[
        DataRequired(), NumberRange(min=0.0, max=360.0, message=f'0.0 < position angle < 360.0')])
    catalog = SelectField('Catalog', choices=CATALOGS, default=CATALOGS[0][0], validators=[DataRequired()])

    # submit
    submit = SubmitField('Submit')


# +
# class: DigitalEllipticalQueryForm(), inherits from FlaskForm
# -
class DigitalEllipticalQueryForm(FlaskForm):

    # fields
    ra = FloatField('RA', default=202.4696, validators=[
        DataRequired(), NumberRange(min=0.0, max=360.0, message=f'0.0 < RA < 360.0')])
    dec = FloatField('Dec', default=47.1953, validators=[
        DataRequired(), NumberRange(min=-90.0, max=90.0, message=f'-90.0 < Dec < 90.0')])
    majaxis = FloatField('Major Axis', default=5.0, validators=[
        DataRequired(), NumberRange(min=0.0, max=180.0, message=f'0.0 < major axis < 180.0')])
    ratio = FloatField('Axis Ratio', default=0.5, validators=[
        DataRequired(), NumberRange(min=0.0, max=180.0, message=f'0.0 < axis ratio < 1.0')])
    posang = FloatField('Position Angle', default=25.0, validators=[
        DataRequired(), NumberRange(min=0.0, max=360.0, message=f'0.0 < position angle < 360.0')])
    catalog = SelectField('Catalog', choices=CATALOGS, default=CATALOGS[0][0], validators=[DataRequired()])

    # submit
    submit = SubmitField('Submit')


# +
# class: SexagisimalEllipticalQueryForm(), inherits from FlaskForm
# -
class SexagisimalEllipticalQueryForm(FlaskForm):

    # fields
    ra = StringField('RA', default='13:30:00.0', validators=[
        DataRequired(), Regexp(regex=REGEXP_RA, flags=re.IGNORECASE, message='RA format is HH:MM:SS.S')])
    dec = StringField('Dec', default='47:11:00.0', validators=[
        DataRequired(), Regexp(regex=REGEXP_DEC, flags=re.IGNORECASE, message='Dec format is +/-dd:mm:ss.s')])
    majaxis = FloatField('Major Axis', default=5.0, validators=[
        DataRequired(), NumberRange(min=0.0, max=180.0, message=f'0.0 < major axis < 180.0')])
    ratio = FloatField('Axis Ratio', default=0.5, validators=[
        DataRequired(), NumberRange(min=0.0, max=180.0, message=f'0.0 < axis ratio < 1.0')])
    posang = FloatField('Position Angle', default=25.0, validators=[
        DataRequired(), NumberRange(min=0.0, max=360.0, message=f'0.0 < position angle < 360.0')])
    catalog = SelectField('Catalog', choices=CATALOGS, default=CATALOGS[0][0], validators=[DataRequired()])

    # submit
    submit = SubmitField('Submit')


# +
# class: SassyBotForm(), inherits from FlaskForm
# -
class SassyBotForm(FlaskForm):

    # fields
    radius = FloatField('Search Radius', default=30.0, validators=[
        DataRequired(), NumberRange(min=0.0, message=f'0.0 < search radius')])
    begin_date = StringField('Begin Date', default=f'{BEGIN_ISO}', validators=[
        DataRequired(), Regexp(regex=DATE_RULE, flags=re.IGNORECASE, message='Begin date')])
    end_date = StringField('End Date', default=f'{END_ISO}', validators=[
        DataRequired(), Regexp(regex=DATE_RULE, flags=re.IGNORECASE, message='End date')])
    rb_min = FloatField('Real-Bogus Minimum', default=0.90, validators=[
        DataRequired(), NumberRange(min=0.0, max=1.0, message=f'0.0 < real-bogus minimum < 1.0')])
    rb_max = FloatField('Real-Bogus Maximum', default=0.95, validators=[
        DataRequired(), NumberRange(min=0.0, max=1.0, message=f'0.0 < real-bogus maximum < 1.0')])

    # submit
    submit = SubmitField('Submit')


# +
# class: MMTImagingForm(), inherits from FlaskForm
# -
class MMTImagingForm(FlaskForm):

    # fields
    ra_hms = StringField('RA', default='', validators=[
        DataRequired(), Regexp(regex=REGEXP_RA, flags=re.IGNORECASE, message='RA format is HH:MM:SS.S')])
    dec_dms = StringField('Dec', default='', validators=[
        DataRequired(), Regexp(regex=REGEXP_DEC, flags=re.IGNORECASE, message='Dec format is +/-dd:mm:ss.s')])
    epoch = FloatField('Epoch', default=2000.0, validators=[
        DataRequired(), NumberRange(min=2000.0, message=f'2000.0 < epoch')])
    exposuretime = FloatField('Exposure Time', default=0.0, validators=[
        DataRequired(), NumberRange(min=0.0, message=f'0.0 < exposure time')])
    filter_name = SelectField('Filter', choices=MMT_IMAGING_FILTERS, default=MMT_IMAGING_FILTERS[0], validators=[
        DataRequired()])
    magnitude = FloatField('Magnitude', default=-15.0, validators=[
        DataRequired(), NumberRange(min=-100.0, max=100.0, message=f'100.0 < magnitude < 100.0')])
    notes = StringField('Note(s)', default='', validators=[DataRequired()])
    numexposures = IntegerField('Exposures', default=1, validators=[
        DataRequired(), NumberRange(min=1, message=f'1 < # exposures')])
    zoid = StringField('Object Id', default='', validators=[DataRequired()])
    visits = IntegerField('Visits', default=1, validators=[
        DataRequired(), NumberRange(min=1, message=f'1 < # visits')])
    token = StringField('Access Token', default='', validators=[DataRequired()])

    # submit
    submit = SubmitField('Submit')


# +
# class: MMTLongslitForm(), inherits from FlaskForm
# -
class MMTLongslitForm(FlaskForm):

    # fields
    ra_hms = StringField('RA', default='', validators=[
        DataRequired(), Regexp(regex=REGEXP_RA, flags=re.IGNORECASE, message='RA format is HH:MM:SS.S')])
    dec_dms = StringField('Dec', default='', validators=[
        DataRequired(), Regexp(regex=REGEXP_DEC, flags=re.IGNORECASE, message='Dec format is +/-dd:mm:ss.s')])
    epoch = FloatField('Epoch', default=2000.0, validators=[
        DataRequired(), NumberRange(min=2000.0, message=f'2000.0 < epoch')])
    central_lambda = FloatField('Central Wavelength', default=6500.0, validators=[DataRequired()])
    exposuretime = FloatField('Exposure Time', default=0.0, validators=[
        DataRequired(), NumberRange(min=0.0, message=f'0.0 < exposure time')])
    filter_name = SelectField('Filter', choices=MMT_LONGSLIT_FILTERS, default=MMT_LONGSLIT_FILTERS[0], validators=[
        DataRequired()])
    grating = SelectField('Grating', choices=MMT_LONGSLIT_GRATINGS, default=MMT_LONGSLIT_GRATINGS[0], validators=[
        DataRequired()])
    slitwidth = SelectField('Slit Width', choices=MMT_LONGSLIT_WIDTHS, default=MMT_LONGSLIT_WIDTHS[0], validators=[
        DataRequired()])
    magnitude = FloatField('Magnitude', default=-15.0, validators=[
        DataRequired(), NumberRange(min=-100.0, max=100.0, message=f'100.0 < magnitude < 100.0')])
    notes = StringField('Note(s)', default='', validators=[DataRequired()])
    numexposures = IntegerField('Exposures', default=1, validators=[
        DataRequired(), NumberRange(min=1, message=f'1 < # exposures')])
    zoid = StringField('Object Id', default='', validators=[DataRequired()])
    visits = IntegerField('Visits', default=1, validators=[
        DataRequired(), NumberRange(min=1, message=f'1 < # visits')])
    token = StringField('Access Token', default='', validators=[DataRequired()])

    # submit
    submit = SubmitField('Submit')
