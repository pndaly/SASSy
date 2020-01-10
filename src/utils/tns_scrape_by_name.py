#!/usr/bin/env python3


# +
# import(s)
# -
import argparse
import math
import hashlib
import os
import requests
import sys
import time
import warnings

from astropy.coordinates import Angle
from astropy.coordinates import SkyCoord
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
from datetime import datetime
from datetime import timedelta
from src.models.tns import TnsRecord
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# noinspection PyUnresolvedReferences
from utils import UtilsLogger


# +
# suppress all warnings!
# -
warnings.filterwarnings('ignore')


# +
# logging
# -
_log = UtilsLogger('TnsScrapeByName').logger


# +
# constant(s)
# -
SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PORT = os.getenv('SASSY_DB_PORT', None)


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


# noinspection PyUnresolvedReferences
def coord_from_sky(_ra='', _dec=''):
    if not isinstance(_ra, str) or _ra.strip() == '':
        return math.nan, math.nan
    if not isinstance(_dec, str) or _dec.strip() == '':
        return math.nan, math.nan
    _coord = SkyCoord(f'{_ra} {_dec}', unit=(u.hourangle, u.deg))
    return _coord.ra.degree, _coord.dec.degree


def get_date_time(offset=0):
    """ return local time string like YYYY-MM-DDThh:mm:ss.ssssss with/without offset """
    return (datetime.now() + timedelta(days=offset)).isoformat()


def get_date_utctime(offset=0):
    """ return UTC time string like YYYY-MM-DDThh:mm:ss.ssssss with/without offset """
    return (datetime.utcnow() + timedelta(days=offset)).isoformat()


def get_unique_hash():
    _date = get_date_time(0)
    return hashlib.sha256(_date.encode('utf-8')).hexdigest()


# +
# default(s)
# -
DEFAULT_BASE_URL = f'https://wis-tns.weizmann.ac.il'
DEFAULT_CREDENTIALS = f':'
DEFAULT_LOGIN_URL = f'{DEFAULT_BASE_URL}/user'
DEFAULT_NUMBER = 1
DEFAULT_SEARCH_URL = f"{DEFAULT_BASE_URL}/search"
DEFAULT_UNITS = ['Days', 'Months', 'Years']
DEFAULT_UNIT = DEFAULT_UNITS[-1]


# +
# __doc__ string
# -
__doc__ = """
    % python3 tns_scrape_by_name.py --help
"""


