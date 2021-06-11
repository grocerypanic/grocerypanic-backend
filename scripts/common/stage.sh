#!/bin/bash

set -e

deploy_stage() {

  pushd "${PROJECT_HOME}" > /dev/null
    pushd "${PROJECT_NAME}" >/dev/null

        set -a
        # shellcheck disable=SC1091
        source ../environments/stage.env

        ./manage.py collectstatic --no-input

        poetry export --without-hashes -f requirements.txt -o requirements.txt
        mv ../requirements.txt .
        cp ../environments/stage.yaml app.yaml

        while read -r line; do
          [[ -z "${line}" ]] && continue
          key="$(echo "${line}" | cut -d'=' -f1)"
          value=''
          value="${line/$key=/$value}"
          echo "  ${key}: \"${value}\"" >> app.yaml
        done < "../environments/stage.env"
        gcloud auth activate-service-account --key-file=../service-account.json
        gcloud config set project "${GCP_PROJECT}"
        gcloud app deploy --version v1 --quiet
        rm app.yaml requirements.txt

    popd >/dev/null
  popd >/dev/null

}
