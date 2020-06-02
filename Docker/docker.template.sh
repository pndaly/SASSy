#!/bin/bash


# +
#
# Name:        docker.sh
# Description: Docker Control
# Author:      Phil Daly (pndaly@arizona.edu)
# Date:        20200317
# Execute:     % bash docker.sh --help
#
# -


# +
# default(s)
# -
def_cmnd="list"
def_file="Dockerfile"
def_name="xx_$$_xx"
def_port=5432
def_dtag="$$:sassy"
dry_run=0
verbose=0


# +
# auxiliary function(s)
# -
write_red () { 
  printf "\033[0;31m${1}\033[0m\n"
}

write_green () { 
  printf "\033[0;32m${1}\033[0m\n"
}

write_yellow () { 
  printf "\033[0;33m${1}\033[0m\n"
}

write_blue () { 
  printf "\033[0;34m${1}\033[0m\n"
}

write_magenta () { 
  printf "\033[0;35m${1}\033[0m\n"
}

write_cyan () { 
  printf "\033[0;36m${1}\033[0m\n"
}

usage () {
  write_blue   ""                                                                                                                      2>&1
  write_blue   "Docker Control"                                                                                                        2>&1
  write_blue   ""                                                                                                                      2>&1
  write_green  "Use:"                                                                                                                  2>&1
  write_green  "  %% bash ${0} --command=<str> --name=<str> [--dry-run]"                                                               2>&1
  write_yellow ""                                                                                                                      2>&1
  write_yellow "Input(s):"                                                                                                             2>&1
  write_yellow "  --command=<str>,   { build | connect | create | list | pull | remove | start | status | stop }, default=${def_cmnd}" 2>&1
  write_yellow "  --file=<str>,      build file,                                                                  default=${def_file}" 2>&1
  write_yellow "  --name=<str>,      unique (container or image) name,                                            default=${def_name}" 2>&1
  write_yellow "  --port=<int>,      port to expose,                                                              default=${def_port}" 2>&1
  write_yellow "  --tag=<str>,       build tag,                                                                   default=${def_dtag}" 2>&1
  write_yellow ""                                                                                                                      2>&1
  write_cyan   "Flag(s):"                                                                                                              2>&1
  write_cyan   "  --dry-run,         show (but do not execute) command(s),                                        default=false"       2>&1
  write_cyan   "  --verbose,         be more verbose,                                                             default=false"       2>&1
  write_cyan   ""                                                                                                                      2>&1
}


# +
# get command line argument(s) 
# -
while [[ $# -gt 0 ]]; do
  case "${1}" in
    --command*)
      docker_cmnd=$(echo ${1} | cut -d'=' -f2)
      shift
      ;;
    --file*)
      docker_file=$(echo ${1} | cut -d'=' -f2)
      shift
      ;;
    --name*)
      docker_name=$(echo ${1} | cut -d'=' -f2)
      shift
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    --port*)
      docker_port=$(echo ${1} | cut -d'=' -f2)
      shift
      ;;
    --tag*)
      docker_dtag=$(echo ${1} | cut -d'=' -f2)
      shift
      ;;
    --verbose)
      verbose=1
      shift
      ;;
    --help|*)
      usage
      exit 0
      ;;
  esac
done


# +
# check and (re)set command line argument(s)
# -
[[ -z ${docker_cmnd} ]] && docker_cmnd=${def_cmnd}
[[ -z ${docker_file} ]] && docker_file=${def_file}
[[ -z ${docker_name} ]] && docker_name=${def_name}
[[ -z ${docker_port} ]] && docker_port=${def_port}
[[ -z ${docker_dtag} ]] && docker_dtag=${def_dtag}

docker_cmnd=$(echo ${docker_cmnd} | tr '[A-Z]' '[a-z]')


# +
# variable(s)
# -
_cid_exited=$(docker container ps -a | grep -i ${docker_name} | grep Exited | cut -d' ' -f1)
_cid_up=$(docker container ps -a | grep -i ${docker_name} | grep Up | cut -d' ' -f1)

_num_exited=$(echo ${_cid_exited} | wc -w)
_num_up=$(echo ${_cid_up} | wc -w)


# +
# --verbose=True
# -
if [[ ${verbose} -eq 1 ]]; then
  write_magenta "%% bash $0 --command=${docker_cmnd} --file=${docker_file} --name=${docker_name} --port=${docker_port} \
    --tag=${docker_dtag} --dry-run=${dry_run} --verbose=${verbose}"
  write_magenta "Container IDs in 'Exited' state = ${_cid_exited}"
  write_magenta "Number of containers in 'Exited' state = ${_num_exited}"
  write_magenta "Container IDs in 'Up' state = ${_cid_up}"
  write_magenta "Number of containers in 'Up' state = ${_num_up}"
