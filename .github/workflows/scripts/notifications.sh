#!/bin/bash

# Takes two text arguments
# Message Format: <ARG1>: <ARG2>

BRANCH_OR_TAG="$(echo "${GITHUB_REF}" | sed 's/refs\/heads\///g' | sed 's/refs\/tags\///g')"
WORKFLOW_URL="$GITHUB_SERVER_URL/$GITHUB_REPOSITORY/actions/runs/$GITHUB_RUN_ID"
NOTIFICATION="${REPONAME} [<${WORKFLOW_URL}|${BRANCH_OR_TAG}>]"

[[ -z ${WEBHOOK_URL} ]] && exit 0

curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"${NOTIFICATION}: ${1}\"}" "${WEBHOOK_URL}"
