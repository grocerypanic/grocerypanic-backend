#!/bin/bash

set -o pipefail

main() {

  # $1 - may be set to "admin"

  echo | ssh-keygen
  touch "${HOME}/.gitconfig"
  touch "${HOME}/.gitconfig_global"

  sudo chmod -R o+w .

  case $1 in
    admin)
      docker-compose -f admin.yml build
      docker-compose -f admin.yml up -d
      ;;
    *)
      docker-compose build
      docker-compose up -d
      ;;
  esac

}

main "$@"
