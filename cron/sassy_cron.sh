#!/bin/bash


# +
#
# Name:        sassy_cron.sh
# Description: SassyCron Control
# Author:      Phil Daly (pndaly@arizona.edu)
# Date:        20200901
# Execute:     % bash sassy_cron.sh --help
#
# -


# +
# default(s)
# -
source /var/www/SASSy/etc/Sassy.sh /var/www/SASSy

authorization="sassy:db_secret"
max_jd=$(python3 -c "from src import *; print(get_jd(0))")
max_mpc=500.0
max_rb=1.0
min_jd=$(python3 -c "from src import *; print(get_jd(-1))")
min_mpc=0.0
min_rb=0.5
radius=45.0
dry_run=0


# +
# auxiliary function(s)
# -
write_red () { 
  printf "\033[0;31m${1}\033[0m\n"
}

write_green () { 
  printf "\033[0;32m${1}\033[0m\n"
}

write_yellow () { 
  printf "\033[0;33m${1}\033[0m\n"
}

write_blue () { 
  printf "\033[0;34m${1}\033[0m\n"
}

write_magenta () { 
  printf "\033[0;35m${1}\033[0m\n"
}

write_cyan () { 
  printf "\033[0;36m${1}\033[0m\n"
}

usage () {
  write_blue   ""                                                                                                                                   2>&1
  write_blue   "SassyCron Control"                                                                                                                  2>&1
  write_blue   ""                                                                                                                                   2>&1
  write_green  "Use:"                                                                                                                               2>&1
  write_green  "  %% bash ${0} --max_jd=<float> --max_mpc=<float> --max_rb=<float> --min_jd=<float> --min_mpc=<float> --min_rb=<float> [--dry-run]" 2>&1
  write_yellow ""                                                                                                                                   2>&1
  write_yellow "Input(s):"                                                                                                                          2>&1
  write_yellow "  --authorization=<str>,  database credentials,                        default=${authorization}"                                    2>&1
  write_yellow "  --max_jd=<float>,       Maximum julian day,                          default=${max_jd}"                                           2>&1
  write_yellow "  --max_mpc=<float>,      Maximum distance (Mpc),                      default=${max_mpc}"                                          2>&1
  write_yellow "  --max_rb=<float>,       Maximum real-bogus score,                    default=${max_rb}"                                           2>&1
  write_yellow "  --min_jd=<float>,       Minimum julian day,                          default=${min_jd}"                                           2>&1
  write_yellow "  --min_mpc=<float>,      Minimum distance (Mpc),                      default=${min_mpc}"                                          2>&1
  write_yellow "  --min_rb=<float>,       Minimum real-bogus score,                    default=${min_rb}"                                           2>&1
  write_yellow "  --radius=<float>,       search radius (arcsec),                      default=${radius}"                                           2>&1
  write_yellow ""                                                                                                                                   2>&1
  write_cyan   "Flag(s):"                                                                                                                           2>&1
  write_cyan   "  --dry-run,         show (but do not execute) command(s),             default=false"                                               2>&1
  write_cyan   ""                                                                                                                                   2>&1
}


# +
# get command line argument(s) 
# -
while [[ $# -gt 0 ]]; do
  case "${1}" in
    --authorization*)
      _authorization=$(echo ${1} | cut -d'=' -f2)
      shift
      ;;
    --max_jd*)
      _max_jd=$(echo ${1} | cut -d'=' -f2)
      shift
      ;;
    --max_mpc*)
      _max_mpc=$(echo ${1} | cut -d'=' -f2)
      shift
      ;;
    --max_rb*)
      _max_rb=$(echo ${1} | cut -d'=' -f2)
      shift
      ;;
    --min_jd*)
      _min_jd=$(echo ${1} | cut -d'=' -f2)
      shift
      ;;
    --min_mpc*)
      _min_mpc=$(echo ${1} | cut -d'=' -f2)
      shift
      ;;
    --min_rb*)
      _min_rb=$(echo ${1} | cut -d'=' -f2)
      shift
      ;;
    --radius*)
      _radius=$(echo ${1} | cut -d'=' -f2)
      shift
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    --help|*)
      usage
      exit 0
      ;;
  esac
done


