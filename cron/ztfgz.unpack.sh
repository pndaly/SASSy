#!/bin/sh


# +
#
# Name:        ztfgz.unpack.sh
# Description: unpack ZTF gzip file for given date
# Author:      Phil Daly (pndaly@email.arizona.edu)
# Date:        20180831
# Execute:     % bash ztfgz.unpack.sh --help
#
# -


# +
# set defaults: edit as you see fit
# -
HERE=${PWD}
default_archive_dir='/dataraid6/backups'
default_avro_dir='/dataraid6/ztf'
default_owner="sassy:users"

# +
# set defaults: do not edit
# -
today=$(date '+%Y%m%d')
default_year=${today:0:4}
default_month=${today:4:2}
default_day=${today:6:2}

dry_run=0
over_ride=0


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
  write_blue   "Unpack ZTF gzip file (pndaly@email.arizona.edu)"                                                      2>&1
  write_blue   ""                                                                                                     2>&1
  write_green  "Use:"                                                                                                 2>&1
  write_green  " %% bash $0 --date=<int> --archive-dir=<str> --avro-dir=<str> [--dry-run] [--over-ride]"              2>&1
  write_green  ""                                                                                                     2>&1
  write_yellow "Input(s):"                                                                                            2>&1
  write_yellow "  --date=<int>         where <int> is of the form YYYYMMDD,           default=${today}"               2>&1
  write_yellow "  --archive-dir=<str>  where <str> is the (input) archive directory,  default=${default_archive_dir}" 2>&1
  write_yellow "  --avro-dir=<str>     where <str> is the (output) avro directory,    default=${default_avro_dir}"    2>&1
  write_yellow ""                                                                                                     2>&1
  write_cyan   "Flag(s):"                                                                                             2>&1
  write_cyan   "  --dry-run            show (but do not execute) commands,            default=false"                  2>&1
  write_cyan   "  --over-ride          over-write existing file(s),                   default=false"                  2>&1
  write_cyan   ""                                                                                                     2>&1
  echo         "Output(s):"                                                                                           2>&1
  echo         "  ${default_avro_dir}/${default_year}/${default_month}/${default_day}/*.avro"                         2>&1
  echo         ""                                                                                                     2>&1
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
    --avro-dir*|--AVRO-DIR*)
      rs_avro_dir=$(echo $1 | cut -d'=' -f2)
      shift
      ;;
    --dry-run|--DRY-RUN)
      dry_run=1
      shift
      ;;
    --override|--OVERRIDE|--over-ride|--OVER-RIDE|--overwrite|--OVERWRITE|--over-write|--OVER-WRITE)
      over_ride=1
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

if [[ -z ${rs_avro_dir} ]]; then
  rs_avro_dir=${default_avro_dir}
fi


# +
# check validity
#-
if ! [[ ${rs_date} =~ ^[0-9]{4}[0-9]{2}[0-9]{2}$ ]]; then
  write_red "<ERROR> date (${rs_date}) is not valid ... exiting"
  exit 0
fi

rs_year=${rs_date:0:4}
rs_month=${rs_date:4:2}
rs_day=${rs_date:6:2}

if ! [[ -d ${rs_archive_dir} ]]; then
  write_red "<ERROR> directory (${rs_archive_dir}) does not exist... exiting"
  exit 0
fi

if ! [[ -d ${rs_avro_dir} ]]; then
  write_red "<ERROR> directory (${rs_avro_dir}) does not exist... exiting"
  exit 0
fi

if [[ -f ${rs_archive_dir}/ztf_public_${rs_date}.tar.gz ]]; then
  if [[ $(stat --printf=%s ${rs_archive_dir}/ztf_public_${rs_date}.tar.gz) =~ ^[0-9]{3}$ ]]; then
    write_red "<ERROR> archive (${rs_archive_dir}/ztf_public_${rs_date}.tar.gz) < 1000 bytes ... not unpacking"
    exit 0
  fi

  if [[ $(stat --printf=%s ${rs_archive_dir}/ztf_public_${rs_date}.tar.gz) =~ ^[0-9]{2}$ ]]; then
    write_red "<ERROR> archive (${rs_archive_dir}/ztf_public_${rs_date}.tar.gz) < 100 bytes ... not unpacking"
    exit 0
  fi
fi


# +
# execute (dry-run)
# -
parent=$(dirname ${rs_avro_dir}/${rs_year}/${rs_month}/${rs_day})
write_blue "%% bash $0 --archive-dir=${rs_archive_dir} --avro-dir=${rs_avro_dir} --date=${rs_date} --dry-run=${dry_run} --over-ride=${over_ride}"
if [[ ${dry_run} -eq 1 ]]; then

  if [[ ! -d ${rs_avro_dir}/${rs_year}/${rs_month}/${rs_day} ]]; then
    write_yellow "Dry-Run>> mkdir -p ${rs_avro_dir}/${rs_year}/${rs_month}/${rs_day}"
  fi

  if [[ ${over_ride} -eq 1 ]]; then
    write_yellow "Dry-Run>> rm -rf ${rs_avro_dir}/${rs_year}/${rs_month}/${rs_day}/*.avro >> /dev/null 2>&1"
  fi

  write_yellow "Dry-Run>> cd ${rs_avro_dir}/${rs_year}/${rs_month}/${rs_day}"
  write_yellow "Dry-Run>> gzip -cd ${rs_archive_dir}/ztf_public_${rs_date}.tar.gz | tar xvf -"
  write_yellow "Dry-Run>> chown -R ${default_owner} ${parent}"


# +
# execute (for-real)
# -
else

  if [[ ! -d ${rs_avro_dir}/${rs_year}/${rs_month}/${rs_day} ]]; then
    write_yellow "Executing>> mkdir -p ${rs_avro_dir}/${rs_year}/${rs_month}/${rs_day}"
    mkdir -p ${rs_avro_dir}/${rs_year}/${rs_month}/${rs_day}
  fi

  if [[ ${over_ride} -eq 1 ]]; then
    write_yellow "Executing>> rm -rf ${rs_avro_dir}/${rs_year}/${rs_month}/${rs_day}/*.avro >> /dev/null 2>&1"
    rm -rf ${rs_avro_dir}/${rs_year}/${rs_month}/${rs_day}/*.avro >> /dev/null 2>&1
  fi

  write_yellow "Executing>> cd ${rs_avro_dir}/${rs_year}/${rs_month}/${rs_day}"
  cd ${rs_avro_dir}/${rs_year}/${rs_month}/${rs_day}
  write_yellow "Executing>> gzip -cd ${rs_archive_dir}/ztf_public_${rs_date}.tar.gz | tar xvf -"
  gzip -cd ${rs_archive_dir}/ztf_public_${rs_date}.tar.gz | tar xvf -
  write_yellow "Executing>> chown -R ${default_owner} ${parent}"
  chown -R ${default_owner} ${parent}
fi


# +
# exit
# -
exit 0