fi


# +
# supported system(s) - edit as you see fit
# -
_sassy () {
  # _sassy ${dry_run} ${docker_name} ${docker_port}
  #  i docker_name should be something like: sassy/postgres-12:postgis3-q3c2
  if [[ ${verbose} -eq 1 ]]; then
    write_magenta "_sassy(${1}, ${2}, ${3})"
  fi
  if [[ ${1} -eq 1 ]]; then
    write_yellow "Dry-Run>> docker container run -d --name=sassy -p ${3}:5432 -e POSTGRES_USER=sassy \
      -e POSTGRES_PASSWORD=db_secret -e PGDATA=/pgdata -v /home/sassy/pgdata/sassy:/pgdata \
      -v /home/sassy/pgdata/backups:/backups ${2}"
  else
    write_green "Executing>> docker container run -d --name=sassy -p ${3}:5432 -e POSTGRES_USER=sassy \
      -e POSTGRES_PASSWORD=db_secret -e PGDATA=/pgdata -v /home/sassy/pgdata/sassy:/pgdata \
      -v /home/sassy/pgdata/backups:/backups ${2}"
    docker container run -d --name=sassy -p ${3}:5432 -e POSTGRES_USER=sassy -e POSTGRES_PASSWORD=db_secret
      -e PGDATA=/pgdata -v /home/sassy/pgdata/sassy:/pgdata ${2}
  fi
}

_test () {
  # _test ${dry_run}
  if [[ ${verbose} -eq 1 ]]; then
    write_magenta "_test(${1})"
  fi
}


# +
# worker function(s)
# -
_build () {
  # _build ${dry_run} ${docker_file} ${docker_dtag}
  if [[ ${verbose} -eq 1 ]]; then
    write_magenta "_build(${1}, ${2}, ${3})"
  fi
  if [[ ! -f ${2} ]]; then
    write_red "<ERROR> file ${2} does not exist!"
    exit 0
  fi
  if [[ ${1} -eq 1 ]]; then
    write_yellow "Dry-Run>> docker build -f ${2} -t ${3} ."
  else
    write_green "Executing>> docker build -f ${2} -t ${3} ."
    docker build -f ${2} -t ${3} .
  fi
}

_connect () {
  # _connect ${dry_run}
  if [[ ${verbose} -eq 1 ]]; then
    write_magenta "_connect(${1}, ${2}, ${3}, ${4})"
  fi
  # 0 container(s)
  if [[ ${3} -eq 0 ]]; then
    write_red "_connect() <ERROR> no '${2}' container in UP state!"
    exit 0
  # 1 container(s)
  elif [[ ${3} -eq 1 ]]; then
    if [[ ${1} -eq 1 ]]; then
      write_yellow "Dry-Run>> docker exec -it ${4} /bin/bash"
    else
      write_green "Executing>> docker exec -it ${4} /bin/bash"
      docker exec -it ${4} /bin/bash
    fi
  # >1 container(s)
  else
    write_red "_connect() <ERROR> multiple '${2}' containers in UP state!"
    exit 0
  fi
}

_create () {
  # _create ${dry_run} ${docker_name} ${docker_port}
  if [[ ${verbose} -eq 1 ]]; then
    write_magenta "_create(${1}, ${2}, ${3})"
  fi
  # check for existing container with same name
  [[ ! -z $(docker container ps -a | grep -i ${2}) ]] && write_red "_create() <ERROR> '${2}' container already exists!" && exit 0
  # check for existing port use
  [[ ! -z $(ss -tulw | grep ${3}) ]] && write_red "_create() <ERROR> port ${3} already in use!" && exit 0
  # add container
  if [[ "${2}" == "sassy" ]]; then
    _sassy ${1} ${2} ${3}
  elif [[ "${2}" == "test" ]]; then
      _test ${1}
  fi
}

_list () {
  # _list ${dry_run} ${docker_name}
  if [[ ${verbose} -eq 1 ]]; then
    write_magenta "_list(${1}, ${2})"
  fi
  # 0 container(s)
  if [[ ${1} -eq 1 ]]; then
    if  [[ "${2}" == "${def_name}" ]]; then
      write_yellow "Dry-Run>> docker container ps -a"
      write_yellow "Dry-Run>> docker images"
    else
      write_yellow "Dry-Run>> docker container ps -a | grep -i ${2}"
      write_yellow "Dry-Run>> docker images | grep -i  ${2}"
    fi
  else
    if  [[ "${2}" == "${def_name}" ]]; then
      write_green "Executing>> docker container ps -a"
      docker container ps -a
      write_green "Executing>> docker images"
      docker images
    else
      write_green "Executing>> docker container ps -a | grep -i ${2}"
      docker container ps -a | grep -i ${2}
      write_green "Executing>> docker images | grep -i ${2}"
      docker images | grep -i ${2}
    fi
  fi
}