# +
# check and (re)set command line argument(s)
# -
[[ -z ${_authorization} ]] && _authorization=${authorization}
[[ -z ${_max_jd} ]] && _max_jd=${max_jd}
[[ -z ${_max_mpc} ]] && _max_mpc=${max_mpc}
[[ -z ${_max_rb} ]] && _max_rb=${max_rb}
[[ -z ${_min_jd} ]] && _min_jd=${min_jd}
[[ -z ${_min_mpc} ]] && _min_mpc=${min_mpc}
[[ -z ${_min_rb} ]] && _min_rb=${min_rb}
[[ -z ${_radius} ]] && _radius=${radius}

[[ ! ${_max_jd} =~ ^[0-9]*\.[0-9]*$ ]] && write_red "<ERROR> max_jd=${_max_jd} is invalid!" && exit 0
[[ ! ${_max_mpc} =~ ^[0-9]*\.[0-9]*$ ]] && write_red "<ERROR> max_mpc=${_max_mpc} is invalid!" && exit 0
[[ ! ${_max_rb} =~ ^[0-9]*\.[0-9]*$ ]] && write_red "<ERROR> max_rb=${_max_rb} is invalid!" && exit 0
[[ ! ${_min_jd} =~ ^[0-9]*\.[0-9]*$ ]] && write_red "<ERROR> min_jd=${_min_jd} is invalid!" && exit 0
[[ ! ${_min_mpc} =~ ^[0-9]*\.[0-9]*$ ]] && write_red "<ERROR> min_mpc=${_min_mpc} is invalid!" && exit 0
[[ ! ${_min_rb} =~ ^[0-9]*\.[0-9]*$ ]] && write_red "<ERROR> min_rb=${_min_rb} is invalid!" && exit 0
[[ ! ${_radius} =~ ^[0-9]*\.[0-9]*$ ]] && write_red "<ERROR> radius=${_radius} is invalid!" && exit 0

write_blue "%% bash ${0} --authorization=${_authorization} --max_jd=${_max_jd} --max_mpc=${_max_mpc} --max_rb=${_max_rb} --min_jd=${_min_jd} --min_mpc=${_min_mpc} --min_rb=${_min_rb} --radius=${_radius} --dry-run=${dry_run}" 2>&1


# +
# variable(s)
# -
_user=$(echo ${_authorization} | cut -d':' -f1)
_pass=$(echo ${_authorization} | cut -d':' -f2)
_radius_degree=$( echo "scale=6; ${_radius} / 3600.00" | bc -l)


# +
# worker function(s)
# -
_create_sassy_cron_ztf () {
  write_magenta "_create_sassy_cron_ztf(dry_run=${1}, user=${2}, pass=${3}, max_jd=${4}, max_rb=${5}, min_jd=${6}, min_rb=${7})"
  if [[ ${1} -eq 1 ]]; then
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"DROP INDEX IF EXISTS sassy_cron_ztf_q3c_ang2ipix_idx;\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"DROP TABLE IF EXISTS sassy_cron_ztf;\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"CREATE TABLE sassy_cron_ztf (zoid, zjd, zmagap, zmagpsf, zmagdiff, zfid, zdrb, zrb, zsid, zcandid, zssnamenr, zra, zdec) AS (SELECT DISTINCT \"objectId\", jd, magap, magpsf, magdiff, fid, drb, rb, id, alert_candid, ssnamenr, (CASE WHEN ST_X(ST_AsText(location)) < 0.0 THEN ST_X(ST_AsText(location))+360.0 ELSE ST_X(ST_AsText(location)) END), ST_Y(ST_AsText(location)) FROM alert WHERE ((\"objectId\" LIKE 'ZTF2') AND ssnamenr LIKE 'null' AND (jd BETWEEN ${6} AND ${4}) AND ((rb BETWEEN ${7} AND ${5}) OR (drb BETWEEN ${7} AND ${5}))));\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"CREATE INDEX ON sassy_cron_ztf (q3c_ang2ipix(zra, zdec));\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"CLUSTER sassy_cron_ztf_q3c_ang2ipix_idx ON sassy_cron_ztf;\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"SELECT COUNT(*) FROM sassy_cron_ztf;\""

  else
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "DROP INDEX IF EXISTS sassy_cron_ztf_q3c_ang2ipix_idx;" 2> /dev/null
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "DROP TABLE IF EXISTS sassy_cron_ztf;" 2> /dev/null
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "CREATE TABLE sassy_cron_ztf (zoid, zjd, zmagap, zmagpsf, zmagdiff, zfid, zdrb, zrb, zsid, zcandid, zssnamenr, zra, zdec) AS (SELECT DISTINCT \"objectId\", jd, magap, magpsf, magdiff, fid, drb, rb, id, alert_candid, ssnamenr, (CASE WHEN ST_X(ST_AsText(location)) < 0.0 THEN ST_X(ST_AsText(location))+360.0 ELSE ST_X(ST_AsText(location)) END), ST_Y(ST_AsText(location)) FROM alert WHERE ((\"objectId\" LIKE '%ZTF2%') AND ssnamenr LIKE '%null%' AND (jd BETWEEN ${6} AND ${4}) AND ((rb BETWEEN ${7} AND ${5}) OR (drb BETWEEN ${7} AND ${5}))));"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "CREATE INDEX ON sassy_cron_ztf (q3c_ang2ipix(zra, zdec));"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "CLUSTER sassy_cron_ztf_q3c_ang2ipix_idx ON sassy_cron_ztf;"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "SELECT COUNT(*) FROM sassy_cron_ztf;"
  fi
}


