#!/usr/bin/env python3


# +
# import(s)
# -
from src.utils.utils import *

import json
import math
import requests


# +
# class: Alerce()
# _
# noinspection PyBroadException
class Alerce(object):

    # +
    # method: __init__()
    # -
    def __init__(self, log=None):

        # get input(s)
        self.log = log

        # set default(s)
        self.__answer = None
        self.__answer_l = None
        self.__answer_r = None
        self.__catalog = None
        self.__classifier = None
        self.__classifier_key = None
        self.__classifier_type = None
        self.__classifier_value = math.nan
        self.__dec = math.nan
        self.__detections = None
        self.__features = None
        self.__json = None
        self.__match = None
        self.__match_all = None
        self.__non_detections = None
        self.__oid = None
        self.__probabilities = None
        self.__payload = None
        self.__query = None
        self.__ra = math.nan
        self.__radius = math.nan
        self.__response = None
        self.__sql = None
        self.__stats = None
        self.__url = None

        # structure(s)
        self.__alerce_catalogs = [
            "AAVSO_VSX", "AKARI", "APASS", "CRTS_per_var", "Cosmos", "DECaLS", "FIRST",
            "GAIADR1", "GAIADR2", "GALEX", "HSCv2", "IPHAS", "IRACgc", "NEDz", "NVSS", "PTFpc",
            "ROSATfsc", "SAGE", "SDSSDR10", "SDSSoffset", "SWIREz", "SkyMapper", "SpecSDSS",
            "TMASS", "TMASSxsc", "UCAC4", "UKIDSS", "VISTAviking", "VSTatlas", "VSTkids",
            "WISE", "XMM", "unWISE"]
        self.__alerce_classifier = ['early', 'late']
        self.__alerce_detection_keys = (
            "candid", "candid_str", "dec", "diffmaglim", "distpsnr1", "fid", "field", "has_stamps", "isdiffpos",
            "magap", "magap_corr", "magnr", "magpsf", "magpsf_corr", "mjd", "oid", "parent_candid", "ra", "rb",
            "rcid", "sgscore1", "sigmadec", "sigmagap", "sigmagap_corr", "sigmagnr", "sigmapsf", "sigmapsf_corr",
            "sigmara")
        self.__alerce_early_classifier = {
            'agn_prob': 'AGN', 'sn_prob': 'Supernova', 'vs_prob': 'Variable Star',
            'asteroid_prob': 'Asteroid', 'bogus_prob': 'Bogus'}
        self.__alerce_early_probability_keys = (
            "agn_prob", "asteroid_prob", "bogus_prob", "classifier_version", "oid", "sn_prob", "vs_prob")
        self.__alerce_feature_keys = (
            "Amplitude_1", "Amplitude_2", "AndersonDarling_1", "AndersonDarling_2", "Autocor_length_1",
            "Autocor_length_2", "Beyond1Std_1", "Beyond1Std_2", "Con_1", "Con_2", "Eta_e_1", "Eta_e_2",
            "ExcessVar_1", "ExcessVar_2", "GP_DRW_sigma_1", "GP_DRW_sigma_2", "GP_DRW_tau_1", "GP_DRW_tau_2",
            "Gskew_1", "Gskew_2", "Harmonics_mag_1_1", "Harmonics_mag_1_2", "Harmonics_mag_2_1",
            "Harmonics_mag_2_2", "Harmonics_mag_3_1", "Harmonics_mag_3_2", "Harmonics_mag_4_1",
            "Harmonics_mag_4_2", "Harmonics_mag_5_1", "Harmonics_mag_5_2", "Harmonics_mag_6_1",
            "Harmonics_mag_6_2", "Harmonics_mag_7_1", "Harmonics_mag_7_2", "Harmonics_mse_1", "Harmonics_mse_2",
            "Harmonics_phase_2_1", "Harmonics_phase_2_2", "Harmonics_phase_3_1", "Harmonics_phase_3_2",
            "Harmonics_phase_4_1", "Harmonics_phase_4_2", "Harmonics_phase_5_1", "Harmonics_phase_5_2",
            "Harmonics_phase_6_1", "Harmonics_phase_6_2", "Harmonics_phase_7_1", "Harmonics_phase_7_2",
            "IAR_phi_1", "IAR_phi_2", "LinearTrend_1", "LinearTrend_2", "MaxSlope_1", "MaxSlope_2", "Mean_1",
            "Mean_2", "Meanvariance_1", "Meanvariance_2", "MedianAbsDev_1", "MedianAbsDev_2", "MedianBRP_1",
            "MedianBRP_2", "PairSlopeTrend_1", "PairSlopeTrend_2", "PercentAmplitude_1", "PercentAmplitude_2",
            "PeriodLS_v2_1", "PeriodLS_v2_2", "Period_fit_v2_1", "Period_fit_v2_2", "Psi_CS_v2_1", "Psi_CS_v2_2",
            "Psi_eta_v2_1", "Psi_eta_v2_2", "Pvar_1", "Pvar_2", "Q31_1", "Q31_2", "Rcs_1", "Rcs_2",
            "SF_ML_amplitude_1", "SF_ML_amplitude_2", "SF_ML_gamma_1", "SF_ML_gamma_2", "Skew_1", "Skew_2",
            "SmallKurtosis_1", "SmallKurtosis_2", "Std_1", "Std_2", "StetsonK_1", "StetsonK_2",
            "delta_mag_fid_1", "delta_mag_fid_2", "delta_mjd_fid_1", "delta_mjd_fid_2", "dmag_first_det_fid_1",
            "dmag_first_det_fid_2", "dmag_non_det_fid_1", "dmag_non_det_fid_2", "g-r_max", "g-r_mean", "gal_b",
            "gal_l", "last_diffmaglim_before_fid_1", "last_diffmaglim_before_fid_2", "last_mjd_before_fid_1",
            "last_mjd_before_fid_2", "max_diffmaglim_after_fid_1", "max_diffmaglim_after_fid_2",
            "max_diffmaglim_before_fid_1", "max_diffmaglim_before_fid_2", "median_diffmaglim_after_fid_1",
            "median_diffmaglim_after_fid_2", "median_diffmaglim_before_fid_1", "median_diffmaglim_before_fid_2",
            "mhps_PN_flag_1", "mhps_PN_flag_2", "mhps_high_1", "mhps_high_2", "mhps_low_1", "mhps_low_2",
            "mhps_non_zero_1", "mhps_non_zero_2", "mhps_ratio_1", "mhps_ratio_2", "n_det_fid_1", "n_det_fid_2",
            "n_neg_1", "n_neg_2", "n_non_det_after_fid_1", "n_non_det_after_fid_2", "n_non_det_before_fid_1",
            "n_non_det_before_fid_2", "n_pos_1", "n_pos_2", "n_samples_1", "n_samples_2", "oid",
            "positive_fraction_1", "positive_fraction_2", "rb", "sgscore1")
        self.__alerce_late_classifier = {
            "AGN-I_prob": "AGN Type I", "Blazar_prob": "Blazar", "CV/Nova_prob": "Cataclysmic Variable / Nova",
            "QSO-I_prob": "Quasar Type I", "SLSN_prob": "Super-luminous Supernova", "SNII_prob": "Supernova Type II",
            "SNIa_prob": "Supernova Type Ia", "SNIbc_prob": "Supernova Type Ibc",
            "EBC_prob": "Eclipsing Binary (Contact)", "EBSD/D_prob": "Eclipsing Binary (Detached/Semi-Detached)",
            "Periodic-Other_prob": "Periodic/Other", "RS-CVn_prob": "RS Canum Venaticorum", "Ceph_prob": "Cepheid",
            "DSCT_prob": "Delta Scuti", "LPV_prob": "Long Period Variable", "RRL_prob": "RR Lyra"}
        self.__alerce_late_probability_keys = (
            "AGN-I_prob", "Blazar_prob", "CV/Nova_prob", "Ceph_prob", "DSCT_prob", "EBC_prob", "EBSD/D_prob",
            "LPV_prob", "Periodic-Other_prob", "QSO-I_prob", "RRL_prob", "RS-CVn_prob", "SLSN_prob", "SNII_prob",
            "SNIa_prob", "SNIbc_prob", "oid")
        self.__alerce_non_detection_keys = ("diffmaglim", "fid", "mjd", "oid")
        self.__alerce_stat_keys = (
            "catalogid", "classearly", "classrf", "classxmatch", "deltajd", "first_magap_g", "first_magap_r",
            "first_magpsf_g", "first_magpsf_r", "firstmjd", "last_magap_g", "last_magap_r", "last_magpsf_g",
            "last_magpsf_r", "lastmjd", "max_magap_g", "max_magap_r", "max_magpsf_g", "max_magpsf_r", "mean_magap_g",
            "mean_magap_r", "mean_magpsf_g", "mean_magpsf_r", "meandec", "meanra", "median_magap_g",
            "median_magap_r", "median_magpsf_g", "median_magpsf_r", "min_magap_g", "min_magap_r", "min_magpsf_g",
            "min_magpsf_r", "nobs", "oid", "pclassearly", "pclassrf", "period", "sigma_magap_g", "sigma_magap_r",
            "sigma_magpsf_g", "sigma_magpsf_r", "sigmadec", "sigmara")

        # sql
        self.__alerce_payload = {
            # total record(s) searched
            'total': 100,
            # number of records per page
            'records_per_pages': 20,
            # page number
            'page': 1,
            # sort by column heading
            'sortBy': 'nobs',
            # query parameter(s) structure
            'query_parameters': {
                # database filter(s)
                'filters': {
                    'oid': None,
                    'nobs': {'min': 0, 'max': 9223372036854775807},
                    # late classifier (random forest)
                    'classrf': 9223372036854775807,
                    'pclassrf': math.nan,
                    # early classifier
                    'classearly': 9223372036854775807,
                    'pclassearly': math.nan,
                    # photometry
                    'min_magap_g': {'min': math.nan, 'max': math.nan},
                    'max_magap_g': {'min': math.nan, 'max': math.nan},
                    'median_magap_g': {'min': math.nan, 'max': math.nan},
                    'mean_magap_g': {'min': math.nan, 'max': math.nan},
                    'min_magap_r': {'min': math.nan, 'max': math.nan},
                    'max_magap_r': {'min': math.nan, 'max': math.nan},
                    'median_magap_r': {'min': math.nan, 'max': math.nan},
                    'mean_magap_r': {'min': math.nan, 'max': math.nan},
                    'min_magpsf_g': {'min': math.nan, 'max': math.nan},
                    'max_magpsf_g': {'min': math.nan, 'max': math.nan},
                    'median_magpsf_g': {'min': math.nan, 'max': math.nan},
                    'mean_magpsf_g': {'min': math.nan, 'max': math.nan},
                    'min_magpsf_r': {'min': math.nan, 'max': math.nan},
                    'max_magpsf_r': {'min': math.nan, 'max': math.nan},
                    'median_magpsf_r': {'min': math.nan, 'max': math.nan},
                    'mean_magpsf_r': {'min': math.nan, 'max': math.nan},
                    'min_magpsf_corr_g': {'min': math.nan, 'max': math.nan},
                    'max_magpsf_corr_g': {'min': math.nan, 'max': math.nan},
                    'median_magpsf_corr_g': {'min': math.nan, 'max': math.nan},
                    'mean_magpsf_corr_g': {'min': math.nan, 'max': math.nan},
                    'min_magpsf_corr_r': {'min': math.nan, 'max': math.nan},
                    'max_magpsf_corr_r': {'min': math.nan, 'max': math.nan},
                    'median_magpsf_corr_r': {'min': math.nan, 'max': math.nan},
                    'mean_magpsf_corr_r': {'min': math.nan, 'max': math.nan}
                },
                # co-ordinate(s)
                'coordinates': {'ra': math.nan, 'dec': math.nan, 'sr': math.nan},
                # date range
                'dates': {'firstmjd': {'min': math.nan, 'max': math.nan}}
            }
        }

        # http code(s)
        self.__http_codes = {
            100: "Continue", 101: "Switching Protocols", 102: "Processing (WebDAV)",
            200: "OK", 201: "Created", 202: "Accepted", 203: "Non-Authoritative Information",
            204: "No Content", 205: "Reset Content", 206: "Partial Content", 207: "Multi-Status (WebDAV)",
            208: "Already Reported (WebDAV)", 226: "IM Used",
            300: "Multiple Choices", 301: "Moved Permanently", 302: "Found", 303: "See Other",
            304: "Not Modified", 305: "Use Proxy", 306: "(Unused)", 307: "Temporary Redirect",
            308: "Permanent Redirect (experimental)",
            400: "Bad Request", 401: "Unauthorized", 402: "Payment Required", 403: "Forbidden", 404: "Not Found",
            405: "Method Not Allowed", 406: "Not Acceptable", 407: "Proxy Authentication Required",
            408: "Request Timeout", 409: "Conflict", 410: "Gone", 411: "Length Required", 412: "Precondition Failed",
            413: "Request Entity Too Large", 414: "Request-URI Too Long", 415: "Unsupported Media Type",
            416: "Requested Range Not Satisfiable", 417: "Expectation Failed", 418: "I'm a teapot (RFC 2324)",
            420: "Enhance Your Calm (Twitter)", 422: "Unprocessable Entity (WebDAV)", 423: "Locked (WebDAV)",
            424: "Failed Dependency (WebDAV)", 425: "Reserved for WebDAV", 426: "Upgrade Required",
            428: "Precondition Required", 429: "Too Many Requests", 431: "Request Header Fields Too Large",
            444: "No Response (Nginx)", 449: "Retry With (Microsoft)",
            450: "Blocked by Windows Parental Controls (Microsoft)", 451: "Unavailable For Legal Reasons",
            499: "Client Closed Request (Nginx)",
            500: "Internal Server Error", 501: "Not Implemented", 502: "Bad Gateway", 503: "Service Unavailable",
            504: "Gateway Timeout", 505: "HTTP Version Not Supported", 506: "Variant Also Negotiates (Experimental)",
            507: "Insufficient Storage (WebDAV)", 508: "Loop Detected (WebDAV)",
            509: "Bandwidth Limit Exceeded (Apache)", 510: "Not Extended", 511: "Network Authentication Required"}

    # +
    # decorator(s)
    # -
    @property
    def log(self):
        return self.__log

    @log.setter
    def log(self, log=None):
        if isinstance(log, logging.Logger):
            self.__log = log
        elif isinstance(log, bool) and log:
            self.__log = UtilsLogger('Alerce').logger
        else:
            self.__log = None

    # +
    # getter(s)
    # -
    @property
    def alerce_catalogs(self):
        return self.__alerce_catalogs

    @property
    def alerce_payload(self):
        return self.__alerce_payload

    @property
    def answer(self):
        return self.__answer

    @property
    def answer_l(self):
        return self.__answer_l

    @property
    def answer_r(self):
        return self.__answer_r

    @property
    def catalog(self):
        return self.__catalog

    @property
    def classifier(self):
        return self.__classifier

    @property
    def classifier_key(self):
        return self.__classifier_key

    @property
    def classifier_type(self):
        return self.__classifier_type

    @property
    def classifier_value(self):
        return self.__classifier_value

    @property
    def dec(self):
        return self.__dec

    @property
    def detections(self):
        return self.__detections

    @property
    def features(self):
        return self.__features

    @property
    def json(self):
        return self.__json

    @property
    def match(self):
        return self.__match

    @property
    def match_all(self):
        return self.__match_all

    @property
    def non_detections(self):
        return self.__non_detections

    @property
    def oid(self):
        return self.__oid

    @property
    def payload(self):
        return self.__payload

    @property
    def probabilities(self):
        return self.__probabilities

    @property
    def query(self):
        return self.__query

    @property
    def ra(self):
        return self.__ra

    @property
    def radius(self):
        return self.__radius

    @property
    def response(self):
        return self.__response

    @property
    def sql(self):
        return self.__sql

    @property
    def stats(self):
        return self.__stats

    @property
    def url(self):
        return self.__url

    # +
    # (hidden) method: __doc__()
    # -
    @staticmethod
    def __doc__():
        return """
            Use:
                from src.utils.Alerce import *
                _a = Alerce()
                _a = Alerce(log=False)
                _a = Alerce(log=True)
                _a = Alerce(log=UtilsLogger('Alerce').logger)
        
            API Method(s):
                crossmatch(catalog='', ra=math.nan, dec=math.nan, radius=math.nan)
                crossmatch_all(ra=math.nan, dec=math.nan, radius=math.nan)
                get_classifier(oid='', classifier='')
                get_detections(oid='')
                get_features(oid='')
                get_non_detections(oid='')
                get_probabilities(oid='')
                get_query(payload=None)
                get_sql(payload=None)
                get_stats(oid='')
        
            Documentation:
                print(Alerce().__doc__())
                print(Alerce().crossmatch.__doc__)
                print(Alerce().crossmatch_all.__doc__)
                print(Alerce().get_classifier.__doc__)
                print(Alerce().get_detections.__doc__)
                print(Alerce().get_features.__doc__)
                print(Alerce().get_non_detections.__doc__)
                print(Alerce().get_probabilities.__doc__)
                print(Alerce().get_query.__doc__)
                print(Alerce().get_sql.__doc__)
                print(Alerce().get_stats.__doc__)
        
            Example(s):
                _a.crossmatch(catalog='GAIADR2', ra=13.5, dec=47.2, radius=60.0)
                _a.crossmatch_all(ra=13.5, dec=47.2, radius=60.0)
                _a.get_classifier(oid='ZTF20aaccyfe', classifier='early')
                _a.get_classifier(oid='ZTF20aaccyfe', classifier='late')
                _a.get_detections(oid='ZTF20aaccyfe')
                _a.get_features(oid='ZTF20aaccyfe')
                _a.get_non_detections(oid='ZTF20aaccyfe')
                _a.get_probabilities(oid='ZTF20aaccyfe')
                _a.get_query(payload={"query_parameters": {"dates": {"firstmjd": {"min": 58682}}}})
                _a.get_sql(payload={"query_parameters": {"dates": {"firstmjd": {"min": 58682}}}})
                _a.get_stats(oid='ZTF20aaccyfe')
        
        """

    # +
    # (hidden) method: __http_get__()
    # -
    def __http_get__(self):
        """ execute and parse a GET request """
        self.__answer = None
        self.__response = None
        try:
            if self.__log:
                self.__log.debug(f"calling requests.get(url='{self.__url}')")
            self.__response = requests.get(url=self.__url)
            self.__answer = json.loads(self.__parse_response__())
        except Exception as _e:
            if self.__log:
                self.__log.error(f"failed calling requests.get(url='{self.__url}'), error={_e}")
        return self.__answer

    # +
    # (hidden) method: __http_post__()
    # -
    def __http_post__(self):
        """ execute and parse a POST request """
        self.__answer = None
        self.__response = None
        try:
            if self.__log:
                self.__log.debug(f"calling requests.post(url='{self.__url}', json={self.__json})")
            self.__response = requests.post(url=self.__url, json=self.__json)
            self.__answer = json.loads(self.__parse_response__())
        except Exception as _e:
            if self.__log:
                self.__log.error(f"failed calling requests.post(url='{self.__url}', json={self.__json}), error={_e}")
        return self.__answer

    # +
    # (hidden) method: __http_status__()
    # -
    # noinspection PyBroadException
    def __http_status__(self, _code=-1):
        """ return boolean for valid/invalid HTTP request status"""
        try:
            return True if self.__http_codes.get(_code, None) is not None else False
        except:
            return False

    # +
    # (hidden) method: __parse_response__()
    # -
    # noinspection PyBroadException
    def __parse_response__(self):
        """ return HTTP text response if valid """
        if self.__response is not None and hasattr(self.__response, 'status_code') and \
                self.__http_status__(int(self.__response.status_code)) and hasattr(self.__response, 'text'):
            if self.__response.status_code == 200:
                return self.__response.text
            else:
                return '{}'

    # +
    # (hidden) method: __reinit__()
    # -
    def __reinit__(self):
        """ re-initialize all private variable(s)"""
        self.__answer = None
        self.__answer_l = None
        self.__answer_r = None
        self.__catalog = None
        self.__classifier = None
        self.__classifier_key = None
        self.__classifier_type = None
        self.__classifier_value = math.nan
        self.__dec = math.nan
        self.__detections = None
        self.__features = None
        self.__json = None
        self.__match = None
        self.__match_all = None
        self.__non_detections = None
        self.__oid = None
        self.__payload = None
        self.__probabilities = None
        self.__query = None
        self.__ra = math.nan
        self.__radius = math.nan
        self.__response = None
        self.__stats = None
        self.__sql = None
        self.__url = None

    # +
    # (hidden) method: __verify_dict__()
    # -
    # noinspection PyBroadException
    @staticmethod
    def __verify_dict__(_d=None):
        """ verify contents of a dictionary """
        try:
            return all(isinstance(_v, (float, str, bool, list, dict, tuple)) for
                       _k, _v in _d.items() if _v is not None)
        except:
            return False

    # +
    # (hidden) method: __verify_keys__()
    # -
    # noinspection PyBroadException
    @staticmethod
    def __verify_keys__(_d=None, _k=None):
        """ verify all required dictionary keys are present """
        try:
            return all(_t in _k for _t in _d)
        except:
            return False

    # +
    # method: crossmatch()
    # -
    def crossmatch(self, catalog='GAIADR2', ra=math.nan, dec=math.nan, radius=math.nan):
        """
            :param catalog: str, case-sensitive, supported catalogs from Alerce().alerce_catalogs
            :param ra: float, RA in digital degrees
            :param dec: float, Dec in digital degrees
            :param radius: float, search radius in digital arc-seconds
            :return: dictionary cone search match against catalog or {}
        """

        # check input(s)
        if not isinstance(catalog, str) or catalog.strip() not in self.__alerce_catalogs:
            return
        if not isinstance(ra, float) or ra is math.nan or not (-360.0 <= ra <= 360.0):
            return
        if not isinstance(dec, float) or dec is math.nan or not (-90.0 <= dec <= 90.0):
            return
        if not isinstance(radius, float) or radius is math.nan or (radius <= 0.0):
            return
        if self.__log:
            self.__log.debug(f"crossmatch(catalog='{catalog}', ra={ra}, dec={dec}, radius={radius})")

        # execute
        self.__reinit__()
        self.__catalog = catalog
        self.__dec = dec
        self.__ra = ra
        self.__radius = radius
        self.__url = f"https://catshtm.alerce.online/crossmatch?" \
                     f"catalog={self.__catalog}&ra={self.__ra}&dec={self.__dec}&radius={self.__radius}"
        self.__match = self.__http_get__()
        return self.__match

    # +
    # method: crossmatch_all()
    # -
    def crossmatch_all(self, ra=math.nan, dec=math.nan, radius=math.nan):
        """
            :param ra: float, RA in digital degrees
            :param dec: float, Dec in digital degrees
            :param radius: float, search radius in digital arc-seconds
            :return: dictionary cone search match against all catalogs or {}
        """

        # check input(s)
        if not isinstance(ra, float) or ra is math.nan or not (-360.0 <= ra <= 360.0):
            return
        if not isinstance(dec, float) or dec is math.nan or not (-90.0 <= dec <= 90.0):
            return
        if not isinstance(radius, float) or radius is math.nan or (radius <= 0.0):
            return
        if self.__log:
            self.__log.debug(f"crossmatch_all(ra={ra}, dec={dec}, radius={radius})")

        # execute
        self.__reinit__()
        self.__dec = dec
        self.__ra = ra
        self.__radius = radius
        self.__url = f"https://catshtm.alerce.online/crossmatch_all?" \
                     f"ra={self.__ra}&dec={self.__dec}&radius={self.__radius}"
        self.__match_all = self.__http_get__()
        return self.__match_all

    # +
    # method: get_classifier()
    # -
    def get_classifier(self, oid='', classifier='early'):
        """
            :param oid: str, case-sensitive, ZTF identifier
            :param classifier: str, choose from 'early', 'late'
            :return: tuple of (key, type, value) for ZTF identifier
        """

        # check input(s)
        if not isinstance(oid, str) or oid.strip() == '':
            return None, None, math.nan
        if not isinstance(classifier, str) or classifier.strip().lower() not in self.__alerce_classifier:
            return None, None, math.nan
        if self.__log:
            self.__log.debug(f"get_classifier(oid='{oid}', classifier='{classifier}')")

        # execute
        self.__reinit__()
        self.__classifier = classifier.strip().lower()
        self.__oid = oid
        self.__json = {'oid': f'{self.__oid}'}
        self.__url = 'https://ztf.alerce.online/get_probabilities'
        self.__answer = self.__http_post__()

        # get classifier
        try:
            self.__answer_l = self.__answer['result']['probabilities'][f'{self.__classifier}_classifier']
            if self.__verify_dict__(self.__answer_l) and (
                    self.__verify_keys__(self.__answer_l, self.__alerce_early_probability_keys) or
                    self.__verify_keys__(self.__answer_l, self.__alerce_late_probability_keys)):
                self.__answer_r = {_v: _k for _k, _v in self.__answer_l.items() if isinstance(_v, float)}
                self.__classifier_value = max(self.__answer_r.keys())
                self.__classifier_key = self.__answer_r[self.__classifier_value]
                if ('early' in self.__classifier) and (self.__classifier_key in self.__alerce_early_classifier):
                    self.__classifier_type = self.__alerce_early_classifier[self.__classifier_key]
                elif ('late' in self.__classifier) and (self.__classifier_key in self.__alerce_late_classifier):
                    self.__classifier_type = self.__alerce_late_classifier[self.__classifier_key]
        except:
            pass
        return self.__classifier_key, self.__classifier_type, self.__classifier_value

    # +
    # method: get_detections()
    # -
    def get_detections(self, oid=''):
        """
            :param oid: str, case-sensitive, ZTF identifier
            :return: dictionary of detections for ZTF identifier or {}
        """

        # check input(s)
        if not isinstance(oid, str) or oid.strip() == '':
            return
        if self.__log:
            self.__log.debug(f"get_detections(oid='{oid}')")

        # execute
        self.__reinit__()
        self.__oid = oid
        self.__url = 'https://ztf.alerce.online/get_detections'
        self.__json = {'oid': f'{self.__oid}'}
        self.__detections = self.__http_post__()
        return self.__detections

    # +
    # method: get_features()
    # -
    def get_features(self, oid=''):
        """
            :param oid: str, case-sensitive, ZTF identifier
            :return: dictionary of features for ZTF identifier or {}
        """

        # check input(s)
        if not isinstance(oid, str) or oid.strip() == '':
            return
        if self.__log:
            self.__log.debug(f"get_features(oid='{oid}')")

        # execute
        self.__reinit__()
        self.__oid = oid
        self.__url = 'https://ztf.alerce.online/get_features'
        self.__json = {'oid': f'{self.__oid}'}
        self.__features = self.__http_post__()
        return self.__features

    # +
    # method: get_non_detections()
    # -
    def get_non_detections(self, oid=''):
        """
            :param oid: str, case-sensitive, ZTF identifier
            :return: dictionary of non-detections for ZTF identifier or {}
        """

        # check input(s)
        if not isinstance(oid, str) or oid.strip() == '':
            return
        if self.__log:
            self.__log.debug(f"get_non_detections(oid='{oid}')")

        # execute
        self.__reinit__()
        self.__oid = oid
        self.__url = 'https://ztf.alerce.online/get_non_detections'
        self.__json = {'oid': f'{self.__oid}'}
        self.__non_detections = self.__http_post__()
        return self.__non_detections

    # +
    # method: get_probabilities()
    # -
    def get_probabilities(self, oid=''):
        """
            :param oid: str, case-sensitive, ZTF identifier
            :return: dictionary of probabilities for ZTF identifier or {}
        """

        # check input(s)
        if not isinstance(oid, str) or oid.strip() == '':
            return
        if self.__log:
            self.__log.debug(f"get_probabilities(oid='{oid}')")

        # execute
        self.__reinit__()
        self.__oid = oid
        self.__url = 'https://ztf.alerce.online/get_probabilities'
        self.__json = {'oid': f'{self.__oid}'}
        self.__probabilities = self.__http_post__()
        return self.__probabilities

    # +
    # method: get_query()
    # -
    def get_query(self, payload=None):
        """
            :param payload: dictionary (over-rides Alerce().default_payload)
            :return: dictionary of database values or {}
        """

        # check input(s)
        if not isinstance(payload, dict) or payload == {}:
            return
        if self.__log:
            self.__log.debug(f"get_query(payload={payload})")

        # execute
        self.__reinit__()
        self.__payload = payload
        self.__json = {**self.__alerce_payload, **self.__payload}
        self.__url = 'https://ztf.alerce.online/query'
        self.__query = self.__http_post__()
        return self.__query

    # +
    # method: get_sql()
    # -
    def get_sql(self, payload=None):
        """
            :param payload: dictionary (over-rides Alerce().default_payload)
            :return: database query string or ''
        """

        # check input(s)
        if not isinstance(payload, dict) or payload == {}:
            return
        if self.__log:
            self.__log.debug(f"get_sql(payload={payload})")

        # execute
        self.__reinit__()
        self.__payload = payload
        self.__json = {**self.__alerce_payload, **self.__payload}
        self.__url = 'https://ztf.alerce.online/get_sql'
        self.__response = requests.post(url=self.__url, json=self.__json)
        self.__sql = self.__parse_response__()
        return self.__sql

    # +
    # method: get_stats()
    # -
    def get_stats(self, oid=''):
        """
            :param oid: str, case-sensitive, ZTF identifier
            :return: dictionary of stats for ZTF identifier or {}
        """

        # check input(s)
        if not isinstance(oid, str) or oid.strip() == '':
            return
        if self.__log:
            self.__log.debug(f"get_stats(oid='{oid}')")

        # execute
        self.__reinit__()
        self.__oid = oid
        self.__url = 'https://ztf.alerce.online/get_stats'
        self.__json = {'oid': f'{self.__oid}'}
        self.__stats = self.__http_post__()
        return self.__stats
