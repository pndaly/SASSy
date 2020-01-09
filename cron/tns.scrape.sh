#!/bin/sh


# +
#
# Name:        tns.scrape.sh
# Description: scrape TNS data from TNS
# Author:      Phil Daly (pndaly@email.arizona.edu)
# Date:        20190624
# Execute:     % bash tns.scrape.sh --help
#
# -


# +
# set defaults: edit as you see fit
# -
HERE=${PWD}
PARENT=$(dirname "${HERE}")

def_credentials="sassy:db_secret"


# +
# set defaults: do not edit
# -
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
  write_blue   ""                                                                                                   2>&1
  write_blue   "Scrape TNS Data"                                                                                    2>&1
  write_blue   ""                                                                                                   2>&1
  write_green  "Use:"                                                                                               2>&1
  write_green  " %% bash $0 [--dry-run]"                                                                            2>&1
  write_yellow ""                                                                                                   2>&1
  write_yellow "Input(s):"                                                                                          2>&1
  write_yellow "  --credentials=<str>, where <str> is of the form 'username:password',  default=${def_credentials}" 2>&1
  write_yellow ""                                                                                                   2>&1
  write_cyan   "Flag(s):"                                                                                           2>&1
  write_cyan   "  --dry-run        show (but do not execute) commands,    default=false"                            2>&1
  write_cyan   ""                                                                                                   2>&1
}


# +
# check command line argument(s) 
# -
while test $# -gt 0; do
  case "${1}" in
    --credentials*|--CREDENTIALS*)
      credentials=$(echo $1 | cut -d'=' -f2)
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
# check input(s)
# -
if [[ -z ${credentials} ]]; then
  credentials=${def_credentials}
fi


# +
# execute (dry-run)
# -
write_blue "%% bash $0 --dry-run=${dry_run}"
if [[ ${dry_run} -eq 1 ]]; then
  write_yellow "Dry-Run>> source ${PARENT}/etc/Sassy.sh ${PARENT}"
  write_yellow "Dry-Run>> PYTHONPATH=${PARENT}:${PARENT}/src python3 ${PARENT}/src/utils/tns_scrape.py --verbose --number=1 --unit=Days --credentials=${credentials}"


# +
# execute (for-real)
# -
else
  write_yellow "Executing>> source ${PARENT}/etc/Sassy.sh ${PARENT}"
  source ${PARENT}/etc/Sassy.sh ${PARENT}
  write_yellow "Executing>> PYTHONPATH=${PARENT}:${PARENT}/src python3 ${PARENT}/src/utils/tns_scrape.py --verbose --number=1 --unit=Days --credentials=${credentials}"
  PYTHONPATH=${PARENT}:${PARENT}/src python3 ${PARENT}/src/utils/tns_scrape.py --verbose --number=1 --unit=Days --credentials=${credentials}
fi


# +
# exit
# -
exit 0