_create_sassy_cron_glade () {
  write_magenta "_create_sassy_cron_glade(dry_run=${1}, user=${2}, pass=${3}, max_mpc=${4}, min_mpc=${5})"
  if [[ ${1} -eq 1 ]]; then
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"DROP INDEX IF EXISTS sassy_cron_glade_q3c_ang2ipix_idx;\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"DROP TABLE IF EXISTS sassy_cron_glade;\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"CREATE TABLE sassy_cron_glade (gid, gra, gdec, gz, gdist) AS (SELECT DISTINCT id, ra, dec, z, dist FROM glade_q3c WHERE (dist BETWEEN ${5} AND ${4}));\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"CREATE INDEX ON sassy_cron_glade (q3c_ang2ipix(gra, gdec));\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"CLUSTER sassy_cron_glade_q3c_ang2ipix_idx ON sassy_cron_glade;\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"SELECT COUNT(*) FROM sassy_cron_glade;\""
  else
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "DROP INDEX IF EXISTS sassy_cron_glade_q3c_ang2ipix_idx;" 2> /dev/null
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "DROP TABLE IF EXISTS sassy_cron_glade;" 2> /dev/null
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "CREATE TABLE sassy_cron_glade (gid, gra, gdec, gz, gdist) AS (SELECT DISTINCT id, ra, dec, z, dist FROM glade_q3c WHERE (dist BETWEEN ${5} AND ${4}));"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "CREATE INDEX ON sassy_cron_glade (q3c_ang2ipix(gra, gdec));"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "CLUSTER sassy_cron_glade_q3c_ang2ipix_idx ON sassy_cron_glade;"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "SELECT COUNT(*) FROM sassy_cron_glade;"
  fi
}

