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
default_authorization="sassy:db_secret"
default_database="sassy"
default_server="localhost"
default_port=5432

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
  write_blue   ""                                                                                                           2>&1
  write_blue   "Return size of PostGreSQL database"                                                                         2>&1
  write_blue   ""                                                                                                           2>&1
  write_green  "Use:"                                                                                                       2>&1
  write_green  " %% bash $0 --authorization=<str> --database=<str> --server=<address> [--dry-run]"                          2>&1
  write_green  ""                                                                                                           2>&1
  write_yellow "Input(s):"                                                                                                  2>&1
  write_yellow "  --authorization=<str>, where <str> is of the form 'username:password',  default=${default_authorization}" 2>&1
  write_yellow "  --database=<str>,      where <str> is a database name,                  default=${default_database}"      2>&1
  write_yellow "  --port=<int>,          where <int> is a port number,                    default=${default_port}"          2>&1
  write_yellow "  --server=<address>,    where <address> is a hostname or IP-address,     default=${default_server}"        2>&1
  write_yellow ""                                                                                                           2>&1
  write_cyan   "Flag(s):"                                                                                                   2>&1
  write_cyan   "  --dry-run,             show (but do not execute) commands,              default=false"                    2>&1
  write_cyan   ""                                                                                                           2>&1
  echo         "Output(s):"                                                                                                 2>&1
  echo         "  size of database"                                                                                         2>&1
  echo         ""                                                                                                           2>&1
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
    --help|*)
      usage
      exit 0
      ;;
  esac
done


# +
# check and (re)set variable(s)
# -
if [[ -z ${rs_authorization} ]]; then
  rs_authorization=${default_authorization}
fi

if [[ -z ${rs_database} ]]; then
  rs_database=${default_database}
fi

if [[ -z ${rs_port} ]]; then
  rs_port=${default_port}
fi

if [[ -z ${rs_server} ]]; then
  rs_server=${default_server}
fi

rs_username=$(echo ${rs_authorization} | cut -d':' -f1)
rs_password=$(echo ${rs_authorization} | cut -d':' -f2)


# +
# check input(s)
# -
if ! ping -c 1 -w 5 ${rs_server} &>/dev/null; then 
  write_red "<ERROR> server (${rs_server}) is down ... exiting"
  exit 0 
fi

if [[ -z "${rs_password}" ]]; then
  write_red "<ERROR> invalid password (${rs_password}) ... exiting"
  exit 0 
fi

if [[ -z "${rs_username}" ]]; then
  write_red "<ERROR> invalid username (${rs_username}) ... exiting"
  exit 0 
fi


# +
# execute (dry-run)
# -
if [[ ${dry_run} -eq 1 ]]; then
  write_green "%% bash $0 -a=${rs_username}:${rs_password} -d=${rs_database} -p=${rs_port} -s=${rs_server} -n=${dry_run}"
  write_yellow "Dry-Run>> PGPASSWORD=${rs_password} psql -h ${rs_server} -p ${rs_port} -U ${rs_username} -d ${rs_database} -c \"SELECT pg_size_pretty(pg_database_size('${rs_database}'));\""

# +
# execute (for-real)
# -
else
  write_blue "%% bash $0 -a=${rs_username}:${rs_password} -d=${rs_database} -p=${rs_port} -s=${rs_server} -n=${dry_run}"
  write_yellow "Executing>> PGPASSWORD=${rs_password} psql -h ${rs_server} -p ${rs_port} -U ${rs_username} -d ${rs_database} -c \"SELECT pg_size_pretty(pg_database_size('${rs_database}'));\""
  _response=$(PGPASSWORD=${rs_password} psql -h ${rs_server} -p ${rs_port} -U ${rs_username} -d ${rs_database} -c "SELECT pg_size_pretty(pg_database_size('${rs_database}'));" 2>/dev/null)
  if [[ ! -z "${_response}" ]]; then
    echo 'Database is '$(echo ${_response} | cut -d' ' -f3)' '$(echo ${_response} | cut -d' ' -f4)
  else
    write_red "<ERROR> invalid access to database (${rs_database}) on server (${rs_server}:${rs_port}) using authorization (${rs_username}:${rs_password}) ... exiting"
  fi
fi


# +
# exit
# -
exit 0
