#!/bin/bash

set -eo pipefail

main() {

  shellcheck ./.github/scripts/*.sh
  shellcheck ./"panic"/*.sh -x
  shellcheck ./scripts/*.sh -x
  shellcheck ./scripts/common/*.sh -x
  shellcheck ./scripts/hooks/*

}

main "$@"