_create_sassy_cron_q3c () {
  write_magenta "_create_sassy_cron_q3c(dry_run=${1}, user=${2}, pass=${3}, radius=${4})"
  if [[ ${1} -eq 1 ]]; then
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"DROP INDEX IF EXISTS sassy_cron_q3c_q3c_ang2ipix_idx;\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"DROP TABLE IF EXISTS sassy_cron_q3c;\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"CREATE TABLE sassy_cron_q3c (zoid, zjd, zmagap, zmagpsf, zmagdiff, zfid, zdrb, zrb, zsid, zcandid, zssnamenr, zra, zdec, gid, gra, gdec, gz, gdist, gsep) AS WITH x AS (SELECT DISTINCT z.zoid, z.zjd, z.zmagap, z.zmagpsf, z.zmagdiff, z.zfid, z.zdrb, z.zrb, z.zsid, z.zcandid, z.zssnamenr, z.zra, z.zdec, g.gid, g.gra, g.gdec, g.gz, g.gdist, q3c_dist(z.zra, z.zdec, g.gra, g.gdec) FROM sassy_cron_ztf as z, sassy_cron_glade as g WHERE q3c_join(z.zra, z.zdec, g.gra, g.gdec, ${4})) SELECT DISTINCT * FROM x;\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"CREATE INDEX ON sassy_cron_q3c (q3c_ang2ipix(zra, zdec));\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"CLUSTER sassy_cron_q3c_q3c_ang2ipix_idx ON sassy_cron_q3c;\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"SELECT COUNT(*) FROM sassy_cron_q3c;\""
  else
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "DROP INDEX IF EXISTS sassy_cron_q3c_q3c_ang2ipix_idx;"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "DROP TABLE IF EXISTS sassy_cron_q3c;"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "CREATE TABLE sassy_cron_q3c (zoid, zjd, zmagap, zmagpsf, zmagdiff, zfid, zdrb, zrb, zsid, zcandid, zssnamenr, zra, zdec, gid, gra, gdec, gz, gdist, gsep) AS WITH x AS (SELECT DISTINCT z.zoid, z.zjd, z.zmagap, z.zmagpsf, z.zmagdiff, z.zfid, z.zdrb, z.zrb, z.zsid, z.zcandid, z.zssnamenr, z.zra, z.zdec, g.gid, g.gra, g.gdec, g.gz, g.gdist, q3c_dist(z.zra, z.zdec, g.gra, g.gdec) FROM sassy_cron_ztf as z, sassy_cron_glade as g WHERE q3c_join(z.zra, z.zdec, g.gra, g.gdec, ${4})) SELECT DISTINCT * FROM x;"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "CREATE INDEX ON sassy_cron_q3c (q3c_ang2ipix(zra, zdec));"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "CLUSTER sassy_cron_q3c_q3c_ang2ipix_idx ON sassy_cron_q3c;"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "SELECT COUNT(*) FROM sassy_cron_q3c;"
  fi
}


_create_sassy_cron () {
  write_magenta "_create_sassy_cron(dry_run=${1}, user=${2}, pass=${3}, radius=${4})"
  if [[ ${1} -eq 1 ]]; then
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"DROP INDEX IF EXISTS sassy_cron_q3c_ang2ipix_idx;\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"DROP TABLE IF EXISTS sassy_cron;\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"CREATE TABLE sassy_cron AS WITH q AS (SELECT DISTINCT * FROM sassy_cron_q3c), e AS (SELECT DISTINCT * FROM q LEFT OUTER JOIN tns_q3c AS t ON q3c_join(q.zra, q.zdec, t.ra, t.dec , ${4})) SELECT DISTINCT * FROM e WHERE tns_id IS null;\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"ALTER TABLE sassy_cron ADD COLUMN aetype VARCHAR(64) DEFAULT '';\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"ALTER TABLE sassy_cron ADD COLUMN altype VARCHAR(64) DEFAULT '';\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"ALTER TABLE sassy_cron ADD COLUMN aeprob FLOAT DEFAULT 'NaN';\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"ALTER TABLE sassy_cron ADD COLUMN alprob FLOAT DEFAULT 'NaN';\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"ALTER TABLE sassy_cron ADD COLUMN dpng VARCHAR(200) DEFAULT '';\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"ALTER TABLE sassy_cron ADD COLUMN spng VARCHAR(200) DEFAULT '';\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"ALTER TABLE sassy_cron ADD COLUMN tpng VARCHAR(200) DEFAULT '';\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"CREATE INDEX ON sassy_cron (q3c_ang2ipix(zra, zdec));\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"CLUSTER sassy_cron_q3c_ang2ipix_idx ON sassy_cron;\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"SELECT COUNT(*) FROM sassy_cron;\""
  else
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "DROP INDEX IF EXISTS sassy_cron_q3c_ang2ipix_idx;"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "DROP TABLE IF EXISTS sassy_cron;"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "CREATE TABLE sassy_cron AS WITH q AS (SELECT DISTINCT * FROM sassy_cron_q3c), e AS (SELECT DISTINCT * FROM q LEFT OUTER JOIN tns_q3c AS t ON q3c_join(q.zra, q.zdec, t.ra, t.dec , ${4})) SELECT DISTINCT * FROM e WHERE tns_id IS null;"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "ALTER TABLE sassy_cron ADD COLUMN aetype VARCHAR(64) DEFAULT '';"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "ALTER TABLE sassy_cron ADD COLUMN altype VARCHAR(64) DEFAULT '';"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "ALTER TABLE sassy_cron ADD COLUMN aeprob FLOAT DEFAULT 'NaN';"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "ALTER TABLE sassy_cron ADD COLUMN alprob FLOAT DEFAULT 'NaN';"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "ALTER TABLE sassy_cron ADD COLUMN dpng VARCHAR(200) DEFAULT '';"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "ALTER TABLE sassy_cron ADD COLUMN spng VARCHAR(200) DEFAULT '';"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "ALTER TABLE sassy_cron ADD COLUMN tpng VARCHAR(200) DEFAULT '';"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "CREATE INDEX ON sassy_cron (q3c_ang2ipix(zra, zdec));"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "CLUSTER sassy_cron_q3c_ang2ipix_idx ON sassy_cron;"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "SELECT COUNT(*) FROM sassy_cron;"
  fi
}


