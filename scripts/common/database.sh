#!/bin/bash

set -e

create_backup() {

  # $1 "stage" or "prod"

  set -e

  pushd "${PROJECT_HOME}" > /dev/null
    pushd "${PROJECT_NAME}" >/dev/null

      set -a
      # shellcheck disable=SC1091,SC1090
      source "../environments/${1}.env"

      gcloud auth activate-service-account --key-file=../service-account.json

      gcloud config set project "${GCP_PROJECT}"
      INSTANCE_NAME=$(echo "${CLOUDSQLINSTANCE}" | cut -d":" -f3)
      OLD_BACKUPS=$(gcloud sql backups list --instance="${INSTANCE_NAME}" --format="value(id,windowStartTime)" | grep -v 00:00.000+00:00 | awk '{print $1}')

      echo "Creating new snapshot..."
      gcloud sql backups create --instance="${INSTANCE_NAME}" --description="Created By Admin Environment"

      prune_backups "${INSTANCE_NAME}" "${OLD_BACKUPS}"

    popd >/dev/null
  popd >/dev/null

}

prune_backups() {

  # $1 Instance Name
  # $2 List of Backups to Purge

  set -e

  INSTANCE_NAME="${1}"
  BACKUPS="${2}"

  echo "Pruning Previous Backups ..."

  for BACKUP in ${BACKUPS}; do
    gcloud sql backups delete -q --instance="${INSTANCE_NAME}" "${BACKUP}"
  done

}
