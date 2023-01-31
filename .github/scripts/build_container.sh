#!/bin/bash

set -o pipefail

main() {

  # $1 - may be set to "admin"

  echo | ssh-keygen
  touch "${HOME}/.gitconfig"
  touch "${HOME}/.gitconfig_global"

  case $1 in
    admin)
      docker-compose -f admin.yml build                 \
        --build-arg BUILD_ARG_CONTAINER_GID="$(id -g)"  \
        --build-arg BUILD_ARG_CONTAINER_UID="$(id -u)"

      docker-compose -f admin.yml up -d
      ;;
    *)
      docker-compose build                              \
        --build-arg BUILD_ARG_CONTAINER_GID="$(id -g)"  \
        --build-arg BUILD_ARG_CONTAINER_UID="$(id -u)"

      docker-compose up -d
      ;;
  esac

}

main "$@"
