#!/usr/bin/env bash
# shellcheck disable=SC1117

build_documentation() {

  echo "Generating Documentation ..."
  set -e

  pushd "${PROJECT_HOME}/documentation" > /dev/null
    rm -rf build
    make html
  popd > /dev/null

}

build_toctree() {

  echo "Rebuilding TOC Tree ..."
  set -e

  pushd "${PROJECT_HOME}/${PROJECT_NAME}" > /dev/null
    find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
    find . -type d -empty -delete
    ./manage.py toctree --write
  popd > /dev/null

}

check_toctree() {

  echo "Checking TOC Tree ..."
  set -e

  pushd "${PROJECT_HOME}/${PROJECT_NAME}" > /dev/null
    ./manage.py toctree --check
  popd > /dev/null

}