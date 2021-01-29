#!/bin/sh


# +
# edit as you see fit
# -
_user=$(env | grep USERNAME | cut -d'=' -f2)
if [[ -z "${_user}" ]]; then
  export USERNAME="sassy"
fi

export SASSY_HOME=${1:-${PWD}}
export SASSY_TYPE=${2:-""}

case ${SASSY_TYPE} in
  dev*|DEV*)
    export SASSY_APP_HOST=localhost
    export SASSY_APP_PORT=5000
    export SASSY_DB_HOST=localhost
    export SASSY_APP_URL="http://${SASSY_APP_HOST}:${SASSY_APP_PORT}/sassy"
    ;;
  prod*|PROD*)
    export SASSY_APP_HOST=$(hostname)
    export SASSY_APP_PORT=6000
    export SASSY_DB_HOST=$(hostname)
    export SASSY_APP_URL="http://${SASSY_APP_HOST}:${SASSY_APP_PORT}/sassy"
    ;;
  *)
    export SASSY_APP_HOST="127.0.0.1"
    export SASSY_APP_PORT=80
    export SASSY_DB_HOST="127.0.0.1"
    export SASSY_APP_URL="https://${SASSY_APP_HOST}/sassy"
    ;;
esac


export SASSY_DB_PORT=5432
export SASSY_DB_NAME="sassy"
export SASSY_DB_USER="sassy"
export SASSY_DB_PASS="db_secret"


# +
# env(s)
# -
export SASSY_BIN=${SASSY_HOME}/bin
export SASSY_CRON=${SASSY_HOME}/cron
export SASSY_ETC=${SASSY_HOME}/etc
export SASSY_LOGS=${SASSY_HOME}/logs
export SASSY_SRC=${SASSY_HOME}/src
export SASSY_TTF=${SASSY_HOME}/ttf


# +
# data path(s)
# -
export SASSY_ZTF_ARCHIVE=/dataraid6/backups:/data/backups
export SASSY_ZTF_DATA=/dataraid6/ztf:/data/ztf
export SASSY_ZTF_AVRO=/dataraid6/ztf:/data/ztf


# +
# PYTHONPATH
# -
export PYTHONPATH=${SASSY_HOME}:${SASSY_SRC}
