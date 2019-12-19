#!/bin/sh


# +
#
# Name:        ztfgz.pull.sh
# Description: pull ZTF gzip file for given date
# Author:      Phil Daly (pndaly@email.arizona.edu)
# Date:        20180831
# Execute:     % bash ztfgz.pull.sh --help
#
# -


# +
# set defaults: edit as you see fit
# -
today=$(date '+%Y%m%d')

def_dir="/dataraid6/backups"
def_file="ztf_public_${today}.tar.gz"
def_owner="sassy:users"
def_server="https://ztf.uw.edu/alerts/public"

dry_run=0
over_ride=0
ignore_md5=0


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
  write_blue   ""                                                                                          2>&1
  write_blue   "Retrieve ZTF gzip file (pndaly@email.arizona.edu)"                                         2>&1
  write_blue   ""                                                                                          2>&1
  write_green  "Use:"                                                                                      2>&1
  write_green  " %% bash $0 --directory=<path> --date=<int> [--dry-run] [--ignore-checksum] [--over-ride]" 2>&1
  write_green  ""                                                                                          2>&1
  write_yellow "Input(s):"                                                                                 2>&1
  write_yellow "  --directory=<path> where <path> is the output directory,  default=${def_dir}"            2>&1
  write_yellow "  --date=<int>       where <int> is of the form YYYYMMDD,   default=${today}"              2>&1
  write_yellow ""                                                                                          2>&1
  write_cyan   "Flag(s):"                                                                                  2>&1
  write_cyan   "  --dry-run          show (but do not execute) commands,    default=false"                 2>&1
  write_cyan   "  --over-ride        over write any output file,            default=false"                 2>&1
  write_cyan   "  --ignore-checksum  ignore checksum file,                  default=false"                 2>&1
  write_cyan   ""                                                                                          2>&1
  echo         "Output(s):"                                                                                2>&1
  echo         "  ${def_dir}/${def_file}"                                                                  2>&1
  echo         ""                                                                                          2>&1
}


# +
# check command line argument(s) 
# -
while test $# -gt 0; do
  case "${1}" in
    --directory*|--DIRECTORY*)
      this_dir=$(echo $1 | cut -d'=' -f2)
      shift
      ;;
    --date*|--DATE*)
      this_date=$(echo $1 | cut -d'=' -f2)
      shift
      ;;
    --dry-run|--DRY-RUN)
      dry_run=1
      shift
      ;;
    --over_ride|--OVERRIDE|--over-ride|--OVER-RIDE|--overwrite|--OVERWRITE|--over-write|--OVER-WRITE)
      over_ride=1
      shift
      ;;
    --ignore_md5|--IGNORE|--ignore-checksum|--IGNORE-CHECKSUM|--ignore-md5|--IGNORE-MD5)
      ignore_md5=1
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
if [[ -z ${this_dir} ]]; then
  this_dir=${def_dir}
fi

case ${this_date} in
  [0-9]*)
    ;;
  *)
    this_date=${today}
    ;;
esac

this_file="${this_dir}/ztf_public_${this_date}.tar.gz"
this_gzip="${def_server}/ztf_public_${this_date}.tar.gz"


# +
# check validity 
#-
if ! [[ ${this_date} =~ ^[0-9]{4}[0-9]{2}[0-9]{2}$ ]]; then
  write_red "<ERROR> date (${this_date}) is not valid ... exiting"
  exit 0 
fi

if ! ping -c 1 -w 5 `echo ${def_server} | cut -d'/' -f3` &>/dev/null; then 
  write_red "<ERROR> remote server (${def_server}) is down ... exiting"
  exit 0 
fi

if [[ ${over_ride} -eq 0 ]]; then
  if [[ -f ${this_file} ]]; then
    write_blue "<INFO> ${this_file} already exists, no action required"
    exit 0
  fi
fi


