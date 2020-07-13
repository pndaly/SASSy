# The Steward Alerts for Science System #

Welcome to the **S**teward **A**lerts for **S**cience **Sy**tem (SASSy).

This work is heavily based upon [MARS](https://mars.lco.global), the 
Las Cumbras Observatory alert broker, and extended to ingest both 
[ZTF](https://www.ztf.caltech.edu) and [TNS](https://wis-tns.weizmann.ac.il) 
public alerts. We also support LIGO data scraped from TNS and both the
GLADE and GWGC catalogs.

Code modified in this system originated from the following sources:

 * http://github.com/lcogt/ztf-alert-server
 * https://github.com/ZwickyTransientFacility/ztf-avro-alert
 * https://wis-tns.weizmann.ac.il/sites/default/files/api/api_bulk_report.zip
 * https://github.com/ericmandel/js9
 
## Pre-Requisites

 * Linux (we use Ubuntu 18.04.2 LTS)
 * Python 3.6.6 (it will not work with Python < 3.6.5)
 * PostGreSQL 12.x (but will probably work with earlier versions)
 * JS9
 * Bootstrap 4.5.x
 * jQuery 3.5.1
 * An account at TNS (optional)
 * A *Memorandum of Understanding (MoU)* with ZTF to ingest alerts in real-time.
   - If you don't have a *MoU*, daily alerts are available at the 
  [University of Washington](https://ztf.uw.edu/alerts/public/).

## Get The Software

 * Obtain a copy of the software from [GitHub](https://github.com/pndaly/SASSy).

 * Install dependencies:

    ```bash
    % pip3 install --upgrade pip
    % pip3 install -r requirements.txt

## Create User

As `root`, create a *sassy* user (change the password to suit your site):

```bash
 % adduser sassy --gecos "sassy, unknown, (xxx) xxx-xxxx, unknown" --disabled-password
 % echo "sassy:secretsanta" | chpasswd
 % usermod -aG sudo sassy
 % usermod -aG users sassy
```

## Create and Populate The Database and Tables

NB: All utility bash-shell scripts in ${SASSY_BIN} support the `--help` argument for further information 
and the `--dry-run` option to show executable commands without invoking them. You would be well-advised
to use them!

 * Create the *sassy* database

    To create a database called *sassy* with username *sassy* and password *my_secret* (using the 
    PostGreSQL server defaults of *localhost:5432*), execute:
    
    ```bash
    % bash ${SASSY_BIN}/sassy.database.sh --database=sassy --password=my_secret --username=sassy --dry-run
    % cat /tmp/sassy.database.sh
    % bash ${SASSY_BIN}/sassy.database.sh --database=sassy --password=my_secret --username=sassy
    ```
 * Create the tables (using the same credentials as defined above):

    ```bash
    % bash ${SASSY_BIN}/sassy.glade.sh --database=sassy --password=my_secret --username=sassy --dry-run
    % cat /tmp/sassy.glade.sh
    % bash ${SASSY_BIN}/sassy.glade.sh --database=sassy --password=my_secret --username=sassy
    ```

    ```bash
    % bash ${SASSY_BIN}/sassy.glade_q3c.sh --database=sassy --password=my_secret --username=sassy --dry-run
    % cat /tmp/sassy.glade_q3c.sh
    % bash ${SASSY_BIN}/sassy.glade_q3c.sh --database=sassy --password=my_secret --username=sassy
    ```

    ```bash
    % bash ${SASSY_BIN}/sassy.gwgc.sh --database=sassy --password=my_secret --username=sassy --dry-run
    % cat /tmp/sassy.gwgc.sh
    % bash ${SASSY_BIN}/sassy.gwgc.sh --database=sassy --password=my_secret --username=sassy
    ```

    ```bash
    % bash ${SASSY_BIN}/sassy.gwgc_q3c.sh --database=sassy --password=my_secret --username=sassy --dry-run
    % cat /tmp/sassy.gwgc_q3c.sh
    % bash ${SASSY_BIN}/sassy.gwgc_q3c.sh --database=sassy --password=my_secret --username=sassy
    ```

    ```bash
    % bash ${SASSY_BIN}/sassy.ligo.sh --database=sassy --password=my_secret --username=sassy --dry-run
    % cat /tmp/sassy.ligo.sh
    % bash ${SASSY_BIN}/sassy.ligo.sh --database=sassy --password=my_secret --username=sassy
    ```

    ```bash
    % bash ${SASSY_BIN}/sassy.ligo_q3c.sh --database=sassy --password=my_secret --username=sassy --dry-run
    % cat /tmp/sassy.ligo_q3c.sh
    % bash ${SASSY_BIN}/sassy.ligo_q3c.sh --database=sassy --password=my_secret --username=sassy
    ```

    ```bash
    % bash ${SASSY_BIN}/sassy.tns.sh --database=sassy --password=my_secret --username=sassy --dry-run
    % cat /tmp/sassy.tns.sh
    % bash ${SASSY_BIN}/sassy.tns.sh --database=sassy --password=my_secret --username=sassy
    ```

    ```bash
    % bash ${SASSY_BIN}/sassy.tns_q3c.sh --database=sassy --password=my_secret --username=sassy --dry-run
    % cat /tmp/sassy.tns_q3c.sh
    % bash ${SASSY_BIN}/sassy.tns_q3c.sh --database=sassy --password=my_secret --username=sassy
    ```

 * Populating the database tables

    To populate the GLADE tables, execute:

    ```bash
    % cd ${SASSY_UTILS}
    % python3 ${SASSY_SRC}/models/glade.py --catalog --output=glade.local.csv
    % python3 ${SASSY_UTILS}/glade_read.py --file=glade.local.csv
    % python3 ${SASSY_UTILS}/glade_q3c_read.py --file=glade.local.csv
    ```

    To populate the GWGC tables, execute:

    ```bash
    % cd ${SASSY_UTILS}
    % python3 ${SASSY_SRC}/models/gwgc.py --catalog >> gwgc.dat
    % python3 ${SASSY_UTILS}/gwgc_read.py --file=gwgc.dat
    % python3 ${SASSY_UTILS}/gwgc_q3c_read.py --file=gwgc.dat
    ```

   The *ligo*, *ligo_q3c*, *tns* and *tns_q3c* tables can be populated using the web-scraping code via the `crontab` entries.   

   The ZTF *alerts* table is populated by the nightly `crontab` ingestion or manually via (*Eg* to retrieve the
   data for the first night and assuming you have modified the scripts to suit your local installation):
   
   ```bash
   % bash ${SASSY_CRON}/ztfgz.pull.sh --date=20180601 --dry-run
   % bash ${SASSY_CRON}/ztfgz.pull.sh --date=20180601
   % bash ${SASSY_CRON}/ztfgz.unpack.sh --date=20180601 --dry-run
   % bash ${SASSY_CRON}/ztfgz.unpack.sh --date=20180601
   % bash ${SASSY_CRON}/ztfgz.updatedb.sh --date=20180601 --dry-run
   % bash ${SASSY_CRON}/ztfgz.updatedb.sh --date=20180601
   ```

 * Database entity-relationship diagram 

    If you have `eralchemy` installed, an entity-relationship diagram can be generated:
    
    ```bash
    % eralchemy -i "postgresql+psycopg2://${SASSY_DB_USER}:${SASSY_DB_PASS}@${SASSY_DB_HOST}:${SASSY_DB_PORT}/${SASSY_DB_NAME}" -o ${SASSY_DB_NAME}.pdf
    ```

 * Database utilities

    We provide the following, generic, utilities for database manipulation:
    
    ```bash
    % bash ${SASSY_BIN}/psql.size.sh --help
    % bash ${SASSY_BIN}/psql.backup.sh --help
    % bash ${SASSY_BIN}/psql.restore.sh --help
    ```
## Create CRON Jobs

 * See [${SASSY_CRON}/README.md](${SASSY_CRON/README.md) for further information


## Configure For Local Site

You should now *copy* `${SASSY_BIN}/Sassy.template.sh`, `${SASSY_ETC}/Sassy.template.sh` 
and `${SASSY_SRC}/common.template.py` and edit the copies to suit your site and change:

   - local installation directory
   - database server and credentials
   - mail server and credentials

```bash
% cp ${SASSY_BIN}/Sassy.template.sh ${SASSY_BIN}/Sassy.sh
% vi ${SASSY_BIN}/Sassy.sh
% cp ${SASSY_ETC}/Sassy.template.sh ${SASSY_ETC}/Sassy.sh
% vi ${SASSY_ETC}/Sassy.sh
% cp ${SASSY_SRC}/common.template.py ${SASSY_SRC}/common.py
% vi ${SASSY_SRC}/common.py
```

## JS9, JavaScript and Bootstrap

We do not ship these items. Please refer to the README.md files in the static sub-directories
for getting and installing these products. The web-site will not work without them!

## Quick Start Guide

If you carried out the above, and assuming the codebase is in /home/sassy/SASSy, you can start the application:

* Local development server

    ```bash
    % cd /home/sassy/SASSy
    % source etc/Sassy.sh `pwd` dev
    % bash ${SASSY_BIN}/Sassy.sh --type=dev --source=/home/sassy/SASSy --command=start --dry-run
    % bash ${SASSY_BIN}/Sassy.sh --type=dev --source=/home/sassy/SASSy --command=start
    ```
    
    then point a browser to the local [ORP development server](http://localhost:5000/sassy).
    
* Local production server

    ```bash
    % cd /home/sassy/SASSy
    % source etc/Sassy.sh `pwd` prod
    % bash ${SASSY_BIN}/Sassy.sh --type=prod --source=/home/sassy/SASSy --command=start --dry-run
    % bash ${SASSY_BIN}/Sassy.sh --type=prod --source=/home/sassy/SASSy --command=start
    ```
    
    then point a browser to the local [ORP production server](http://localhost:6000/sassy).
    
* WSGI

    If you wish to run a WSGI-based server, we provide:

    * `${SASSY_HOME}/sassy.wsgi` file which should work as-is
    * `${SASSY_HOME}/sassy.conf` which should be edited: 
        `% sed 's/__myhost__/127\.0\.0\.1/g' >> /etc/apache2/sites-available/sassy.conf` (or whatever IP address you have)
    * Enable the site via *Apache2* in the usual way

-----------------------------------------------------------------------------------------------------------------

Last Updated: 20200702
