#!/bin/bash

check_release() {

  halt() {
    # $1 - Message

    echo "$1"
    exit 127
  }

  [[ ! -f /etc/container_release ]] && halt "Must be run inside the container."

  set -e

  pushd "${PROJECT_HOME}" > /dev/null

    # Formatting
    echo "Checking Formatting ... "

    tomll /app/pyproject.toml
    fmt

    DIFF=$(git diff)
    [[ -n "${DIFF}" ]] && halt "Formatting needs to be checked!"

    echo "Release Looks Good."

  popd >/dev/null
}