# +
# execute (dry-run)
# -
if [[ ${dry_run} -eq 1 ]]; then

  write_green "%% bash $0 --date=${this_date} --dry-run=${dry_run} --ignore-checksum=${ignore_md5} --over-ride=${over_ride}"

  if [[ ${ignore_md5} -eq 1 ]]; then
    if [[ ${over_ride} -eq 1 ]]; then
      write_yellow "Dry-Run>> rm -f ${this_file} >> /dev/null 2>&1"
    fi
    write_yellow "Dry-Run>> curl ${this_gzip} -o ${this_file}"
    write_yellow "Dry-Run>> chown :users ${this_file}"
  else
    write_yellow "Dry-Run>> rm -f ${this_dir}/MD5SUMS >> /dev/null 2>&1"
    write_yellow "Dry-Run>> curl ${def_server}/MD5SUMS -o ${this_dir}/MD5SUMS"
    write_yellow "Dry-Run>> chown :users ${this_dir}/MD5SUMS"
    if [[ ${over_ride} -eq 1 ]]; then
      write_yellow "Dry-Run>> rm -f ${this_file} >> /dev/null 2>&1"
    fi
    write_yellow "Dry-Run>> curl ${this_gzip} -o ${this_file}"
    write_yellow "Dry-Run>> chown :users ${this_file}"
    write_yellow "Dry-Run>> rem_chk=\`grep -i $(basename ${this_file}) ${this_dir}/MD5SUMS | cut -d' ' -f1\`"
    write_yellow "Dry-Run>> loc_chk=\`md5sum ${this_file} | cut -d' ' -f1\`"
    write_yellow "Dry-Run>> if [ -z \${rem_chk} ]; then write_red \"<WARNING> ${this_file} has no known checksum\"; else if [ \${rem_chk} == \${loc_chk} ]; then echo \"${this_file} is valid\"; else write_red \"<ERROR> ${this_file} is invalid\"; fi; fi"
    write_yellow "Dry-Run>> chown -R ${def_owner} ${this_dir}"
  fi


# +
# execute (for-real)
# -
else

  write_blue "%% bash $0 --date=${this_date} --dry-run=${dry_run} --ignore-checksum=${ignore_md5} --over-ride=${over_ride}"

  if [[ ${ignore_md5} -eq 1 ]]; then
    if [[ ${over_ride} -eq 1 ]]; then
      write_green "Executing>> rm -f ${this_file} >> /dev/null 2>&1"
      rm -f ${this_file} >> /dev/null 2>&1
    fi
    write_green "Executing>> curl ${this_gzip} -o ${this_file}"
    curl ${this_gzip} -o ${this_file}
    write_green "Executing>> chown :users ${this_file}"
    chown :users ${this_file}
  else
    write_green "Executing>> rm -f ${this_dir}/MD5SUMS >> /dev/null 2>&1"
    rm -f ${this_dir}/MD5SUMS >> /dev/null 2>&1
    write_green "Executing>> curl ${def_server}/MD5SUMS -o ${this_dir}/MD5SUMS"
    curl ${def_server}/MD5SUMS -o ${this_dir}/MD5SUMS
    write_green "Executing>> chown :users ${this_dir}/MD5SUMS"
    chown :users ${this_dir}/MD5SUMS
    if [[ ${over_ride} -eq 1 ]]; then
      write_green "Executing>> rm -f ${this_file} >> /dev/null 2>&1"
      rm -f ${this_file} >> /dev/null 2>&1
    fi
    write_green "Executing>> curl ${this_gzip} -o ${this_file}"
    curl ${this_gzip} -o ${this_file}
    write_green "Executing>> chown :users ${this_file}"
    chown :users ${this_file}

    write_green "Executing>> rem_chk=\`grep -i $(basename ${this_file}) ${this_dir}/MD5SUMS | cut -d' ' -f1\`"
    rem_chk=`grep -i $(basename ${this_file}) ${this_dir}/MD5SUMS | cut -d' ' -f1`
    write_green "Executing>> loc_chk=\`md5sum ${this_file} | cut -d' ' -f1\`"
    loc_chk=`md5sum ${this_file} | cut -d' ' -f1`
    write_green "Executing>> if [ -z \${rem_chk} ]; then write_red \"<WARNING> ${this_file} has no known checksum\"; else if [ \${rem_chk} == \${loc_chk} ]; then echo \"${this_file} is valid\"; else write_red \"<ERROR> ${this_file} is invalid\"; fi; fi"
    if [[ -z ${rem_chk} ]]; then write_red "<WARNING> ${this_file} has no known checksum"; else if [[ ${rem_chk} == ${loc_chk} ]]; then echo "${this_file} is valid"; else write_red "<ERROR> ${this_file} is invalid"; fi; fi
    write_green "Executing>> chown -R ${def_owner} ${this_dir}"
    chown -R ${def_owner} ${this_dir}
  fi
fi


# +
# exit
# -
exit 0
