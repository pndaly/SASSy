#!/usr/bin/env python3


# +
# import(s)
# -
from astroplan import download_IERS_A
from astropy.utils import iers
from astropy.utils.data import clear_download_cache


# +
# function: get_iers():
# -
# noinspection PyBroadException
def get_iers(url='https://datacenter.iers.org/data/9/finals2000A.all'):

    # check input(s)
    if not isinstance(url, str) or url.strip() == '':
        raise Exception(f'invalid input, url={url}')
    if not (url.strip().lower().startswith('ftp') or url.strip().lower().startswith('http')):
        raise Exception(f'invalid address, url={url}')

    # astropy download
    try:
        clear_download_cache()
        iers.IERS_A_URL = f'{url}'
        download_IERS_A()
    except:
        pass

# +
# main()
# -
if __name__ == '__main__':
    get_iers()
