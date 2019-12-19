#!/bin/sh


# +
#
# Name:        ztfgz.updatedb.sh
# Description: update database from ZTF gzip file for given date
# Author:      Phil Daly (pndaly@email.arizona.edu)
# Date:        20190121
# Execute:     % bash ztfgz.updatedb.sh --help
#
# -


# +
# set defaults: edit as you see fit
# -
HERE=${PWD}
PARENT=$(dirname "${HERE}")
default_archive_dir='/dataraid6/backups'


# +
# set defaults: do not edit
# -
today=$(date '+%Y%m%d')

dry_run=0


# +
# utility functions
# -
write_blue () {
  BLUE='\033[0;34m'
  NCOL='\033[0m'
  printf "${BLUE}${1}${NCOL}\n"
}
write_red () {
  RED='\033[0;31m'
  NCOL='\033[0m'
  printf "${RED}${1}${NCOL}\n"
}
write_yellow () {
  YELLOW='\033[0;33m'
  NCOL='\033[0m'
  printf "${YELLOW}${1}${NCOL}\n"
}
write_green () {
  GREEN='\033[0;32m'
  NCOL='\033[0m'
  printf "${GREEN}${1}${NCOL}\n"
}
write_cyan () {
  CYAN='\033[0;36m'
  NCOL='\033[0m'
  printf "${CYAN}${1}${NCOL}\n"
}
usage () {
  write_blue   ""                                                                                                     2>&1
  write_blue   "Update database from ZTF gzip file (pndaly@email.arizona.edu)"                                        2>&1
  write_blue   ""                                                                                                     2>&1
  write_green  "Use:"                                                                                                 2>&1
  write_green  " %% bash $0 --date=<int> --archive-dir=<str> [--dry-run]"                                             2>&1
  write_green  ""                                                                                                     2>&1
  write_yellow "Input(s):"                                                                                            2>&1
  write_yellow "  --date=<int>         where <int> is of the form YYYYMMDD,           default=${today}"               2>&1
  write_yellow "  --archive-dir=<str>  where <str> is the (input) archive directory,  default=${default_archive_dir}" 2>&1
  write_yellow ""                                                                                                     2>&1
  write_cyan   "Input(s):"                                                                                            2>&1
  write_cyan   "  --dry-run            show (but do not execute) commands,            default=false"                  2>&1
  write_cyan   ""                                                                                                     2>&1
}


# +
# check command line argument(s) 
# -
while test $# -gt 0; do
  case "${1}" in
    --date*|--DATE*)
      rs_date=$(echo $1 | cut -d'=' -f2)
      shift
      ;;
    --archive-dir*|--ARCHIVE-DIR*)
      rs_archive_dir=$(echo $1 | cut -d'=' -f2)
      shift
      ;;
    --dry-run|--DRY-RUN)
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
# (re)set variable(s)
# -
case ${rs_date} in
  [0-9]*)
    ;;
  *)
    rs_date=${today}
    ;;
esac

if [[ -z ${rs_archive_dir} ]]; then
  rs_archive_dir=${default_archive_dir}
fi


# +
# check validity
#-
if ! [[ ${rs_date} =~ ^[0-9]{4}[0-9]{2}[0-9]{2}$ ]]; then
  write_red "<ERROR> date (${rs_date}) is not valid ... exiting"
  exit 0
fi

if ! [[ -d ${rs_archive_dir} ]]; then
  write_red "<ERROR> directory (${rs_archive_dir}) does not exist... exiting"
  exit 0
fi

if [[ -f ${rs_archive_dir}/ztf_public_${rs_date}.tar.gz ]]; then
  if [[ $(stat --printf=%s ${rs_archive_dir}/ztf_public_${rs_date}.tar.gz) =~ ^[0-9]{3}$ ]]; then
    write_red "<ERROR> archive (${rs_archive_dir}/ztf_public_${rs_date}.tar.gz) < 1000 bytes ... not updating"
    exit 0
  fi

  if [[ $(stat --printf=%s ${rs_archive_dir}/ztf_public_${rs_date}.tar.gz) =~ ^[0-9]{2}$ ]]; then
    write_red "<ERROR> archive (${rs_archive_dir}/ztf_public_${rs_date}.tar.gz) < 100 bytes ... not updating"
    exit 0
  fi
fi


# +
# execute (dry-run)
# -
if [[ ${dry_run} -eq 1 ]]; then
  write_green "%% bash $0 --archive-dir=${rs_archive_dir} --date=${rs_date} --dry-run=${dry_run}"
  write_yellow "Dry-Run>> source ${PARENT}/etc/Sassy.sh ${PARENT}"
  write_yellow "Dry-Run>> PYTHONPATH=${PARENT}:${PARENT}/src python3 ${PARENT}/src/ingest_from_gzip.py --file=${rs_archive_dir}/ztf_public_${rs_date}.tar.gz"


# +
# execute (for-real)
# -
else
  write_blue "%% bash $0 --archive-dir=${rs_archive_dir} --date=${rs_date} --dry-run=${dry_run}"
  write_yellow "Executing>> source ${PARENT}/etc/Sassy.sh ${PARENT}"
  source ${PARENT}/etc/Sassy.sh ${PARENT}
  write_yellow "Executing>> PYTHONPATH=${PARENT}:${PARENT}/src python3 ${PARENT}/src/ingest_from_gzip.py --file=${rs_archive_dir}/ztf_public_${rs_date}.tar.gz"
  PYTHONPATH=${PARENT}:${PARENT}/src python3 ${PARENT}/src/ingest_from_gzip.py --file=${rs_archive_dir}/ztf_public_${rs_date}.tar.gz

fi


# +
# exit
# -
exit 0
