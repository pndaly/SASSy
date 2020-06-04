#!/usr/bin/python3


# +
# import(s)
# -
import os
import hashlib
import sys


# +
# code base
# -
BASE = "/var/www/SASSy"
KEY = hashlib.sha256(BASE.encode('utf-8')).hexdigest()


# +
# path(s)
# -
os.environ["PYTHONPATH"] = f'{BASE}:{BASE}/src'
sys.path.insert(0, f'{BASE}')
sys.path.append(f'{BASE}/src')


# +
# start
# -
# noinspection PyPep8
from src.app import app as application
application.secret_key = KEY
