#!/bin/bash

set -o pipefail

main() {

  docker-compose build
  docker-compose up -d

}

main "$@"
