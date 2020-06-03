#!/bin/sh


# +
#
# Name:        psql.cleanup.sh
# Description: cleanup a PostGresQL database
# Author:      Phil Daly (pndaly@email.arizona.edu)
# Date:        20181205
# Execute:     % bash psql.cleanup.sh --help
#
# -


# +
# set defaults: edit as you see fit
# -
today=$(date "+%Y%m%d")
default_authorization="sassy:S@ssy_520"
default_database="sassy"
default_port=5432
default_server="localhost"
default_table=""

dry_run=0


# +
# env(s)
# -
export PATH=/usr/lib/postgresql/10/bin:${PATH}
export PATH=/usr/lib/postgresql/11/bin:${PATH}


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
  write_blue   "Cleanup a PostGreSQL database"                                                                                2>&1
  write_blue   ""                                                                                                             2>&1
  write_green  "Use:"                                                                                                         2>&1
  write_green  " %% bash $0 --authorization=<str> --database=<str> --port=<int> --server=<address> --table=<str> [--dry-run]" 2>&1
  write_yellow ""                                                                                                             2>&1
  write_yellow "Input(s):"                                                                                                    2>&1
  write_yellow "  --authorization=<str>, where <str> is of the form 'username:password',  default=${default_authorization}"   2>&1
  write_yellow "  --database=<str>,      where <str> is a database name,                  default=${default_database}"        2>&1
  write_yellow "  --port=<int>,          where <int> is a port number,                    default=${default_port}"            2>&1
  write_yellow "  --server=<address>,    where <address> is a hostname or IP-address,     default=${default_server}"          2>&1
  write_yellow "  --table=<str>,         where <str> is a table name within the database, default=${default_table}"           2>&1
  write_yellow ""                                                                                                             2>&1
  write_cyan   "Flag(s):"                                                                                                     2>&1
  write_cyan   "  --dry-run,             show (but do not execute) commands,              default=false"                      2>&1
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
write_blue "%% bash $0 --authorization=${rs_username}:${rs_password} --database=${rs_database} --port=${rs_port} --server=${rs_server} --table=${rs_table} --dry-run=${dry_run}"
if [[ ${dry_run} -eq 1 ]]; then
  write_yellow "Dry-Run>> PGPASSWORD=${rs_password} psql -h ${rs_server} -p ${rs_port} -U ${rs_username} -d ${rs_database} ${rs_table} -c 'VACUUM(FULL, ANALYZE, VERBOSE) ${rs_table};'"

  if [[ ! -z ${rs_table} ]]; then
    write_yellow "Dry-Run>> PGPASSWORD=${rs_password} psql -h ${rs_server} -p ${rs_port} -U ${rs_username} -d ${rs_database} ${rs_table} -c 'REINDEX TABLE ${rs_table};'"
    write_yellow "Dry-Run>> PGPASSWORD=${rs_password} psql -h ${rs_server} -p ${rs_port} -U ${rs_username} -d ${rs_database} ${rs_table} -c 'VACUUM(FULL, ANALYZE, VERBOSE) ${rs_table};'"
  fi

# +
# execute (for-real)
# -
else
  write_green "Executing>> PGPASSWORD=${rs_password} psql -h ${rs_server} -p ${rs_port} -U ${rs_username} -d ${rs_database} ${rs_table} -c 'VACUUM(FULL, ANALYZE, VERBOSE) ${rs_table};'"
  PGPASSWORD=${rs_password} psql -h ${rs_server} -p ${rs_port} -U ${rs_username} -d ${rs_database} ${rs_table} -c "VACUUM(FULL, ANALYZE, VERBOSE) ${rs_table};"

  if [[ ! -z ${rs_table} ]]; then
    write_green "Executing>> PGPASSWORD=${rs_password} psql -h ${rs_server} -p ${rs_port} -U ${rs_username} -d ${rs_database} ${rs_table} -c 'REINDEX TABLE ${rs_table};'"
    PGPASSWORD=${rs_password} psql -h ${rs_server} -p ${rs_port} -U ${rs_username} -d ${rs_database} ${rs_table} -c "REINDEX TABLE ${rs_table};"
    write_green "Executing>> PGPASSWORD=${rs_password} psql -h ${rs_server} -p ${rs_port} -U ${rs_username} -d ${rs_database} ${rs_table} -c 'VACUUM(FULL, ANALYZE, VERBOSE) ${rs_table};'"
    PGPASSWORD=${rs_password} psql -h ${rs_server} -p ${rs_port} -U ${rs_username} -d ${rs_database} ${rs_table} -c "VACUUM(FULL, ANALYZE, VERBOSE) ${rs_table};"
  fi
fi


# +
# exit
# -
exit 0