_drop_interim () {
  write_magenta "_drop_interim(dry_run=${1}, user=${2}, pass=${3})"
  if [[ ${1} -eq 1 ]]; then
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"DROP INDEX IF EXISTS sassy_cron_ztf_q3c_ang2ipix_idx;\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"DROP TABLE IF EXISTS sassy_cron_ztf;\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"DROP INDEX IF EXISTS sassy_cron_glade_q3c_ang2ipix_idx;\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"DROP TABLE IF EXISTS sassy_cron_glade;\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"DROP INDEX IF EXISTS sassy_cron_q3c_q3c_ang2ipix_idx;\""
    write_yellow "DryRun> PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c \"DROP TABLE IF EXISTS sassy_cron_q3c;\""
  else
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "DROP INDEX IF EXISTS sassy_cron_ztf_q3c_ang2ipix_idx;"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "DROP TABLE IF EXISTS sassy_cron_ztf;"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "DROP INDEX IF EXISTS sassy_cron_glade_q3c_ang2ipix_idx;"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "DROP TABLE IF EXISTS sassy_cron_glade;"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "DROP INDEX IF EXISTS sassy_cron_q3c_q3c_ang2ipix_idx;"
    PGPASSWORD=${3} psql -h localhost -p 5432 -U ${2} -d ${2} -e -c "DROP TABLE IF EXISTS sassy_cron_q3c;"
  fi
}


_add_classifier_and_plot () {
  write_magenta "_add_classifier_and_plot(dry_run=${1})"
  if [[ ${1} -eq 1 ]]; then
    write_yellow "DryRun> source ~/.bashrc_conda"
    write_yellow "DryRun> conda activate"
    write_yellow "DryRun> python3 ${SASSY_SRC}/utils/get_iers.py"
    write_yellow "DryRun> cd ${SASSY_SRC}/static/img"
    write_yellow "DryRun> rm -f ZTF20*.png >> /dev/null 2>&1"
    write_yellow "DryRun> python3 ${SASSY_SRC}/utils/sassy_cron.py"
    write_yellow "DryRun> chown www-data:www-data ZTF20*.png >> /dev/null 2>&1"
  else
    source ~/.bashrc_conda
    conda activate
    python3 ${SASSY_SRC}/utils/get_iers.py
    cd ${SASSY_SRC}/static/img
    rm -f ZTF20*.png >> /dev/null 2>&1
    python3 ${SASSY_SRC}/utils/sassy_cron.py
    chown www-data:www-data ZTF20*.png >> /dev/null 2>&1
  fi
}



# +
# execute
# -
_create_sassy_cron_ztf ${dry_run} ${_user} ${_pass} ${_max_jd} ${_max_rb} ${_min_jd} ${_min_rb}
_create_sassy_cron_glade ${dry_run} ${_user} ${_pass} ${_max_mpc} ${_min_mpc}
_create_sassy_cron_q3c ${dry_run} ${_user} ${_pass} ${_radius_degree}
_create_sassy_cron ${dry_run} ${_user} ${_pass} ${_radius_degree}
_drop_interim ${dry_run} ${_user} ${_pass}
_add_classifier_and_plot ${dry_run}


# +
# exit
# -
exit 0
