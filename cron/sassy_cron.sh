#!/bin/sh


# +
#
# Name:        sassy_cron.sh
# Description: SASSYy cron
# Author:      Phil Daly (pndaly@arizona.edu)
# Date:        20200605
# Execute:     % bash sassy_cron.sh --help
#
# -


# +
# set defaults: edit as you see fit
# -
HERE=${PWD}
PARENT=$(dirname "${HERE}")

def_begin=$(date --date="yesterday" +%Y-%m-%dT%H:%M:%S.000000)
def_end=$(date --date="today" +%Y-%m-%dT%H:%M:%S.000000)
def_radius=60.0
def_rb_min=0.5
def_rb_max=1.0


# +
# set defaults: do not edit
# -
dry_run=0


# +
# utility functions
# -
write_blue () {
  printf "\033[0;34m${1}\033[0m\n"
}

write_red () {
  printf "\033[0;31m${1}\033[0m\n"
}

write_yellow () {
  printf "\033[0;33m${1}\033[0m\n"
}

write_green () {
  printf "\033[0;32m${1}\033[0m\n"
}

write_cyan () {
  printf "\033[0;36m${1}\033[0m\n"
}

write_magenta () {
  printf "\033[0;35m${1}\033[0m\n"
}

usage () {
  write_blue   ""                                                                                          2>&1
  write_blue   "SASSy Cron Control"                                                                        2>&1
  write_blue   ""                                                                                          2>&1
  write_green  "Use:"                                                                                      2>&1
  write_green  " %% bash $0 [--dry-run]"                                                                   2>&1
  write_yellow ""                                                                                          2>&1
  write_yellow "Input(s):"                                                                                 2>&1
  write_yellow "  --begin=<str>,    where <str> is an ISOT time string,             default=${def_begin}"  2>&1
  write_yellow "  --end=<str>,      where <str> is an ISOT time string,             default=${def_end}"    2>&1
  write_yellow "  --radius=<float>, where <float> is a cone search radius (asec),   default=${def_radius}" 2>&1
  write_yellow "  --rb-min=<float>, where <float> is the minimum real-bogus score,  default=${def_rb_min}" 2>&1
  write_yellow "  --rb-max=<float>, where <float> is the maximum real-bogus score,  default=${def_rb_max}" 2>&1
  write_yellow ""                                                                                          2>&1
  write_cyan   "Flag(s):"                                                                                  2>&1
  write_cyan   "  --dry-run        show (but do not execute) commands,    default=false"                   2>&1
  write_cyan   ""                                                                                          2>&1
}


# +
# check command line argument(s) 
# -
while test $# -gt 0; do
  case "${1}" in
    --begin*)
      begin=$(echo $1 | cut -d'=' -f2)
      shift
      ;;
    --end*)
      end=$(echo $1 | cut -d'=' -f2)
      shift
      ;;
    --radius*)
      radius=$(echo $1 | cut -d'=' -f2)
      shift
      ;;
    --rb-min*)
      rb_min=$(echo $1 | cut -d'=' -f2)
      shift
      ;;
    --rb-max*)
      rb_max=$(echo $1 | cut -d'=' -f2)
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
[[ -z ${begin} ]]   && begin=${def_begin}
[[ -z ${end} ]]     && end=${def_end}
[[ -z ${radius} ]]  && radius=${def_radius}
[[ -z ${rb_min} ]]  && rb_min=${def_rb_min}
[[ -z ${rb_max} ]]  && rb_max=${def_rb_max}

[[ ! ${radius} =~ ^[0-9]*\.[0-9]*$ ]] && write_red "<ERROR> radius ${radius} is invalid!" && exit 0
[[ ! ${rb_min} =~ ^[0-9]*\.[0-9]*$ ]] && write_red "<ERROR> rb_min ${rb_min} is invalid!" && exit 0
[[ ! ${rb_max} =~ ^[0-9]*\.[0-9]*$ ]] && write_red "<ERROR> rb_max ${rb_max} is invalid!" && exit 0


# +
# execute (dry-run)
# -
write_blue "%% bash $0 --begin=${begin} --end=${end} --radius=${radius} --rb-min=${rb_min} --rb-max=${rb_max} --dry-run=${dry_run}"
_args="--begin=${begin} --end=${end} --radius=${radius} --rb-min=${rb_min} --rb-max=${rb_max} --verbose" 
if [[ ${dry_run} -eq 1 ]]; then
  write_yellow "Dry-Run>> source ${PARENT}/etc/Sassy.sh ${PARENT}"
  write_yellow "Dry-Run>> PYTHONPATH=${PARENT}:${PARENT}/src python3 ${PARENT}/src/utils/sassy_cron.py ${_args}"


# +
# execute (for-real)
# -
else
  write_green "Executing>> source ${PARENT}/etc/Sassy.sh ${PARENT}"
  source ${PARENT}/etc/Sassy.sh ${PARENT}
  write_green "Executing>> PYTHONPATH=${PARENT}:${PARENT}/src python3 ${PARENT}/src/utils/sassy_cron.py ${_args}"
  PYTHONPATH=${PARENT}:${PARENT}/src python3 ${PARENT}/src/utils/sassy_cron.py ${_args}
fi


# +
# exit
# -
exit 0
