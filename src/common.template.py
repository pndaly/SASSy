#!/usr/bin/env python3


# +
# import(s)
# -
import os


# +
# get env(s)
# -
SASSY_APP_HOST = os.getenv("SASSY_APP_HOST", "localhost")
SASSY_APP_PORT = os.getenv("SASSY_APP_PORT", 5000)
SASSY_APP_URL = os.getenv("SASSY_APP_URL", f"https://{SASSY_APP_HOST}/sassy")

SASSY_DB_HOST = os.getenv("SASSY_DB_HOST", "localhost")
SASSY_DB_NAME = os.getenv("SASSY_DB_NAME", "sassy")
SASSY_DB_PASS = os.getenv("SASSY_DB_PASS", "*******")
SASSY_DB_PORT = os.getenv("SASSY_DB_PORT", 5432)
SASSY_DB_USER = os.getenv("SASSY_DB_USER", "sassy")

SASSY_HOME = os.getenv("SASSY_HOME", "/var/www/SASSy")
SASSY_SRC = os.getenv("SASSY_SRC", "/var/www/SASSy/src")

SASSY_AIRMASS = os.getenv("SASSY_AIRMASS", "/var/www/SASSy/img/airmass")
SASSY_FINDERS = os.getenv("SASSY_FINDERS", "/var/www/SASSy/img/finders")
SASSY_TTF = os.getenv("SASSY_TTF", "/var/www/SASSy/src/ttf")

SASSY_ZTF_ARCHIVE = os.getenv("SASSY_ZTF_ARCHIVE", "/dataraid6/backups:/data/backups")
SASSY_ZTF_DATA = os.getenv("SASSY_ZTF_DATA", "/dataraid6/ztf:/data/ztf")
SASSY_ZTF_AVRO = os.getenv("SASSY_ZTF_AVRO", "/dataraid6/ztf:/data/ztf")

PYTHONPATH = os.getenv("PYTHONPATH", "/var/www/SASSy/src")