# +
# class: TnsTableParser()
# -
# noinspection PyBroadException
class TnsTableParser(object):

    # +
    # method: __init__()
    # -
    def __init__(self, url=DEFAULT_LOGIN_URL, credentials=DEFAULT_CREDENTIALS, name='', exact=False, verbose=False):

        # get input(s)
        self.url = url
        self.credentials = credentials
        self.name = name
        self.exact = exact
        self.verbose = verbose

        # private variable(s)
        self.__ans = None
        self.__response = None
        self.__soup = None
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
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name if isinstance(name, str) else ''

    @property
    def exact(self):
        return self.__exact

    @exact.setter
    def exact(self, exact):
        self.__exact = exact if isinstance(exact, bool) else False

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
            _res += f'self.__name = {self.__name}, '
            _res += f'self.__exact = {self.__exact}, '
            _res += f'self.__verbose = {self.__verbose}, '
            _res += f'self.__response = {self.__response}, '
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
                _requests = self.__session.get(url=self.__url,)
            else:
                _requests = requests.get(url=self.__url, auth=(self.__username, self.__password),)
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

        _rows = list(set().union(_evens, _odds))
        if self.__verbose:
            _log.info(f"len(_rows)={len(_rows)}")

        # scrape each row which should look like this
        for _e in _rows:

            # initialize a dictionary
            if self.__verbose:
                _log.info(f"scraping row {_e}")
            _ans_tmp = {}

            try:
                # <td class="cell-id">6565</td>
                _ans_tmp['tns_id'] = _e.find('td', attrs={'class': 'cell-id'}).text.strip()
            except Exception:
                _ans_tmp['tns_id'] = ''

            try:
                # <td class="cell-name"><a href="/object/2015z">SN 2015Z</a></td>
                _ans_tmp['tns_name'] = (_e.find('td', attrs={'class': 'cell-name'})).find('a').text.strip()
                _link = (_e.find('td', attrs={'class': 'cell-name'})).find('a', href=True)['href']
                _ans_tmp['tns_link'] = f"{DEFAULT_BASE_URL}{_link}"
            except Exception:
                _ans_tmp['tns_name'] = ''
                _ans_tmp['tns_link'] = ''

            try:
                # <td class="cell-reps">1<a class="cert-open" href="/object/2019oel/discovery-cert" rel="43659"></a>
                # <a class="at-reps-open clearfix" href="/%23" rel="43659"></a></td>
                _cert = (_e.find('td', attrs={'class': 'cell-reps'})).find('a', href=True)['href']
                _ans_tmp['tns_cert'] = f"{DEFAULT_BASE_URL}{_cert}"
            except Exception:
                _ans_tmp['tns_cert'] = ''

            try:
                # <td class="cell-class"></td>
                _ans_tmp['tns_class'] = _e.find('td', attrs={'class': 'cell-class'}).text.strip()
            except Exception:
                _ans_tmp['tns_class'] = ''

            try:
                # <td class="cell-ra">17:18:23.982</td>
                _ans_tmp['ra'] = _e.find('td', attrs={'class': 'cell-ra'}).text.strip()
            except Exception:
                _ans_tmp['ra'] = ''

            try:
                # <td class="cell-decl">-31:04:29.63</td>
                _ans_tmp['decl'] = _e.find('td', attrs={'class': 'cell-decl'}).text.strip()
            except Exception:
                _ans_tmp['decl'] = ''

            try:
                # <td class="cell-ot_name"></td>
                _ans_tmp['ot_name'] = _e.find('td', attrs={'class': 'cell-ot_name'}).text.strip()
            except Exception:
                _ans_tmp['ot_name'] = ''

            try:
                # <td class="cell-redshift"></td>
                _ans_tmp['redshift'] = _e.find('td', attrs={'class': 'cell-redshift'}).text.strip()
            except Exception:
                _ans_tmp['redshift'] = ''

            try:
                # <td class="cell-hostname"></td>
                _ans_tmp['hostname'] = _e.find('td', attrs={'class': 'cell-hostname'}).text.strip()
            except Exception:
                _ans_tmp['hostname'] = ''

            try:
                # <td class="cell-host_redshift"></td>
                _ans_tmp['host_redshift'] = _e.find('td', attrs={'class': 'cell-host_redshift'}).text.strip()
            except Exception:
                _ans_tmp['host_redshift'] = ''

            try:
                # <td class="cell-source_group_name">ATLAS</td>
                _ans_tmp['source_group'] = _e.find('td', attrs={'class': 'cell-source_group_name'}).text.strip()
            except Exception:
                _ans_tmp['source_group'] = ''

            try:
                # <td class="cell-classifying_source_group_name"></td>
                _ans_tmp['classifying_group'] = _e.find('td',
                                                        attrs={'class': 'cell-classifying_source_group_name'}).text.strip()
            except Exception:
                _ans_tmp['classifying_group'] = ''

            try:
                # <td class="cell-groups">ATLAS</td>
                _ans_tmp['groups'] = _e.find('td', attrs={'class': 'cell-groups'}).text.strip()
            except Exception:
                _ans_tmp['groups'] = ''

            try:
                # <td class="cell-internal_name">ATLAS19svo</td>
                _ans_tmp['internal_name'] = _e.find('td', attrs={'class': 'cell-internal_name'}).text.strip()
            except Exception:
                _ans_tmp['internal_name'] = ''

            try:
                # <td class="cell-discovering_instrument_name">ATLAS1 - ACAM1</td>
                _ans_tmp['instrument_name'] = _e.find('td', attrs={'class': 'cell-discovering_instrument_name'}).text.strip()
            except Exception:
                _ans_tmp['instrument_name'] = ''

            try:
                # <td class="cell-classifing_instrument_name"></td>
                _ans_tmp['classifying_instrument'] = _e.find('td',
                                                             attrs={'class': 'cell-classifing_instrument_name'}).text.strip()
            except Exception:
                _ans_tmp['classifying_instrument'] = ''

            try:
                # <td class="cell-isTNS_AT">Y</td>
                _ans_tmp['isTNS_AT'] = _e.find('td', attrs={'class': 'cell-isTNS_AT'}).text.strip()
            except Exception:
                _ans_tmp['isTNS_AT'] = ''

            try:
                # <td class="cell-public">Y</td>
                _ans_tmp['public'] = _e.find('td', attrs={'class': 'cell-public'}).text.strip()
            except Exception:
                _ans_tmp['public'] = ''

            try:
                # <td class="cell-end_prop_period"></td>
                _ans_tmp['end_prop_period'] = _e.find('td', attrs={'class': 'cell-end_prop_period'}).text.strip()
            except Exception:
                _ans_tmp['end_prop_period'] = ''

            try:
                # <td class="cell-spectra_count"></td>
                _ans_tmp['spectra_count'] = _e.find('td', attrs={'class': 'cell-spectra_count'}).text.strip()
            except Exception:
                _ans_tmp['spectra_count'] = ''

            try:
                # <td class="cell-discoverymag">17.775</td>
                _ans_tmp['mag'] = _e.find('td', attrs={'class': 'cell-discoverymag'}).text.strip()
            except Exception:
                _ans_tmp['mag'] = ''

            try:
                # <td class="cell-disc_filter_name">orange-ATLAS</td>
                _ans_tmp['filter'] = _e.find('td', attrs={'class': 'cell-disc_filter_name'}).text.strip()
            except Exception:
                _ans_tmp['filter'] = ''

            try:
                # <td class="cell-discoverydate">2019-08-22 06:59:02</td>
                _ans_tmp['date'] = _e.find('td', attrs={'class': 'cell-discoverydate'}).text.strip()
            except Exception:
                _ans_tmp['date'] = ''

            try:
                # <td class="cell-discoverer">ATLAS_Bot1</td>
                _ans_tmp['discoverer'] = _e.find('td', attrs={'class': 'cell-discoverer'}).text.strip()
            except Exception:
                _ans_tmp['discoverer'] = ''

            try:
                # <td class="cell-remarks"></td>
                _ans_tmp['remarks'] = _e.find('td', attrs={'class': 'cell-remarks'}).text.strip()
            except Exception:
                _ans_tmp['remarks'] = ''

            try:
                # <td class="cell-sources"></td>
                _ans_tmp['sources'] = _e.find('td', attrs={'class': 'cell-sources'}).text.strip()
            except Exception:
                _ans_tmp['sources'] = ''

            try:
                # <td class="cell-bibcode"></td>
                _ans_tmp['bibcode'] = _e.find('td', attrs={'class': 'cell-bibcode'}).text.strip()
            except Exception:
                _ans_tmp['bibcode'] = ''

            try:
                # _log.info(f"_ans_tmp['bibcode']={_ans_tmp['bibcode']}")
                _ans_tmp['catalogs'] = _e.find('td', attrs={'class': 'cell-ext_catalogs'}).text.strip()
            except Exception:
                _ans_tmp['catalogs'] = ''


            # add it to the result(s)
            if _ans_tmp['tns_id'] != '' and _ans_tmp['tns_name'] != '' and _ans_tmp['ra'] != '' and _ans_tmp['decl'] != '':
                if self.__verbose:
                    _log.debug(f"scraped row {_ans_tmp}")
                self.__ans.append(_ans_tmp)
            else:
                if self.__verbose:
                    _log.debug(f"ignoring {_ans_tmp}")


    # +
    # method: get_soup()
    # -
    def get_soup(self, _page=0):
        """ scrape web-site page """

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
        if self.__exact:
            self.__url = f'{DEFAULT_SEARCH_URL}?name={self.__name}&name_like="1"'
        else:
            self.__url = f'{DEFAULT_SEARCH_URL}?name={self.__name}&name_like="0"'

        # get soup
        self.get_soup()
        if self.__verbose:
            # _log.debug(f'self.__soup={self.__soup}')
            _log.debug(f'type(self.__soup)={type(self.__soup)}')

        # get max number of results by scraping
        if self.__soup is not None:
            _div = self.__soup.find_all('div', attrs={'class': 'count rsults'})
            if self.__verbose:
                _log.debug(f'_div={_div}')
            if _div is not None or _div is not []:
                _ems = [_e.find_all('em', attrs={'class': 'placeholder'}) for _e in _div][0]
                if self.__verbose:
                    _log.debug(f'_ems={_ems}')
                self.__total = int(_ems[-1].text)
                if self.__verbose:
                    _log.debug(f'self.__total={self.__total}')
        else:
            return self.__total, self.__ans

        # get record(s) for page 0
        self.get_records()

        # return result
        if self.__verbose:
            _log.debug(f'self.__total = {self.__total}')
            _log.debug(f'len(self.__ans) = {len(self.__ans)}')
        return self.__total, self.__ans


