#!/bin/bash

set -e

prune_backups() {

  set -e

  INSTANCE_NAME=$(echo "${CLOUDSQLINSTANCE}" | cut -d":" -f3)

  INPUT_LOOP=1
  while [[ "${INPUT_LOOP}" -eq 1 ]]; do
    read -rp "Do you wish to prune old backups (y/n) ?" yn
    INPUT_LOOP=0
    case $yn in
      [Yy]* )
         OLD_BACKUPS=$(gcloud sql backups list --instance=panic-prod --format="value(id,windowStartTime)" | grep -v 00:00.000+00:00 | awk '{print $1}')
          for BACKUP in ${OLD_BACKUPS}; do
            gcloud sql backups delete -q --instance="${INSTANCE_NAME}" "${BACKUP}"
          done
        break
        ;;
      [Nn]* )
        break
        ;;
      * )
        echo "Please answer yes or no."
        INPUT_LOOP=1
        ;;
    esac
  done

}
