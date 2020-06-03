#!/usr/bin/env python3


# +
# import(s)
# -
import argparse
import math
import os
import requests
import sys
import time
import warnings

from astropy.coordinates import Angle
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector

# noinspection PyUnresolvedReferences
from utils import UtilsLogger


# +
# suppress all warnings!
# -
warnings.filterwarnings('ignore')


# +
# logging
# -
_log = UtilsLogger('TnsDump').logger


# +
# constant(s)
# -
SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PORT = os.getenv('SASSY_DB_PORT', None)


# +
# default(s)
# -
DEFAULT_BASE_URL = f'https://wis-tns.weizmann.ac.il'
DEFAULT_CREDENTIALS = f':'
DEFAULT_LOGIN_URL = f'{DEFAULT_BASE_URL}/user'
DEFAULT_NPAGE = 500
DEFAULT_NUMBER = 1
DEFAULT_SEARCH_URL = f"{DEFAULT_BASE_URL}/search"
DEFAULT_UNITS = ['Days', 'Months', 'Years']
DEFAULT_UNIT = DEFAULT_UNITS[0]

DEFAULT_SEARCH_PARAMS = {
    "page": 0,
    "discovered_period_value": "1",
    "discovered_period_units": "Days",
    "name": "",
    "name_like": "0",
    "isTNS_AT": "all",
    "public": "all",
    "unclassified_at": "0",
    "classified_sne": "0",
    "ra": "",
    "decl": "",
    "radius": "",
    "coords_unit": "arcsec",
    "groupid[]": "null",
    "classifier_groupid[]": "null",
    "objtype[]": "null",
    "at_type[]": "null",
    "date_start[date]": "",
    "date_end[date]": "",
    "discovery_mag_min": "",
    "discovery_mag_max": "",
    "internal_name": "",
    "redshift_min": "",
    "redshift_max": "",
    "spectra_count": "",
    "discoverer": "",
    "classifier": "",
    "discovery_instrument[]": "",
    "classification_instrument[]": "",
    "hostname": "",
    "associated_groups[]": "null",
    "ra_range_min": "",
    "ra_range_max": "",
    "decl_range_min": "",
    "decl_range_max": "",
    "ext_catid": "",
    "num_page": "500",
    "display[redshift]": "1",
    "display[hostname]": "1",
    "display[host_redshift]": "1",
    "display[source_group_name]": "1",
    "display[classifying_source_group_name]": "1",
    "display[discovering_instrument_name]": "1",
    "display[classifing_instrument_name]": "1",
    "display[programs_name]": "1",
    "display[internal_name]": "1",
    "display[isTNS_AT]": "1",
    "display[public]": "1",
    "display[end_pop_period]": "1",
    "display[spectra_count]": "1",
    "display[discoverymag]": "1",
    "display[discmagfilter]": "1",
    "display[discoverydate]": "1",
    "display[discoverer]": "1",
    "display[remarks]": "1",
    "display[sources]": "1",
    "display[bibcode]": "1",
    "display[ext_catalogs]": "1",
    "format": "html",
    "edit[type]": "",
    "edit[objname]": "",
    "edit[id]": "",
    "sort": "desc",
    "order": "id"
}


# +
# __doc__ string
# -
__doc__ = """
    % python3 tns_dump.py --help
"""


# +
# function(s)
# -
# noinspection PyBroadException
def ra_from_angle(_ra=''):
    if not isinstance(_ra, str) or _ra.strip() == '':
        return math.nan
    if not _ra.lower().endswith('hours'):
        _ra = f'{_ra} hours'
    try:
        return float(Angle(_ra).degree)
    except Exception:
        return math.nan


# noinspection PyBroadException
def dec_from_angle(_dec=''):
    if not isinstance(_dec, str) or _dec.strip() == '':
        return math.nan
    if not _dec.lower().endswith('degrees'):
        _dec = f'{_dec} degrees'
    try:
        return float(Angle(_dec).degree)
    except Exception:
        return math.nan