_pull () {
  # _pull ${dry_run} ${docker_name}
  if [[ ${verbose} -eq 1 ]]; then
    write_magenta "_pull(${1}, ${2})"
  fi
  # 0 container(s)
  if [[ ${1} -eq 1 ]]; then
    write_yellow "Dry-Run>> docker pull ${2}"
  else
    write_green "Executing>> docker pull ${2}"
    docker pull ${2}
  fi
}

_remove () {
  # _remove ${dry_run} ${docker_name} ${_num_exited} ${_cid_exited}
  if [[ ${verbose} -eq 1 ]]; then
    write_magenta "_remove(${1}, ${2}, ${3}, ${4})"
  fi
  # 0 container(s)
  if [[ ${3} -eq 0 ]]; then
    write_red "_remove() <ERROR> no '${2}' container in EXITED state!"
    exit 0
  # 1 container(s)
  elif [[ ${3} -eq 1 ]]; then
    if [[ ${1} -eq 1 ]]; then
      write_yellow "Dry-Run>> docker rm --force ${4}"
    else
      write_green "Executing>> docker rm --force ${4}"
      docker rm --force ${4}
    fi
  # >1 container(s)
  else
    write_red "_remove() <ERROR> multiple '${2}' containers in EXITED state!"
    exit 0
  fi
}

_start () {
  # _start ${dry_run} ${docker_name} ${_num_exited} ${_cid_exited}
  if [[ ${verbose} -eq 1 ]]; then
    write_magenta "_start(${1}, ${2}, ${3}, ${4})"
  fi
  # 0 container(s)
  if [[ ${3} -eq 0 ]]; then
    write_red "_start() <ERROR> no '${2}' container in EXITED state!"
    exit 0
  # 1 container(s)
  elif [[ ${3} -eq 1 ]]; then
    if [[ ${1} -eq 1 ]]; then
      write_yellow "Dry-Run>> docker start ${4}"
    else
      write_green "Executing>> docker start ${4}"
      docker start ${4}
    fi
  # >1 container(s)
  else
    write_red "_start() <ERROR> multiple '${2}' containers in EXITED state!"
    exit 0
  fi
}

_status () {
  # _status ${dry_run} ${docker_name}
  if [[ ${verbose} -eq 1 ]]; then
    write_magenta "_status(${1}, ${2})"
  fi
  # show status
  if [[ ${1} -eq 1 ]]; then
    write_yellow "Dry-Run>> docker container ps -a | grep -i ${2}"
  else
    write_green "Executing>> docker container ps -a | grep -i ${2}"
    docker container ps -a | grep -i ${2}
  fi
}

_stop () {
  # _stop ${dry_run} ${docker_name} ${_num_up} ${_cid_up}
  if [[ ${verbose} -eq 1 ]]; then
    write_magenta "_stop(${1}, ${2}, ${3}, ${4})"
  fi
  # 0 container(s)
  if [[ ${3} -eq 0 ]]; then
    write_red "_stop() <ERROR> no '${2}' container in UP state!"
    exit 0
  # 1 container(s)
  elif [[ ${3} -eq 1 ]]; then
    if [[ ${1} -eq 1 ]]; then
      write_yellow "Dry-Run>> docker stop ${4}"
    else
      write_green "Executing>> docker stop ${4}"
      docker stop ${4}
    fi
  # >1 container(s)
  else
    write_red "_stop() <ERROR> multiple '${2}' containers in UP state!"
    exit 0
  fi
}




# +
# execute
# -
case $(echo ${docker_cmnd}) in
  build*)
    _build ${dry_run} ${docker_file} ${docker_dtag}
    ;;
  connect*)
    _connect ${dry_run} ${docker_name} ${_num_up} ${_cid_up}
    ;;
  create*)
    _create ${dry_run} ${docker_name} ${docker_port}
    ;;
  list*)
    _list ${dry_run} ${docker_name}
    ;;
  pull*)
    _pull ${dry_run} ${docker_name}
    ;;
  remove*)
    _remove ${dry_run} ${docker_name} ${_num_exited} ${_cid_exited}
    ;;
  start*)
    _start ${dry_run} ${docker_name} ${_num_exited} ${_cid_exited}
    ;;
  status*)
    _status ${dry_run} ${docker_name}
    ;;
  stop*)
    _stop ${dry_run} ${docker_name} ${_num_up} ${_cid_up}
    ;;
  *)
    write_red "<ERROR> invalid command!"
    exit 0
    ;;
esac


# +
# exit
# -
exit 0
