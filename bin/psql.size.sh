#!/bin/sh


# +
#
# Name:        psql.size.sh
# Description: returns PostGresQL database size
# Author:      Phil Daly (pndaly@email.arizona.edu)
# Date:        20181205
# Execute:     % bash psql.size.sh --help
#
# -


# +
# set defaults: edit as you see fit
# -
today=$(date "+%Y%m%d")
default_authorization="sassy:S@ssy_520"
default_database="sassy"
default_server="localhost"
default_port=5432
default_table=""

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
  write_blue   ""                                                                                                             2>&1
  write_blue   "Return size of PostGreSQL database or table"                                                                  2>&1
  write_blue   ""                                                                                                             2>&1
  write_green  "Use:"                                                                                                         2>&1
  write_green  " %% bash $0 --authorization=<str> --database=<str> --port=<int> --server=<address> --table=<str> [--dry-run]" 2>&1
  write_green  ""                                                                                                             2>&1
  write_yellow "Input(s):"                                                                                                    2>&1
  write_yellow "  --authorization=<str>, where <str> is of the form 'username:password',  default=${default_authorization}"   2>&1
  write_yellow "  --database=<str>,      where <str> is a database name,                  default=${default_database}"        2>&1
  write_yellow "  --port=<int>,          where <int> is a port number,                    default=${default_port}"            2>&1
  write_yellow "  --server=<address>,    where <address> is a hostname or IP-address,     default=${default_server}"          2>&1
  write_yellow "  --table=<str>,         where <str> is a database table,                 default=${default_table}"           2>&1
  write_yellow ""                                                                                                             2>&1
  write_cyan   "Flag(s):"                                                                                                     2>&1
  write_cyan   "  --dry-run,             show (but do not execute) commands,              default=false"                      2>&1
  write_cyan   ""                                                                                                             2>&1
  echo         "Output(s):"                                                                                                   2>&1
  echo         "  size of database or table"                                                                                  2>&1
  echo         ""                                                                                                             2>&1
}


# +
# check command line argument(s) 
# -
while test $# -gt 0; do
  case "${1}" in
    --authorization*|--AUTHORIZATION*)
      rs_authorization=$(echo $1 | cut -d'=' -f2)
      shift
      ;;
    --database*|--DATABASE*)
      rs_database=$(echo $1 | cut -d'=' -f2)
      shift
      ;;
    --dry-run|--DRY-RUN)
      dry_run=1
      shift
      ;;
    --port*|--PORT*)
      rs_port=$(echo $1 | cut -d'=' -f2)
      shift
      ;;
    --server*|--SERVER*)
      rs_server=$(echo $1 | cut -d'=' -f2)
      shift
      ;;
    --table*|--TABLE*)
      rs_table=$(echo $1 | cut -d'=' -f2)
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
[[ -z ${rs_authorization} ]] && rs_authorization=${default_authorization}
[[ -z ${rs_database} ]] && rs_database=${default_database}
[[ -z ${rs_port} ]] && rs_port=${default_port}
[[ -z ${rs_server} ]] && rs_server=${default_server}


rs_username=$(echo ${rs_authorization} | cut -d':' -f1)
rs_password=$(echo ${rs_authorization} | cut -d':' -f2)


# +
# check input(s)
# -
if [[ ${rs_server} != "localhost" ]]; then
  if ! ping -c 1 -w 5 ${rs_server} &>/dev/null; then
    write_red "<ERROR> server (${rs_server}) is down ... exiting"
    exit 0
  fi
fi

if [[ -z ${rs_password} ]]; then
  write_red "<ERROR> invalid password (${rs_password}) ... exiting"
  exit 0 
fi

if [[ -z ${rs_username} ]]; then
  write_red "<ERROR> invalid username (${rs_username}) ... exiting"
  exit 0 
fi

if [[ -z ${rs_table} ]]; then
  _command="SELECT pg_size_pretty(pg_database_size('${rs_database}'));"
else
  _command="SELECT pg_size_pretty(pg_total_relation_size('${rs_table}'));"
fi


# +
# execute (dry-run)
# -
write_blue "%% bash $0 --authorization=${rs_username}:${rs_password} --database=${rs_database} --port=${rs_port} --server=${rs_server} --table=${rs_table} --dry-run=${dry_run}"
if [[ ${dry_run} -eq 1 ]]; then
  write_yellow "Dry-Run>> PGPASSWORD=${rs_password} psql -h ${rs_server} -p ${rs_port} -U ${rs_username} -d ${rs_database} -c \"${_command}\""

# +
# execute (for-real)
# -
else
  write_green "Executing>> PGPASSWORD=${rs_password} psql -h ${rs_server} -p ${rs_port} -U ${rs_username} -d ${rs_database} -c \"${_command}\""
  _response=$(PGPASSWORD=${rs_password} psql -h ${rs_server} -p ${rs_port} -U ${rs_username} -d ${rs_database} -c "${_command}" 2>/dev/null)
  if [[ ! -z "${_response}" ]]; then
    if [[ -z ${rs_table} ]]; then
      echo 'Database is '$(echo ${_response} | cut -d' ' -f3)' '$(echo ${_response} | cut -d' ' -f4)
    else
      echo 'Table is '$(echo ${_response} | cut -d' ' -f3)' '$(echo ${_response} | cut -d' ' -f4)
    fi
  else
    if [[ -z ${rs_table} ]]; then
      write_red "<ERROR> invalid access to table (${rs_table}) on server (${rs_server}:${rs_port}) using authorization (${rs_username}:${rs_password}) ... exiting"
    else
      write_red "<ERROR> invalid access to database (${rs_database}) on server (${rs_server}:${rs_port}) using authorization (${rs_username}:${rs_password}) ... exiting"
    fi
  fi
fi


# +
# exit
# -
exit 0