def coord_from_angle(_ra='', _dec=''):
    if not isinstance(_ra, str) or _ra.strip() == '':
        return math.nan, math.nan
    if not isinstance(_dec, str) or _dec.strip() == '':
        return math.nan, math.nan
    return ra_from_angle(_ra), dec_from_angle(_dec)


# +
# class: TnsTableParser()
# -
class TnsTableParser(object):

    # +
    # method: __init__()
    # -
    def __init__(self, url=DEFAULT_LOGIN_URL, credentials=DEFAULT_CREDENTIALS, number=DEFAULT_NUMBER,
                 unit=DEFAULT_UNIT, npage=DEFAULT_NPAGE, verbose=False):

        # get input(s)
        self.url = url
        self.credentials = credentials
        self.number = number
        self.unit = unit
        self.npage = npage
        self.verbose = verbose

        # private variable(s)
        self.__ans = None
        self.__response = None
        self.__soup = None
        self.__params = None
        self.__pages = -1
        self.__total = -1

        # login
        self.__session = None
        try:
            self.__session = requests.Session()
            self.__session.post(self.__url, data=dict(username=self.__username, password=self.__password))
        except Exception as e:
            self.__session = None
            _log.debug(f"self.__session={self.__session}, error={e}")

    # +
    # decorator(s)
    # -
    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, url):
        self.__url = url if (isinstance(url, str) and url.lower().startswith(f'http')) else DEFAULT_LOGIN_URL

    @property
    def credentials(self):
        return self.__credentials

    @credentials.setter
    def credentials(self, credentials):
        self.__credentials = credentials if (isinstance(credentials, str)
                                             and f':' in credentials) else DEFAULT_CREDENTIALS
        self.__username, self.__password = self.__credentials.split(f':')

    @property
    def number(self):
        return self.__number

    @number.setter
    def number(self, number):
        self.__number = number if (isinstance(number, int) and number > 0) else DEFAULT_NUMBER

    @property
    def unit(self):
        return self.__unit

    @unit.setter
    def unit(self, unit):
        self.__unit = unit if (isinstance(unit, str) and unit in DEFAULT_UNITS) else DEFAULT_UNIT

    @property
    def npage(self):
        return self.__npage

    @npage.setter
    def npage(self, npage):
        self.__npage = npage if (isinstance(npage, int) and (1 <= npage <= 1000)) else DEFAULT_NPAGE

    @property
    def verbose(self):
        return self.__verbose

    @verbose.setter
    def verbose(self, verbose):
        self.__verbose = verbose if isinstance(verbose, bool) else False

    # +
    # method: dump()
    # -
    def dump(self, _item=None, _delimiter='\n'):
        if _item is None:
            _res = f''
        elif isinstance(_item, tuple) and _item is not ():
            _res = f''.join(f'{_v}{_delimiter}' for _v in _item)[:-1]
        elif isinstance(_item, list) and _item is not []:
            _res = f''.join(f'{_v}{_delimiter}' for _v in _item)[:-1]
        elif isinstance(_item, set) and _item is not {}:
            _res = f''.join(f'{_v}{_delimiter}' for _v in _item)[:-1]
        elif isinstance(_item, dict) and _item is not {}:
            _res = f''.join(f'{_k}={_v}{_delimiter}' for _k, _v in _item.items())[:-1]
        elif isinstance(_item, str) and _item.strip().lower() == 'variables':
            _res = f'self.__url = {self.__url}, '
            _res += f'self.__credentials = {self.__credentials}, '
            _res += f'self.__number = {self.__number}, '
            _res += f'self.__unit = {self.__unit}, '
            _res += f'self.__npage = {self.__npage}, '
            _res += f'self.__verbose = {self.__verbose}, '
            _res += f'self.__response = {self.__response}, '
            _res += f'self.__params = {self.__params}, '
            _res += f'self.__soup = {self.__soup}, '
            _res += f'self.__session = {self.__session}, '
            _res += f'self.__username = {self.__username}, '
            _res += f'self.__password = {self.__password}, '
            _res += f'self.__ans = {self.__ans}, '
            _res += f'self.__pages = {self.__pages}, '
            _res += f'self.__total = {self.__total}, '
        else:
            _res = f'{str(_item)}'
        return _res

    # +
    # method: get_request()
    # -
    def get_request(self):
        """ get data from web-site """

        # noinspection PyBroadException
        try:
            if self.__session is not None:
                _requests = self.__session.get(url=self.__url, params=self.__params,)
            else:
                _requests = requests.get(url=self.__url, params=self.__params, auth=(self.__username, self.__password),)
        except Exception as e:
            if self.__verbose:
                _log.error(f"Failed calling self.get_request(), error={e}")
            return None

        # return data
        if _requests.status_code != 200 or _requests.text.strip() == '':
            if self.__verbose:
                _log.error(f"Bad response (code={_requests.status_code}, text='{_requests.text[1:80]}...')")
            return None
        else:
            return _requests

    # +
    # method: get_records()
    # -
    # noinspection PyBroadException
    def get_records(self):
        """ scrape records from soup """

        # get the results table and extract rows we want
        _table = self.__soup.find_all('table', attrs={'class': 'results-table sticky-enabled'})

        _repe = [_e.find_all('tr', attrs={'class': 'row-even public even'}) for _e in _table][0]
        _repo = [_e.find_all('tr', attrs={'class': 'row-even public odd'}) for _e in _table][0]
        _rope = [_e.find_all('tr', attrs={'class': 'row-odd public even'}) for _e in _table][0]
        _ropo = [_e.find_all('tr', attrs={'class': 'row-odd public odd'}) for _e in _table][0]
        if self.__verbose:
            _log.info(f"len(_repe)={len(_repe)}")
            _log.info(f"len(_repo)={len(_repo)}")
            _log.info(f"len(_rope)={len(_rope)}")
            _log.info(f"len(_ropo)={len(_ropo)}")

        _evens = set().union(_repe, _repo)
        _odds = set().union(_rope, _ropo)
        if self.__verbose:
            _log.info(f"len(_evens)={len(_evens)}")
            _log.info(f"len(_odds)={len(_odds)}")

        # make rows unique
        _rows = list(set().union(_evens, _odds))
        if self.__verbose:
            _log.info(f"len(_rows)={len(_rows)}")
            # _log.info(f"_rows={_rows}")

        # scrape each row
        for _e in _rows:

            # ignore elements that have no find or find_all
            if not (hasattr(_e, 'find') or hasattr(_e, 'find_all')):
                continue
            if self.__verbose:
                _log.info(f"scraping row {_e}")

            # initialize a dictionary
            _ans_tmp = {}

            # only scrape rows that include *all* these elements (class=cell-<something>)
            try:
                # <td class="cell-id">43659</td>
                _ans_tmp['tns_id'] = _e.find('td', attrs={'class': 'cell-id'}).text
                # <td class="cell-name"><a href="/object/2019oel">AT 2019oel</a></td>
                _ans_tmp['tns_name'] = (_e.find('td', attrs={'class': 'cell-name'})).find('a').text
                _link = (_e.find('td', attrs={'class': 'cell-name'})).find('a', href=True)['href']
                _ans_tmp['tns_link'] = f"{DEFAULT_BASE_URL}{_link}"
                # <td class="cell-reps">1<a class="cert-open" href="/object/2019oel/discovery-cert" rel="43659">
                # </a><a class="at-reps-open clearfix" href="/%23" rel="43659"></a></td>
                _cert = (_e.find('td', attrs={'class': 'cell-reps'})).find('a', href=True)['href']
                _ans_tmp['tns_cert'] = f"{DEFAULT_BASE_URL}{_cert}"
                # <td class="cell-class"></td>
                _ans_tmp['tns_class'] = _e.find('td', attrs={'class': 'cell-class'}).text
                # <td class="cell-ra">17:18:23.982</td>
                _ans_tmp['ra'] = _e.find('td', attrs={'class': 'cell-ra'}).text
                # <td class="cell-decl">-31:04:29.63</td>
                _ans_tmp['decl'] = _e.find('td', attrs={'class': 'cell-decl'}).text
                # <td class="cell-ot_name"></td>
                _ans_tmp['ot_name'] = _e.find('td', attrs={'class': 'cell-ot_name'}).text
                # <td class="cell-redshift"></td>
                _ans_tmp['redshift'] = _e.find('td', attrs={'class': 'cell-redshift'}).text
                # <td class="cell-hostname"></td>
                _ans_tmp['hostname'] = _e.find('td', attrs={'class': 'cell-hostname'}).text
                # <td class="cell-host_redshift"></td>
                _ans_tmp['host_redshift'] = _e.find('td', attrs={'class': 'cell-host_redshift'}).text
                # <td class="cell-source_group_name">ATLAS</td>
                _ans_tmp['source_group'] = _e.find('td', attrs={'class': 'cell-source_group_name'}).text
                # <td class="cell-classifying_source_group_name"></td>
                _ans_tmp['classifying_group'] = _e.find('td',
                                                        attrs={'class': 'cell-classifying_source_group_name'}).text
                # <td class="cell-groups">ATLAS</td>
                _ans_tmp['groups'] = _e.find('td', attrs={'class': 'cell-groups'}).text
                # <td class="cell-internal_name">ATLAS19svo</td>
                _ans_tmp['internal_name'] = _e.find('td', attrs={'class': 'cell-internal_name'}).text
                # <td class="cell-discovering_instrument_name">ATLAS1 - ACAM1</td>
                _ans_tmp['instrument_name'] = _e.find('td', attrs={'class': 'cell-discovering_instrument_name'}).text
                # <td class="cell-classifing_instrument_name"></td>
                _ans_tmp['classifying_instrument'] = _e.find('td',
                                                             attrs={'class': 'cell-classifing_instrument_name'}).text
                # <td class="cell-isTNS_AT">Y</td>
                _ans_tmp['isTNS_AT'] = _e.find('td', attrs={'class': 'cell-isTNS_AT'}).text
                # <td class="cell-public">Y</td>
                _ans_tmp['public'] = _e.find('td', attrs={'class': 'cell-public'}).text
                # <td class="cell-end_prop_period"></td>
                _ans_tmp['end_prop_period'] = _e.find('td', attrs={'class': 'cell-end_prop_period'}).text
                # <td class="cell-spectra_count"></td>
                _ans_tmp['spectra_count'] = _e.find('td', attrs={'class': 'cell-spectra_count'}).text
                # <td class="cell-discoverymag">17.775</td>
                _ans_tmp['mag'] = _e.find('td', attrs={'class': 'cell-discoverymag'}).text
                # <td class="cell-disc_filter_name">orange-ATLAS</td>
                _ans_tmp['filter'] = _e.find('td', attrs={'class': 'cell-disc_filter_name'}).text
                # <td class="cell-discoverydate">2019-08-22 06:59:02</td>
                _ans_tmp['date'] = _e.find('td', attrs={'class': 'cell-discoverydate'}).text
                # <td class="cell-discoverer">ATLAS_Bot1</td>
                _ans_tmp['discoverer'] = _e.find('td', attrs={'class': 'cell-discoverer'}).text
                # <td class="cell-remarks"></td>
                _ans_tmp['remarks'] = _e.find('td', attrs={'class': 'cell-remarks'}).text
                # <td class="cell-sources"></td>
                _ans_tmp['sources'] = _e.find('td', attrs={'class': 'cell-sources'}).text
                # <td class="cell-bibcode"></td>
                _ans_tmp['bibcode'] = _e.find('td', attrs={'class': 'cell-bibcode'}).text
                # _log.info(f"_ans_tmp['bibcode']={_ans_tmp['bibcode']}")
                _ans_tmp['catalogs'] = _e.find('td', attrs={'class': 'cell-ext_catalogs'}).text
            except Exception:
                # we did not get all elements to ignore this row
                if self.__verbose:
                    _log.info(f"ignoring row {_e}")
                continue

            # we did get all elements, so add it to the result(s)
            if self.__verbose:
                _log.debug(f"scraped row {_ans_tmp}")
            self.__ans.append(_ans_tmp)

    # +
    # method: get_soup()
    # -
    def get_soup(self, _page=0):
        """ scrape web-site page """

        # set default(s)
        self.__params['page'] = _page if (isinstance(_page, int) and _page > 0) else 0
        if self.__verbose:
            _log.debug(f'self.__params={self.__params}')

        # get request
        self.__response = self.get_request()
        if self.__verbose:
            _log.debug(f'self.__response={self.__response}')

        # get encoding
        _http_encoding = self.__response.encoding if 'charset' in self.__response.headers.get(
            'content-type', '').lower() else None
        _html_encoding = EncodingDetector.find_declared_encoding(self.__response.content, is_html=True)

        # get soup
        self.__soup = None
        try:
            if self.__verbose:
                _log.debug(f'Getting soup from self.__response.text')
            self.__soup = BeautifulSoup(self.__response.text, features='html5lib', 
                                        from_encoding=(_html_encoding or _http_encoding))
            if self.__verbose:
                _log.debug(f'Got soup from self.__response.text OK')
        except Exception as e:
            self.__soup = None
            if self.__verbose:
                _log.error(f'Failed to get soup from self.__response.text, error={e}')

    # +
    # method: scrape_tns_pages()
    # -
    def scrape_tns_pages(self):
        """ scrape web-site for tns pages """

        # set default(s)
        self.__ans = []
        self.__pages = -1
        self.__total = -1
        self.__url = DEFAULT_SEARCH_URL
        self.__params = DEFAULT_SEARCH_PARAMS
        self.__params['discovered_period_value'] = f'{self.__number}'
        self.__params['discovered_period_units'] = f'{self.__unit}'
        self.__params['num_page'] = f'{self.__npage}'

        # get soup
        self.get_soup()
        if self.__verbose:
            _log.debug(f'type(self.__soup)={type(self.__soup)}')

        # get max number of results by scraping
        if self.__soup is not None:
            _div = self.__soup.find_all('div', attrs={'class': 'count rsults'})
            _ems = [_e.find_all('em', attrs={'class': 'placeholder'}) for _e in _div][0]
            self.__total = int(_ems[-1].text)
            if self.__verbose:
                _log.debug(f'self.__total={self.__total}')
                _log.debug(f"self.__params['num_page']={self.__params['num_page']}")
        else:
            return self.__total, self.__ans

        # calculate pages
        self.__pages = math.ceil(int(self.__total) / int(self.__params['num_page']))
        if self.__verbose:
            _log.debug(f'self.__pages={self.__pages}')

        # get record(s) for page 0
        self.get_records()

        # get record(s) for other pages
        if self.__pages > 0:
            for _i in range(1, self.__pages):
                self.get_soup(_i)
                self.get_records()
                if self.__verbose:
                    _log.debug(f'sleeping for 5 seconds ...')
                time.sleep(5)

        # return result
        if self.__verbose:
            _log.debug(f'self.__total = {self.__total}')
            _log.debug(f'len(self.__ans) = {len(self.__ans)}')
        return self.__total, self.__ans


