#!/bin/sh


# +
#
# Name:        Sassy.sh
# Description: Sassy control
# Author:      Phil Daly (pndaly@email.arizona.edu)
# Date:        20190411
# Execute:     % bash Sassy.sh --help
#
# -


# +
# default(s)
# -
_sassy_home=$(env | grep '^SASSY_HOME=' | cut -d'=' -f2)
def_sassy_command="status"
def_sassy_source="${_sassy_home}"
def_sassy_type="dev"

def_dev_host="localhost"
def_dev_port=5000
def_prd_host="localhost"
def_prd_port=6000

dry_run=0


# +
# variable(s)
# -
sassy_command="${def_sassy_command}"
sassy_source="${def_sassy_source}"
sassy_type="${def_sassy_type}"

sassy_port=${def_dev_port}
sassy_host="${def_dev_host}"


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
  write_blue   ""                                                                                                2>&1
  write_blue   "Sassy Control"                                                                                   2>&1
  write_blue   ""                                                                                                2>&1
  write_green  "Use:"                                                                                            2>&1
  write_green  "  %% bash $0 --command=<str> --source=<str> --type=<str> [--dry-run]"                            2>&1
  write_yellow ""                                                                                                2>&1
  write_yellow "Input(s):"                                                                                       2>&1
  write_yellow "  --command=<str>,  where <str> is { 'start', 'status', 'stop' },  default=${def_sassy_command}" 2>&1
  write_yellow "  --source=<str>,   where <str> is source code directory,          default=${def_sassy_source}"  2>&1
  write_yellow "  --type=<str>,     where <str> is { 'dev', 'prod' }               default=${def_sassy_type}"    2>&1
  write_yellow ""                                                                                                2>&1
  write_cyan   "Flag(s):"                                                                                        2>&1
  write_cyan   " --dry-run,         show (but do not execute) commands,            default=false"                2>&1
  write_cyan   ""                                                                                                2>&1
}


# +
# check command line argument(s) 
# -
while test $# -gt 0; do
  case "${1}" in
    --command*|--COMMAND*)
      sassy_command=$(echo $1 | cut -d'=' -f2)
      shift
      ;;
    --dry-run|--DRY-RUN)
      dry_run=1
      shift
      ;;
    --source*|--SOURCE*)
      sassy_source=$(echo $1 | cut -d'=' -f2)
      shift
      ;;
    --type*|--TYPE*)
      sassy_type=$(echo $1 | cut -d'=' -f2)
      shift
      ;;
    --help|*)
      usage
      exit 0
      ;;
  esac
done


# +
# check and (re)set variable(s)
# -
case $(echo ${sassy_command} | tr '[A-Z]' '[a-z]') in
  start*|status*|stop*)
    ;;
  *)
    sassy_command=${def_sassy_command}
    ;;
esac


if [[ ! -d ${sassy_source} ]]; then
  write_red "<ERROR> directory (${sassy_source}) is unknown ... exiting"
  exit 0 
fi


case $(echo ${sassy_type} | tr '[A-Z]' '[a-z]') in
  prod*)
    sassy_type="production"
    sassy_host=$(getent hosts ${def_prd_host} | cut -d' ' -f1)
    sassy_port=${def_prd_port}
    ;;
  *)
    sassy_type="development"
    sassy_host="${def_dev_host}"
    sassy_port=${def_dev_port}
    ;;
esac


if [[ ${sassy_host} != "localhost" ]]; then
  if ! ping -c 1 -w 5 ${sassy_host} &>/dev/null; then
    write_red "<ERROR> server (${sassy_host}) is down ... exiting"
    exit 0
  fi
fi


# +
# env(s)
# -
_pythonpath=$(env | grep PYTHONPATH | cut -d'=' -f2)
if [[ -z "${_pythonpath}" ]]; then
  export PYTHONPATH=`pwd`
fi
write_blue "%% source ${sassy_source}/etc/Sassy.sh ${sassy_source} ${sassy_type}"
source ${sassy_source}/etc/Sassy.sh ${sassy_source} ${sassy_type}


# +
# execute (dry-run)
# -
write_blue "%% bash $0 --command=${sassy_command} --dry-run=${dry_run} --source=${sassy_source} --type=${sassy_type}"
case $(echo ${sassy_command} | tr '[A-Z]' '[a-z]') in
  start*)
    if [[ ${dry_run} -eq 1 ]]; then
      if [[ "${sassy_type}" == "development" ]]; then
        write_yellow "Dry-Run> FLASK_DEBUG=True  FLASK_ENV=Development FLASK_APP=${sassy_source}/source/app.py flask run"
      elif [[ "${sassy_type}" == "production" ]]; then
        write_yellow "Dry-Run> FLASK_DEBUG=False FLASK_ENV=Production  FLASK_APP=${sassy_source}/source/app.py flask run -h ${sassy_host} -p ${sassy_port}"
      fi
    else
      if [[ "${sassy_type}" == "development" ]]; then
        write_green "Executing> FLASK_DEBUG=True  FLASK_ENV=Development FLASK_APP=${sassy_source}/source/app.py flask run"
        FLASK_DEBUG=True  FLASK_ENV=Development FLASK_APP=${sassy_source}/source/app.py flask run
      elif [[ "${sassy_type}" == "production" ]]; then
        write_green "Executing> FLASK_DEBUG=False FLASK_ENV=Production  FLASK_APP=${sassy_source}/source/app.py flask run -h ${sassy_host} -p ${sassy_port}"
        FLASK_DEBUG=False FLASK_ENV=Production  FLASK_APP=${sassy_source}/source/app.py flask run -h ${sassy_host} -p ${sassy_port}
      fi
    fi
    ;;

  stop*)
    _pid=$(ps -ef | pgrep -f 'python' | pgrep  -f flask)
    if [[ ! -z "${_pid}" ]]; then
      if [[ ${dry_run} -eq 1 ]]; then
        write_yellow "Dry-Run> kill -9 ${_pid}"
      else
        write_green "Executing> kill -9 ${_pid}"
        kill -9 ${_pid}
      fi
    fi
    ;;

  status*)
      if [[ ${dry_run} -eq 1 ]]; then
        write_yellow "Dry-Run> ps -ef | grep -i python | grep -i flask"
      else
        write_green "Executing> ps -ef | grep -i python | grep -i flask"
        ps -ef | grep -i python | grep -i flask
      fi
    ;;
esac


# +
# exit
# -
exit 0
