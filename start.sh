#!/bin/sh

set -x

trap "exit" INT
trap "exit" TERM

CSV_DONE="${CSV_DONE:-./done}"
CSV_TODO="${CSV_TODO:-./todo}"
CSV_ERROR="${CSV_ERROR:-./error}"
SLEEP=${SLEEP:-10}
LOOP=${LOOP:-1}

run_app() {
  COMMAND="$*"

  if [ "$(find "${CSV_TODO}/" -name '*.csv' | wc -l)" -gt 0 ]
  then
    eval "${COMMAND}"
  fi
}

message_sleep() {
  MESSAGE="${1}"
  SLEEP="${2}"

  echo "${MESSAGE}" && sleep "${SLEEP}"
}

if [ -z "${DB_HOST}" ] || \
   [ -z "${DB_PORT}" ] || \
   [ -z "${DB_PASSWORD}" ] || \
   [ -z "${DB_USER}" ]
then
  echo "Missing required database environment variables:"
  echo "  - DB_HOST"
  echo "  - DB_PORT"
  echo "  - DB_PASSWORD"
  echo "  - DB_USER"
  exit 1
fi

echo "Current Python Version: $(python --version)"

WAIT_HOSTS="${DB_HOST}:${DB_PORT}" /wait || exit 1

export CSV_DONE \
       CSV_TODO \
       CSV_ERROR \
       DB_HOST \
       DB_PORT \
       DB_PASSWORD \
       DB_USER

for DIR in "${CSV_TODO}" "${CSV_DONE}" "${CSV_ERROR}"
do
  test -f "${DIR}" || mkdir -vp "${DIR}"
done

if [ "${LOOP}" -ne 1 ]
then
  run_app "$@"
else
  while true
  do
    run_app "$@"
    message_sleep "Sleeping for ${SLEEP}s..." "${SLEEP}"
  done
fi
