#!/usr/bin/env python3


# +
# import(s)
# -
import argparse
import math
import hashlib
import os
import re
import requests
import sys
import warnings

from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
from datetime import datetime
from pprint import pprint
from src.models.ligo_q3c import LigoQ3cRecord
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils import UtilsLogger


# +
# suppress all warnings!
# -
warnings.filterwarnings('ignore')


# +
# logging
# -
_log = UtilsLogger('LigoQ3c').logger


# +
# default(s)
# -
DEFAULT_URL = f'https://wis-tns.weizmann.ac.il/ligo/events'
DEFAULT_CREDENTIALS = f':'
DEFAULT_SCHEMA = f'json'


# +
# constant(s)
# -
SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_PORT = os.getenv('SASSY_DB_PORT', None)
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)

TNS_LIGO_Q3C_SUPPORTED_EVENTS = re.compile(r'GW\d{8}_\d{6}')
TNS_LIGO_Q3C_SUPPORTED_SCHEMAS = [f'json', f'tsv']


# +
# __doc__ string
# -
__doc__ = """

    % python3 ligo_q3c_scrape.py --help

"""


# +
# class: LigoQ3cTableParser()
# -
class LigoQ3cTableParser(object):

    # +
    # method: __init__()
    # -
    def __init__(self, url=DEFAULT_URL, credentials=DEFAULT_CREDENTIALS, schema=DEFAULT_SCHEMA, verbose=False):

        # get input(s)
        self.url = url
        self.credentials = credentials
        self.schema = schema
        self.verbose = verbose

        # private variable(s)
        self.__response = None
        self.__soup = None

        self.__after = []
        self.__aka = []
        self.__before = []
        self.__dates = []
        self.__events = []
        self.__names = []

        self.__columns = 0
        self.__headers = []
        self.__rows = 0

    # +
    # decorator(s)
    # -
    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, url):
        self.__url = url if (
                isinstance(url, str) and url.strip() != f'' and url.lower().startswith(f'http')) else DEFAULT_URL

    @property
    def credentials(self):
        return self.__credentials

    @credentials.setter
    def credentials(self, credentials):
        self.__credentials = credentials if (
                isinstance(credentials, str) and credentials.strip() != f'' and
                f':' in credentials) else DEFAULT_CREDENTIALS
        self.__username, self.__password = self.__credentials.split(f':')

    @property
    def schema(self):
        return self.__schema

    @schema.setter
    def schema(self, schema):
        self.__schema = schema.lower() if schema in TNS_LIGO_Q3C_SUPPORTED_SCHEMAS else DEFAULT_SCHEMA

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
        else:
            _res = f'{str(_item)}'
        return _res

    # +
    # method: get_after()
    # -
    def get_after(self, _table=None):
        """ gets links labelled as after the event """

        # check input(s)
        self.__after= []
        if _table is None or not hasattr(_table, f'find_all'):
            return

        # find <td class="cell-downloads"></td> elements
        for _td in _table.find_all('td', attrs={'class': 'cell-downloads'}):

            # find <a href="/ligo/event/*"></a> elements
            for _a in _td.find_all('a', href=True):

                # check names are in correct format
                if _a['href'].strip().lower().startswith(f'http') and _a['href'].strip().lower().endswith(self.__schema):

                    # check for search pattern
                    if f'after' in _a['href'].strip().lower() and f"{_a['href'].strip()}" not in self.__after:
                        self.__after.append(f"{_a['href'].strip()}")

    # +
    # method: get_aka()
    # -
    def get_aka(self, _table=None):
        """ get the also-known-as name of the event """

        # check input(s)
        self.__aka = []
        if _table is None or not hasattr(_table, f'find_all'):
            return

        # find <td class="cell-name"></td> elements
        for _td in _table.find_all('td', attrs={'class': 'cell-name'}):

            # find <a href="/ligo/event/*"></a> elements
            for _a in _td.find_all('a', href=True):

                # check names are in correct format
                if _a['href'].lower().startswith(f'/ligo/event'):

                    # check for search pattern
                    m = TNS_LIGO_Q3C_SUPPORTED_EVENTS.search(_a['href'])
                    if m and f'{m.group().strip()}' not in self.__aka:
                        self.__aka.append(f'{m.group()}')

    # +
    # method: get_attributes()
    # -
    def get_attributes(self, _table=None):
        """ get table attributes """

        # check input(s)
        self.__columns, self.__headers, self.__rows = 0, [], 0
        if _table is None or not hasattr(_table, f'find_all'):
            return

        # get headers
        for _th in _table.find_all('th'):
            if f'{_th.text.strip()}' not in self.__headers:
                self.__headers.append(f'{_th.text.strip()}')

        # get number of columns
        self.__columns = len(self.__headers)

        # get number of rows
        for row in _table.find_all('tr'):
            if len(row.find_all('td')) > 0:
                self.__rows += 1

        if self.__verbose:
            _log.debug(f"self.__columns={self.__columns}")
            _log.debug(f"self.__headers={self.__headers}")
            _log.debug(f"self.__rows={self.__rows}")

    # +
    # method: get_before()
    # -
    def get_before(self, _table=None):
        """ gets links labelled as before the event """

        # check input(s)
        self.__before= []
        if _table is None or not hasattr(_table, f'find_all'):
            return

        # find <td class="cell-downloads"></td> elements
        for _td in _table.find_all('td', attrs={'class': 'cell-downloads'}):

            # find <a href="/ligo/event/*"></a> elements
            for _a in _td.find_all('a', href=True):

                # check names are in correct format
                if _a['href'].strip().lower().startswith(f'http') and _a['href'].strip().lower().endswith(self.__schema):

                    # check for search pattern
                    if f'before' in _a['href'].strip().lower() and f"{_a['href'].strip()}" not in self.__before:
                        self.__before.append(f"{_a['href'].strip()}")

    # +
    # method: get_dates()
    # -
    def get_dates(self, _table=None):
        """ get dates of events """

        # check input(s)
        self.__dates = []
        if _table is None or not hasattr(_table, f'find_all'):
            return

        # find <td class="cell-date"></td> elements
        for _td in _table.find_all('td', attrs={'class': 'cell-date'}):
            if f'{_td.text.strip()}' not in self.__dates:
                self.__dates.append(f'{_td.text.strip()}')

    # +
    # method: get_events()
    # -
    def get_events(self, _table=None):
        """ get all data associated with events """

        # check input(s)
        if _table is None or not hasattr(_table, f'find_all'):
            return {}

        # get data
        self.get_attributes(_table)
        self.get_after(_table)
        self.get_aka(_table)
        self.get_before(_table)
        self.get_dates(_table)
        self.get_names(_table)

        # message(s)
        if self.__verbose:
            _log.debug(f"self.__after={self.dump(self.__after, ' ')}, len={len(self.__after)}")
            _log.debug(f"self.__aka={self.dump(self.__aka, ' ')}, len={len(self.__aka)}")
            _log.debug(f"self.__before={self.dump(self.__before, ' ')}, len={len(self.__before)}")
            _log.debug(f"self.__dates={self.dump(self.__dates, ' ')}, len={len(self.__dates)}")
            _log.debug(f"self.__names={self.dump(self.__names, ' ')}, len={len(self.__names)}")

        # return - this is horrible, it really needs splitting up somehow
        _ans = {}
        for _i in range(self.__rows):
            if self.__verbose:
                _log.debug(f"scraping row {_i}")

            # get before data from json
            if self.__schema == 'json':
                _before = self.scrape_json(self.__before[_i])
                if _before is not None:
                    for _bk, _bv in _before.items():
                        _name = f"{self.__names[_i]}-{_bk.strip()}"
                        _suffix = f'{get_unique_hash()}'[:6]
                        if f'{_name}' in _ans:
                            _name = f'{_name}-{_suffix}'
                        if self.__verbose:
                            _log.debug(f"Creating new dictionary element, _ans['{_name}']")
                        _ans[f'{_name}'] = {
                            'name': f'{_name}',
                            'name_prefix': _bv['name_prefix'] if 'name_prefix' in _bv else '',
                            'name_suffix': _suffix if f'{_suffix}' in _name else '',
                            'ra': float(_bv['ra']) if 'ra' in _bv else math.nan,
                            'dec': float(_bv['dec']) if 'dec' in _bv else math.nan,
                            'transient_type': _bv['type'] if 'type' in _bv else '',
                            'discovery_date': _bv['discoverydate'] if 'discoverydate' in _bv else '',
                            'discovery_mag': float(_bv['discoverymag']) if 'discoverymag' in _bv else math.nan,
                            'filter_name': _bv['filter'] if 'filter' in _bv else '',
                            'source_group': _bv['source_group'] if 'source_group' in _bv else '',
                            'probability': float(_bv['probability']) if 'probability' in _bv else math.nan,
                            'sigma': float(_bv['sigma']) if 'sigma' in _bv else math.nan,
                            'gw_aka': self.__aka[_i],
                            'gw_event': self.__names[_i],
                            'gw_date': self.__dates[_i],
                            'before': True
                        }
                        # if self.__verbose:
                        #     _log.debug(f"_ans['{_name}']={_ans[_name]}")

            # get before data from tsv
            elif self.__schema == 'tsv':
                _before = self.scrape_tsv(self.__before[_i])
                if _before is not None:
                    _before = _before.split('\n')
                    _hdr = _before[0].split('\t')
                    for _e in _before[1:]:
                        _before_entry = dict(zip(_hdr, _e.split('\t')))
                        if len(_hdr) != len(_before_entry):
                            continue
                        _name = f"{self.__names[_i]}-{_before_entry['name'].strip()}"
                        _suffix = f'{get_unique_hash()}'[:6]
                        if f'{_name}' in _ans:
                            _name = f'{_name}-{_suffix}'
                        if self.__verbose:
                            _log.debug(f"Creating new dictionary element, _ans['{_name}']")
                        _ans[f'{_name}'] = {
                            'name': f'{_name}',
                            'name_prefix': _before_entry['name_prefix'] if 'name_prefix' in _before_entry else '',
                            'name_suffix': _suffix if f'{_suffix}' in _name else '',
                            'ra': float(_before_entry['ra']) if 'ra' in _before_entry else math.nan,
                            'dec': float(_before_entry['dec']) if 'dec' in _before_entry else math.nan,
                            'transient_type': _before_entry['type'] if 'type' in _before_entry else '',
                            'discovery_date': _before_entry['discoverydate'] if 'discoverydate' in _before_entry else '',
                            'discovery_mag': float(_before_entry['discoverymag']) if 'discoverymag' in _before_entry else math.nan,
                            'filter_name': _before_entry['filter'] if 'filter' in _before_entry else '',
                            'source_group': _before_entry['source_group'] if 'source_group' in _before_entry else '',
                            'probability': float(_before_entry['probability']) if 'probability' in _before_entry else math.nan,
                            'sigma': float(_before_entry['sigma']) if 'sigma' in _before_entry else math.nan,
                            'gw_aka': self.__aka[_i],
                            'gw_event': self.__names[_i],
                            'gw_date': self.__dates[_i],
                            'before': True
                        }
                        # if self.__verbose:
                        #     _log.debug(f"_ans['{_name}']={_ans[_name]}")

   
            # get after data from json
            if self.__schema == 'json':
                _after = self.scrape_json(self.__after[_i])
                if _after is not None:
                    for _ak, _av in _after.items():
                        _name = f"{self.__names[_i]}-{_ak.strip()}"
                        _suffix = f'{get_unique_hash()[:6]}'
                        if f'{_name}' in _ans:
                            _name = f'{_name}-{_suffix}'
                        if self.__verbose:
                            _log.debug(f"Creating new dictionary element, _ans['{_name}']")
                        _ans[f'{_name}'] = {
                            'name': f'{_name}',
                            'name_prefix': _av['name_prefix'] if 'name_prefix' in _av else '',
                            'name_suffix': _suffix if f'{_suffix}' in _name else '',
                            'ra': float(_av['ra']) if 'ra' in _av else math.nan,
                            'dec': float(_av['dec']) if 'dec' in _av else math.nan,
                            'transient_type': _av['type'] if 'type' in _av else '',
                            'discovery_date': _av['discoverydate'] if 'discoverydate' in _av else '',
                            'discovery_mag': float(_av['discoverymag']) if 'discoverymag' in _av else math.nan,
                            'filter_name': _av['filter'] if 'filter' in _av else '',
                            'source_group': _av['source_group'] if 'source_group' in _av else '',
                            'probability': float(_av['probability']) if 'probability' in _av else math.nan,
                            'sigma': float(_av['sigma']) if 'sigma' in _av else math.nan,
                            'gw_aka': self.__aka[_i],
                            'gw_event': self.__names[_i],
                            'gw_date': self.__dates[_i],
                            'before': False
                        }
                        # if self.__verbose:
                        #     _log.debug(f"_ans['{_name}']={_ans[_name]}")

            # get after data from tsv
            elif self.__schema == 'tsv':
                _after = self.scrape_tsv(self.__after[_i])
                if _after is not None:
                    _after = _after.split('\n')
                    _hdr = _after[0].split('\t')
                    for _e in _after[1:]:
                        _after_entry = dict(zip(_hdr, _e.split('\t')))
                        if len(_hdr) != len(_after_entry):
                            continue
                        _name = f"{self.__names[_i]}-{_after_entry['name'].strip()}"
                        _suffix = f'{get_unique_hash()[:6]}'
                        if f'{_name}' in _ans:
                            _name = f'{_name}-{_suffix}'
                        if self.__verbose:
                            _log.debug(f"Creating new dictionary element, _ans['{_name}']")
                        _ans[f'{_name}'] = {
                            'name': f'{_name}',
                            'name_prefix': _after_entry['name_prefix'] if 'name_prefix' in _after_entry else '',
                            'name_suffix': _suffix if f'{_suffix}' in _name else '',
                            'ra': float(_after_entry['ra']) if 'ra' in _after_entry else math.nan,
                            'dec': float(_after_entry['dec']) if 'dec' in _after_entry else math.nan,
                            'transient_type': _after_entry['type'] if 'type' in _after_entry else '',
                            'discovery_date': _after_entry['discoverydate'] if 'discoverydate' in _after_entry else '',
                            'discovery_mag': float(_after_entry['discoverymag']) if 'discoverymag' in _after_entry else math.nan,
                            'filter_name': _after_entry['filter'] if 'filter' in _after_entry else '',
                            'source_group': _after_entry['source_group'] if 'source_group' in _after_entry else '',
                            'probability': float(_after_entry['probability']) if 'probability' in _after_entry else math.nan,
                            'sigma': float(_after_entry['sigma']) if 'sigma' in _after_entry else math.nan,
                            'gw_aka': self.__aka[_i],
                            'gw_event': self.__names[_i],
                            'gw_date': self.__dates[_i],
                            'before': False
                        }
                        # if self.__verbose:
                        #     _log.debug(f"_ans['{_name}']={_ans[_name]}")

        # return
        return _ans

    # +
    # method: get_names()
    # -
    def get_names(self, _table=None):
        """ get names of events """

        # check input(s)
        self.__names = []
        if _table is None or not hasattr(_table, f'find_all'):
            return

        # find <td class="cell-name"></td> elements
        for _td in _table.find_all('td', attrs={'class': 'cell-name'}):

            # find <a href="/ligo/event/*"></a> elements
            for _a in _td.find_all('a', href=True):

                # check names are in correct format
                # if _a['href'].lower().startswith(f'/ligo/event') and f'{_a.text.strip()}' not in self.__names:
                if _a['href'].lower().startswith(f'/ligo/event'):
                    self.__names.append(f'{_a.text.strip()}')

    # +
    # method: get_request()
    # -
    def get_request(self):
        """ get data from web-site """

        # noinspection PyBroadException
        try:
            if self.__verbose:
                _log.debug(f"Calling requests.get('{self.__url}', auth='{self.__username, self.__password}')")
            _requests = requests.get(self.__url, auth=(self.__username, self.__password))
            if self.__verbose:
                _log.debug(f"Called requests.get('{self.__url}', auth='{self.__username, self.__password}'), _requests={_requests}")

            if _requests.status_code == 200:
                return _requests
            else:
                if self.__verbose:
                    _log.error(f"Bad status code ({_requests.status_code})  calling requests.get('{self.__url}', auth='{self.__username, self.__password}')")
                return None

        except Exception as e:
            if self.__verbose:
                _log.error(f"Failed calling requests.get('{self.__url}', auth='{self.__username, self.__password}'), error={e}")
            return None

    # +
    # method: scrape_json()
    # -
    def scrape_json(self, _url=''):
        """ get json data from web-site """

        # return data
        if _url.strip().lower().startswith(f'http') and _url.strip().lower().endswith('json'):
            self.__url = _url
            self.__response = self.get_request()
            if self.__response is not None:
                return self.__response.json()
        else:
            return None

    # +
    # method: scrape_tsv()
    # -
    def scrape_tsv(self, _url=''):
        """ get tsv data from web-site """

        # return data
        if _url.strip().lower().startswith(f'http') and _url.strip().lower().endswith('tsv'):
            self.__url = _url
            self.__response = self.get_request()
            if self.__response is not None:
                return self.__response.content.decode()
        else:
            return None

    # +
    # method: scrape_ligo_q3c_events()
    # -
    def scrape_ligo_q3c_events(self):
        """ scrape web-site for ligo_q3c events """

        # get data
        self.__response = self.get_request()
        if self.__verbose:
            _log.debug(f'self.__response={self.__response}')

        # check response
        if self.__response is None:
            return []

        # set up encoding
        _http_encoding = self.__response.encoding if 'charset' in self.__response.headers.get(
            'content-type', '').lower() else None
        _html_encoding = EncodingDetector.find_declared_encoding(self.__response.content, is_html=True)

        # return data
        try:
            self.__soup = BeautifulSoup(self.__response.text, features='html5lib', 
                                        from_encoding=(_html_encoding or _http_encoding))
            return [self.get_events(_t) for _t in self.__soup.find_all('table', attrs={'class': 'ligo-alerts-table'})]
        except Exception as e:
            if self.__verbose:
                _log.error(f'Failed to get soup from self.__response, error={e}')
            return []


