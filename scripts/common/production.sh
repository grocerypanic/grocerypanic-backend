#!/bin/bash

set -e

backup_prod() {

  set -e

  pushd "${PROJECT_HOME}" > /dev/null
    pushd "${PROJECT_NAME}" >/dev/null

      set -a
      # shellcheck disable=SC1091
      source ../environments/prod.env

      gcloud config set project "${GCP_PROJECT}"

      prune_backups

      echo "Creating new snapshot..."
      INSTANCE_NAME=$(echo "${CLOUDSQLINSTANCE}" | cut -d":" -f3)
      gcloud sql backups create --instance="${INSTANCE_NAME}"

    popd >/dev/null
  popd >/dev/null

}

deploy_prod() {

  pushd "${PROJECT_HOME}" > /dev/null
    pushd "${PROJECT_NAME}" >/dev/null

        set -a
        # shellcheck disable=SC1091
        source ../environments/prod.env

        ./manage.py collectstatic --no-input

        poetry export --without-hashes -f requirements.txt -o requirements.txt
        mv ../requirements.txt .
        cp ../environments/prod.yaml app.yaml

        while read -r line; do
          [[ -z "${line}" ]] && continue
          key="$(echo "${line}" | cut -d'=' -f1)"
          value=''
          value="${line/$key=/$value}"
          echo "  ${key}: \"${value}\"" >> app.yaml
        done < "../environments/prod.env"
        gcloud auth activate-service-account --key-file=../service-account.json
        gcloud config set project "${GCP_PROJECT}"
        gcloud app deploy --version v1 --quiet
        rm app.yaml requirements.txt

    popd >/dev/null
  popd >/dev/null

}