# +
# function: tns_dump()
# -
# noinspection PyBroadException
def tns_dump(login=DEFAULT_LOGIN_URL, credentials=DEFAULT_CREDENTIALS, number=DEFAULT_NUMBER,
             unit=DEFAULT_UNIT, npage=DEFAULT_NPAGE, verbose=False):

    # check input(s)
    login = login if (isinstance(login, str) and login.strip() != '' and
                      login.strip().lower().startswith(f'http')) else DEFAULT_LOGIN_URL
    credentials = credentials if (isinstance(credentials, str) and credentials.strip() != ''
                                  and ':' in credentials.strip()) else DEFAULT_CREDENTIALS
    number = number if (isinstance(number, int) and number > 0) else DEFAULT_NUMBER
    unit = unit if (isinstance(unit, str) and unit in DEFAULT_UNITS) else DEFAULT_UNIT
    npage = npage if (isinstance(npage, int) and (1 <= npage <= 1000)) else DEFAULT_NPAGE
    verbose = verbose if isinstance(verbose, bool) else False

    # instantiate the class
    try:
        _log.info(f"Instantiating TnsTableParser('{login}', '{credentials}', {number}, '{unit}', {npage}, {verbose})")
        _ttp = TnsTableParser(login, credentials, number, unit, npage, verbose)
        _log.info(f"Instantiated TnsTableParser('{login}', '{credentials}', {number}, '{unit}', {npage}, {verbose}) OK")
    except Exception as e:
        _log.error(f"Failed instantiating TnsTableParser("
                   f"'{login}', '{credentials}', {number}, '{unit}',  {npage}, {verbose}), error={e}")
        return

    # scrape the web site
    try:
        _log.info(f'Scraping pages')
        _total, _data = _ttp.scrape_tns_pages()
        _log.info(f'Scraped pages OK')
    except Exception as e:
        if verbose:
            _log.error(f'Failed scraping pages, error={e}')
        return

    if verbose:
        _log.info(f'_total={_total}')
        _log.info(f'len(_data)={len(_data)}')

    # create database records from scraped data
    for _e in _data:

        # conversion(s) 
        _tns_id = -1
        if _e.get('tns_id', '') != '':
            try:
                _tns_id = int(_e['tns_id'])
            except Exception:
                _tns_id = -1
            if verbose:
                _log.info(f"_e['tns_id']={_e['tns_id']}, _tns_id={_tns_id}")

        _ra, _dec = math.nan, math.nan
        if _e.get('ra', '') != '' and _e.get('decl', '') != '':
            try:
                _ra, _dec = coord_from_angle(_e['ra'], _e['decl'])
            except Exception:
                _ra, _dec = math.nan, math.nan
            if verbose:
                _log.info(f"_e['ra']={_e['ra']}, _ra={_ra}")
                _log.info(f"_e['decl']={_e['decl']}, _dec={_dec}")

        _mag = math.nan
        if _e.get('mag', '') != '':
            try:
                _mag = float(_e['mag'])
            except Exception:
                _mag = math.nan
            if verbose:
                _log.info(f"_e['mag']={_e['mag']}, _mag={_mag}")

        _z = math.nan
        if _e.get('redshift', '') != '':
            try:
                _z = float(_e['redshift'])
            except Exception:
                _z = math.nan
            if verbose:
                _log.info(f"_e['redshift']={_e['redshift']}, _z={_z}")

        _h_z = math.nan
        if _e.get('host_redshift', '') != '':
            try:
                _h_z = float(_e['host_redshift'])
            except Exception:
                _h_z = math.nan
            if verbose:
                _log.info(f"_e['host_redshift']={_e['host_redshift']}, _h_z={_h_z}")

        # report
        if verbose:
            _log.info(f'_e = {_e}')


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s)
    # noinspection PyTypeChecker
    _parser = argparse.ArgumentParser(description=f'Ingest TNS events from TNS',
                                      formatter_class=argparse.RawTextHelpFormatter)
    _parser.add_argument(f'-l', f'--login', default=f'{DEFAULT_BASE_URL}/login',
                         help=f"""URL url=<str>, defaults to %(default)s""")
    _parser.add_argument(f'-c', f'--credentials', default=f'{DEFAULT_CREDENTIALS}',
                         help=f"""server credentials=<str>:<str>, defaults to '%(default)s'""")
    _parser.add_argument(f'-n', f'--number', default=DEFAULT_NUMBER,
                         help=f"""Number <int>, defaults to %(default)s""")
    _parser.add_argument(f'-p', f'--npage', default=DEFAULT_NPAGE,
                         help=f"""Number of results per page <int>, defaults to %(default)s""")
    _parser.add_argument(f'-u', f'--unit', default=DEFAULT_UNIT,
                         help=f"""Unit <str>, defaults to '%(default)s' from {DEFAULT_UNITS}""")
    _parser.add_argument(f'--verbose', default=False, action='store_true',
                         help='if present, produce more verbose output')
    args = _parser.parse_args()

    # execute
    if args:
        tns_dump(args.login, args.credentials, int(args.number), args.unit, int(args.npage), bool(args.verbose))
    else:
        _log.critical(f'Insufficient command line arguments specified\nUse: python {sys.argv[0]} --help')