# +
# function: get_unique_hash()
# -
def get_unique_hash():
    _date = datetime.now().isoformat()
    return hashlib.sha256(_date.encode('utf-8')).hexdigest()


# +
# function: ligo_q3c_scrape()
# -
def ligo_q3c_scrape(url=DEFAULT_URL, credentials=DEFAULT_CREDENTIALS, schema=DEFAULT_SCHEMA, verbose=False, force=False, dry_run=False):

    # check input(s)
    verbose = verbose if isinstance(verbose, bool) else False
    force = force if isinstance(force, bool) else False
    dry_run = dry_run if isinstance(dry_run, bool) else False

    if (not isinstance(url, str)) or (url.strip() == '') or (not args.url.strip().lower().startswith(f'http')):
        if verbose:
            _log.critical(f'Invalid input, url={url}')
        return
    if (not isinstance(credentials, str)) or (credentials.strip() == '') or (':' not in args.credentials):
        if verbose:
            _log.critical(f'Invalid input, credentials={credentials}')
        return
    if (not isinstance(schema, str)) or (schema.strip() == '') or (args.schema.strip().lower() not in TNS_LIGO_Q3C_SUPPORTED_SCHEMAS):
        if verbose:
            _log.critical(f'Invalid input, schema={schema}')
        return

    # instantiate the class
    try:
        _ltp = LigoQ3cTableParser(url, credentials, schema, verbose)
    except Exception as e:
        _log.error(f"Failed instantiating LigoQ3cTableParser('{url}', '{credentials}', '{schema}', {verbose}), error={e}")
        return

    # scrape the web site
    try:
        _data = _ltp.scrape_ligo_q3c_events()
    except Exception as e:
        if verbose:
            _log.error(f'Failed scraping {url}, error={e}')
        return

    # connect to database
    try:
        engine = create_engine(f'postgresql+psycopg2://{SASSY_DB_USER}:{SASSY_DB_PASS}@'
                               f'{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}')
        get_session = sessionmaker(bind=engine)
        session = get_session()
    except Exception as e:
        if verbose:
            _log.error(f'Failed to connect to database, error={e}')
        return

    # create database records from scraped data
    for _d in _data:
        for _ek, _ev in _d.items():

            # get name of object
            _name = ''
            if 'name_suffix' in _ev and _ev['name_suffix'].strip() != '':
                _name = _ev['name'][:-7] if 'name' in _ev else ''
            else:
                _name = _ev['name'] if 'name' in _ev else ''
            _name = f'{_name.strip()}'
            if f'{_name}' == '':
                continue

            # delete record if it exists and we want to force an update
            _rec = None
            try:
                _rec = session.query(LigoQ3cRecord).filter_by(name=f'{_name}').first()
            except Exception as e:
                _rec = None

            if force:
                if _rec is not None:
                    if dry_run:
                        if verbose:
                            _log.info(f"Dry-Run>> deleting record for {_name} from database")
                    else:
                        try:
                            if verbose:
                                _log.info(f"Deleting record for {_name} from database")
                            session.delete(_rec)
                            session.commit()
                            if verbose:
                                _log.info(f"Deleted record for {_name} from database")
                        except Exception as e:
                            session.rollback()
                            session.commit()
                            if verbose:
                                _log.error(f"Failed to delete record for {_name} from database, error={e}")
            else:
                if _rec is not None:
                    if dry_run:
                        if verbose:
                            _log.info(f"Dry-Run>> ignoring record for {_name} from database")
                    else:
                        if verbose:
                            _log.warning(f"Ignoring record {_name}, duplicate in database (use --force to override)")
                        continue
    
            # create new record
            _ligo_q3c = None
            try:
                _ligo_q3c = LigoQ3cRecord(
                    name = f'{_name}',
                    name_prefix = _ev['name_prefix'] if 'name_prefix' in _ev else '',
                    name_suffix = _ev['name_suffix'] if 'name_suffix' in _ev else '',
                    ra = float(_ev['ra']) if 'ra' in _ev else math.nan,
                    dec = float(_ev['dec']) if 'dec' in _ev else math.nan,
                    transient_type = _ev['transient_type'] if ('transient_type' in _ev and _ev['transient_type'].lower() != 'null') else '',
                    discovery_date = _ev['discovery_date'] if 'discovery_date' in _ev else '',
                    discovery_mag = float(_ev['discovery_mag']) if 'discovery_mag' in _ev else math.nan,
                    filter_name = _ev['filter_name'] if 'filter_name' in _ev else '',
                    source_group = _ev['source_group'] if 'source_group' in _ev else '',
                    probability = float(_ev['probability']) if 'probability' in _ev else math.nan,
                    sigma = float(_ev['sigma']) if 'sigma' in _ev else math.nan,
                    gw_aka = _ev['gw_aka'] if 'gw_aka' in _ev else '',
                    gw_date = _ev['gw_date'] if 'gw_date' in _ev else '',
                    gw_event = _ev['gw_event'] if 'gw_event' in _ev else '',
                    before = bool(_ev['before']) if 'before' in _ev else False)
            except Exception as e:
                _ligo_q3c = None
                if verbose:
                    _log.error(f"Failed to create LigoQ3cRecord for {_ev['name']}, error={e}")

            # update database with results
            if _ligo_q3c is not None:
                if dry_run:
                    if verbose:
                        _ligo_q3c.id = -1
                        _log.info(f"Dry-Run>> _ligo_q3c={_ligo_q3c.serialized()}")
                    if verbose:
                        _log.info(f"Dry-Run>> inserting record for {_name} into database")
                else:
                    try:
                        if verbose:
                            _log.info(f"Inserting record for {_name} into database")
                        session.add(_ligo_q3c)
                        session.commit()
                        if verbose:
                            _log.info(f"Inserted record for {_name} into database")
                    except Exception as e:
                        session.rollback()
                        session.commit()
                        if verbose:
                            _log.error(f"Failed to insert record for {_name} into database, error={e}")

    # close
    session.close()
    session.close_all()


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s)
    _parser = argparse.ArgumentParser(description=f'Ingest LIGO_Q3C events from TNS',
                                      formatter_class=argparse.RawTextHelpFormatter)
    _parser.add_argument(f'-u', f'--url', default=f'{DEFAULT_URL}',
                         help=f"""server url=<str>, defaults to %(default)s""")
    _parser.add_argument(f'-c', f'--credentials', default=f'{DEFAULT_CREDENTIALS}',
                         help=f"""server credentials=<str>:<str>, defaults to '%(default)s'""")
    _parser.add_argument(f'--dry-run', default=False, action='store_true',
                         help='if present, show actions')
    _parser.add_argument(f'--force', default=False, action='store_true',
                         help='if present, force updates by first deleting existing records')
    _parser.add_argument(f'-s', f'--schema', default=DEFAULT_SCHEMA,
                         help=f"""Input schema=<str>, choice of 'json' or 'tsv'""")
    _parser.add_argument(f'--verbose', default=False, action='store_true',
                         help='if present, produce more verbose output')
    args = _parser.parse_args()

    # execute
    if args:
        ligo_q3c_scrape(args.url, args.credentials, args.schema, bool(args.verbose), bool(args.force), bool(args.dry_run))
    else:
        _log.critical(f'Insufficient command line arguments specified\nUse: python {sys.argv[0]} --help')