# +
# function: tns_scrape_by_name()
# -
# noinspection PyBroadException
def tns_scrape_by_name(login=DEFAULT_LOGIN_URL, credentials=DEFAULT_CREDENTIALS, name='',
                 exact=False, verbose=False, force=False):

    # check input(s)
    login = login if (isinstance(login, str) and login.strip() != '' and
                      login.strip().lower().startswith(f'http')) else DEFAULT_LOGIN_URL
    credentials = credentials if (isinstance(credentials, str) and credentials.strip() != ''
                                  and ':' in credentials.strip()) else DEFAULT_CREDENTIALS
    name = name if isinstance(name, str) else ''
    exact = exact if isinstance(exact, bool) else False
    verbose = verbose if isinstance(verbose, bool) else False
    force = force if isinstance(force, bool) else False

    # instantiate the class
    try:
        _log.info(f"Instantiating TnsTableParser('{login}', '{credentials}', '{name}', {exact}, {verbose})")
        _ttp = TnsTableParser(login, credentials, name, exact, verbose)
        _log.info(f"Instantiated TnsTableParser('{login}', '{credentials}', '{name}', {exact}, {verbose}) OK")
    except Exception as e:
        _log.error(f"Failed instantiating TnsTableParser("
                   f"'{login}', '{credentials}', '{name}', '{exact}', {verbose}), error={e}")
        return

    # scrape the web site
    try:
        _log.info(f'Scraping pages')
        _total, _data = _ttp.scrape_tns_pages()
        _log.info(f'Scraped pages OK')
    except Exception as e:
        if verbose:
            _log.error(f'Failed scraping pages, name={name}, error={e}')
        return

    if verbose:
        _log.info(f'_total={_total}')
        _log.info(f'len(_data)={len(_data)}')

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
    for _e in _data:

        # report
        if verbose:
            _log.info(f'_e = {_e}')

        # conversion(s) 
        _tns_name = _e.get('tns_name', 'unknown')
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

         
        if _e.get('date', '') == '':
            _e['date'] = '1900-01-01 00:00:00.0'

        # does record already exist?
        _rec = None
        if _tns_id > 0:
            try:
                _rec = session.query(TnsRecord).filter_by(tns_id=_tns_id).first()
            except Exception:
                _rec = None
            if _rec is not None:
              if force:
                    try:
                        _log.info(f"Deleting record tns_id={_tns_id} tns_name={_tns_name} from database")
                        session.delete(_rec)
                        session.commit()
                        _log.info(f"Deleted record tns_id={_tns_id} tns_name={_tns_name} from database")
                    except Exception as e:
                        _log.error(f"Failed to delete record tns_id={_tns_id} tns_name={_tns_name} from database, error={e}")
                        session.rollback()
                        session.commit()
              else:
                  continue

        # create record
        _tns = None
        #if '0000-00-00' in _e['date']:
        #    _log.info(f"Ignoring record {_e['tns_name']} with null discovery date")
        #else:
        _tns = TnsRecord(tns_id=_tns_id, tns_name=_e['tns_name'], tns_link=_e['tns_link'],
                         ra=_ra, dec=_dec, redshift=_z, discovery_date=_e['date'], discovery_mag=_mag,
                         discovery_instrument=_e['instrument_name'], filter_name=_e['filter'],
                         tns_class=_e['tns_class'], host=_e['hostname'], host_z=_h_z,
                         source_group=_e['source_group'], alias=_e['internal_name'], certificate=_e['tns_cert'])

        # update database with results
        if _tns is not None:
            _log.info(f"Record = {_tns.serialized()}")
            try:
                _log.info(f"Inserting tns_id={_tns_id} tns_name={_tns_name}")
                session.add(_tns)
                session.commit()
                _log.info(f"Inserted tns_id={_tns_id} tns_name={_tns_name}")
            except Exception as e:
                _log.error(f"Failed inserting tns_id={_tns_id} tns_name={_tns_name}, error={e}")
                session.rollback()
                session.commit()

    # close
    session.close()
    session.close_all()


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s)
    _parser = argparse.ArgumentParser(description=f'Ingest TNS events from TNS',
                                      formatter_class=argparse.RawTextHelpFormatter)
    _parser.add_argument(f'-l', f'--login', default=f'{DEFAULT_BASE_URL}/login',
                         help=f"""URL url=<str>, defaults to %(default)s""")
    _parser.add_argument(f'-c', f'--credentials', default=f'{DEFAULT_CREDENTIALS}',
                         help=f"""server credentials=<str>:<str>, defaults to '%(default)s'""")
    _parser.add_argument(f'-n', f'--name', default='',
                         help=f"""Name <str>, defaults to %(default)s""")
    _parser.add_argument(f'--exact', default=False, action='store_true',
                         help='if present, name value must be an exact match')
    _parser.add_argument(f'--force', default=False, action='store_true',
                         help='if present, force updates by first deleting existing records')
    _parser.add_argument(f'--verbose', default=False, action='store_true',
                         help='if present, produce more verbose output')
    args = _parser.parse_args()

    # execute
    if args:
        tns_scrape_by_name(args.login, args.credentials, args.name, bool(args.exact), bool(args.verbose), bool(args.force))
    else:
        _log.critical(f'Insufficient command line arguments specified\nUse: python {sys.argv[0]} --help')
