#!/bin/sh


# +
#
# Name:        sassy.tns.sh
# Description: SASSY TNS Control
# Author:      Phil Daly (pndaly@email.arizona.edu)
# Date:        20190415
# Execute:     % bash sassy.tns.sh --help
#
# -


# +
# default(s) - edit as required
# -
def_db_name="sassy"
def_db_pass="db_secret"
def_db_host="localhost:5432"
def_db_user="sassy"

dry_run=0


# +
# variable(s)
# -
sassy_db_name="${def_db_name}"
sassy_db_pass="${def_db_pass}"
sassy_db_host="${def_db_host}"
sassy_db_user="${def_db_user}"


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
  write_blue   ""                                                                                                 2>&1
  write_blue   "SASSY TNS Control"                                                                                2>&1
  write_blue   ""                                                                                                 2>&1
  write_green  "Use:"                                                                                             2>&1
  write_green  "  %% bash $0 --database=<str> --hostname=<str:int> --password=<str> --username=<str> [--dry-run]" 2>&1
  write_yellow ""                                                                                                 2>&1
  write_yellow "Input(s):"                                                                                        2>&1
  write_yellow "  --database=<str>,      where <str> is the database name,               default=${def_db_name}"  2>&1
  write_yellow "  --hostname=<str:int>,  where <str> is the database hostname and port,  default=${def_db_host}"  2>&1
  write_yellow "  --password=<str>,      where <str> is the database password,           default=${def_db_pass}"  2>&1
  write_yellow "  --username=<str>,      where <str> is the database username,           default=${def_db_user}"  2>&1
  write_yellow ""                                                                                                 2>&1
  write_cyan   "Flag(s):"                                                                                         2>&1
  write_cyan   "  --dry-run,             show (but do not execute) commands,             default=false"           2>&1
  write_cyan   ""                                                                                                 2>&1
}


# +
# check command line argument(s) 
# -
while test $# -gt 0; do
  case "${1}" in
    --database*|--DATABASE*)
      sassy_db_name=$(echo $1 | cut -d'=' -f2)
      shift
      ;;
    --dry-run|--DRY-RUN)
      dry_run=1
      shift
      ;;
    --password*|--PASSWORD*)
      sassy_db_pass=$(echo $1 | cut -d'=' -f2)
      shift
      ;;
    --username*|--USERNAME*)
      sassy_db_user=$(echo $1 | cut -d'=' -f2)
      shift
      ;;
    --hostname*|--HOSTNAME*)
      sassy_db_host=$(echo $1 | cut -d'=' -f2)
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
if [[ -z ${sassy_db_name} ]]; then
  sassy_db_name=${def_db_name}
fi
if [[ -z ${sassy_db_host} ]]; then
  sassy_db_host=${def_db_host}
fi
if [[ -z ${sassy_db_pass} ]]; then
  sassy_db_pass=${def_db_pass}
fi
if [[ -z ${sassy_db_user} ]]; then
  sassy_db_user=${def_db_user}
fi


# +
# write file to create database
# -
_host=$(echo ${sassy_db_host} | cut -d':' -f1)
_port=$(echo ${sassy_db_host} | cut -d':' -f2)
PSQL_CMD="PGPASSWORD=\"${sassy_db_pass}\" psql --echo-all -h ${_host} -p ${_port} -U ${sassy_db_user} -d ${sassy_db_name}"
if [[ -f /tmp/sassy.tns.sh ]]; then
  rm -f /tmp/sassy.tns.sh
fi


# +
# create table
# -
echo "Creating /tmp/sassy.tns.sh"
echo "#!/bin/sh"                            >> /tmp/sassy.tns.sh 2>&1
echo ""                                     >> /tmp/sassy.tns.sh 2>&1
echo "${PSQL_CMD} << END_TABLE"             >> /tmp/sassy.tns.sh 2>&1
echo "DROP TABLE IF EXISTS tns;"            >> /tmp/sassy.tns.sh 2>&1
echo "CREATE TABLE tns ("                   >> /tmp/sassy.tns.sh 2>&1
echo "  id serial PRIMARY KEY,"             >> /tmp/sassy.tns.sh 2>&1
echo "  tns_id INTEGER,"                    >> /tmp/sassy.tns.sh 2>&1
echo "  tns_name VARCHAR(128) NOT NULL,"    >> /tmp/sassy.tns.sh 2>&1
echo "  tns_link VARCHAR(128),"             >> /tmp/sassy.tns.sh 2>&1
echo "  ra double precision,"               >> /tmp/sassy.tns.sh 2>&1
echo "  dec double precision,"              >> /tmp/sassy.tns.sh 2>&1
echo "  redshift double precision,"         >> /tmp/sassy.tns.sh 2>&1
echo "  discovery_date TIMESTAMP,"          >> /tmp/sassy.tns.sh 2>&1
echo "  discovery_mag double precision,"    >> /tmp/sassy.tns.sh 2>&1
echo "  discovery_instrument VARCHAR(128)," >> /tmp/sassy.tns.sh 2>&1
echo "  filter_name VARCHAR(32),"           >> /tmp/sassy.tns.sh 2>&1
echo "  tns_class VARCHAR(128),"            >> /tmp/sassy.tns.sh 2>&1
echo "  host VARCHAR(128),"                 >> /tmp/sassy.tns.sh 2>&1
echo "  host_z double precision,"           >> /tmp/sassy.tns.sh 2>&1
echo "  source_group VARCHAR(128),"         >> /tmp/sassy.tns.sh 2>&1
echo "  alias VARCHAR(128),"                >> /tmp/sassy.tns.sh 2>&1
echo "  certificate VARCHAR(128));"         >> /tmp/sassy.tns.sh 2>&1
echo "END_TABLE"                            >> /tmp/sassy.tns.sh 2>&1
echo ""                                     >> /tmp/sassy.tns.sh 2>&1


# +
# execute
# -
_user=$(env | grep '^USER=')
write_blue "%% bash $0 --database=${sassy_db_name} --hostname=${sassy_db_host} --password=${sassy_db_pass} --username=${sassy_db_user} --dry-run=${dry_run}"
if [[ ${dry_run} -eq 1 ]]; then
  if [[ "${_user}" != "root" ]]; then
    write_red "WARNING: you need to be root to execute these commands!"
  fi
  if [[ ! -f /tmp/sassy.tns.sh ]]; then
    write_red "WARNING: /tmp/sassy.tns.sh does not exist!"
  fi
  write_yellow "Dry-Run> chmod a+x /tmp/sassy.tns.sh"
  write_yellow "Dry-Run> bash /tmp/sassy.tns.sh"
  write_yellow "Dry-Run> rm -f /tmp/sassy.tns.sh"

else
  if [[ "${_user}" != "root" ]]; then
    write_red "ERROR: you need to be root to execute these commands!"
    usage
    exit
  fi
  if [[ ! -f /tmp/sassy.tns.sh ]]; then
    write_red "ERROR: /tmp/sassy.tns.sh does not exist!"
    usage
    exit
  fi
  write_green "Executing> chmod a+x /tmp/sassy.tns.sh"
  chmod a+x /tmp/sassy.tns.sh
  write_green "Executing> bash /tmp/sassy.tns.sh"
  bash /tmp/sassy.tns.sh
  write_green "Executing> rm -f /tmp/sassy.tns.sh"
  rm -f /tmp/sassy.tns.sh
fi


# +
# exit
# -
exit 0
