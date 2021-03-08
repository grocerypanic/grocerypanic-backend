#!/bin/bash

# Do Not Modify This File, It's Intended To Be Updated From Time to TIme
# INSTEAD: add additional functionality by adding separate library files
# Import your new libraries into the commander.sh script and add them to the CLI.

fmt() {

  set -e

  pushd "${PROJECT_HOME}" >/dev/null
  echo "Running yapf ..."
  yapf -i --recursive --exclude '**/*_pb2.py' --style='{based_on_style: google, INDENT_WIDTH: 2, ALIGN_CLOSING_BRACKET_WITH_VISUAL_INDENT: false, COALESCE_BRACKETS:true, DEDENT_CLOSING_BRACKETS: true}' "${PROJECT_NAME}/"
  echo "Running isort ..."
  isort -y
  popd >/dev/null

}

lint() {

  lint_check "$@"

}

lint_check() {

  set -e
  if [[ $# -eq 0 ]]; then
    ARGS=("${PROJECT_NAME}")
  else
    ARGS=("$@")
  fi

  pushd "${PROJECT_HOME}" >/dev/null

  lint_extras

  echo "Running pylint ..."
  pytest --pylint -m pylint --pylint-rcfile=.pylint.rc --pylint-jobs=3 "${ARGS[@]}"

  echo "Running shellcheck ..."
  shellcheck -x scripts/*.sh
  shellcheck -x scripts/common/*.sh

  popd >/dev/null

}

lint_diff() {
  echo "Running pylint on DIFF ..."
  pushd "${PROJECT_HOME}" >/dev/null
    FILES=()
    IFS=" " read -r -a FILES <<< "$(git diff --name-only --diff-filter=d | grep -E '\.py$' | tr '\n' ' ')"
    pytest --pylint -m pylint --pylint-rcfile=.pylint.rc --pylint-jobs=3 "${FILES[@]}"
  popd >/dev/null
}

lint_extras() {
  echo "Checking docstrings ..."
  pushd "${PROJECT_HOME}" >/dev/null
    pydocstyle "${PROJECT_NAME}"
    pydocstyle --config=.pydocstyle.tests "${PROJECT_NAME}"
    echo "Checking imports ..."
    isort -c
  popd >/dev/null
}

reinstall_requirements() {

  set -e

  pushd "${PROJECT_HOME}" >/dev/null
  pip install -r assets/requirements.txt --no-warn-script-location
  pip install -r assets/requirements-dev.txt --no-warn-script-location
  popd >/dev/null

}

security() {

  set -e

  pushd "${PROJECT_HOME}" >/dev/null
  bandit -r "${PROJECT_NAME}" -c .bandit.rc --ini .bandit
  safety check
  popd >/dev/null

}

setup_bash() {

  [[ ! -f /etc/container_release ]] && return

  for filename in /app/development/bash/.bash*; do
    echo "Symlinking ${filename} ..."
    ln -sf "${filename}" "/home/user/$(basename "${filename}")"
  done

}

setup_python() {

  unvirtualize

  pushd "${PROJECT_HOME}" >/dev/null
  if [[ ! -f /etc/container_release ]]; then
    set +e
    pipenv --rm
    set -e
    pipenv --python 3.7
  fi
  source_environment
  reinstall_requirements
  unvirtualize
  popd >/dev/null

}

source_environment() {

  if [[ ! -f /etc/container_release ]]; then

    unvirtualize

    # shellcheck disable=SC1090
    source "$(pipenv --venv)/bin/activate"

  fi

  pushd "${PROJECT_HOME}" >/dev/null
  set +e
  cd .git/hooks
  ln -sf ../../scripts/hooks/pre-commit pre-commit
  set -e
  popd >/dev/null

}

test_runner() {

  set -e

  if [[ $1 == "functional" ]]; then
    functional_tests "$@"
  else
    unittests "$@"
  fi

}

type_check() {

  set -e

  pushd "${PROJECT_HOME}" >/dev/null
  mypy "${PROJECT_NAME}"
  popd >/dev/null

}

unittests() {

  set -e

  if [[ $1 == "integration" ]]; then

    integration_tests "$@"

  else

    pushd "${PROJECT_HOME}" >/dev/null
    if [[ $1 == "coverage" ]]; then
      shift
      set +e
      pytest --cov-config=.coveragerc --cov-report term-missing --cov-fail-under=100 --cov="${PROJECT_NAME}" "$@"
      exit_code="$?"
      coverage html
      set -e
      exit "${exit_code}"
    else
      pytest "$@"
    fi
    popd >/dev/null

  fi

}

integration_tests() {

  set -e

  pushd "${PROJECT_HOME}" >/dev/null

  shopt -s globstar

    pytest -x "${PROJECT_NAME}/"**/integration_*.py

  popd >/dev/null

}

unvirtualize() {

  if [[ ! -f /etc/container_release ]]; then

    toggle=1

    if [[ -n "${-//[^e]/}" ]]; then set +e; else toggle=0; fi
    if python -c 'import sys; sys.exit(0 if hasattr(sys, "real_prefix") else 1)'; then
      deactivate_present=$(LC_ALL=C type deactivate 2>/dev/null)
      if [[ -n ${deactivate_present} ]]; then
        deactivate
      else
        exit
      fi
    fi
    if [[ "${toggle}" == "1" ]]; then set -e; fi

  fi

}

update_cli() {

  echo "Disabled, due to upstream changes in the PIB api."

  return

  set -e

  updates=("/scripts/common/documentation.sh" "/scripts/common/wheel.sh" "/scripts/common/upload.sh" "/scripts/common/common.sh" "/development/bash/.bash_git" "/development/bash/.bash_profile" "/development/bash/.bashrc")

  pushd "${PROJECT_HOME}" >/dev/null
  mkdir -p scripts/common/.archive
  mkdir -p development/bash/.archive
  cp scripts/common/*.sh scripts/common/.archive
  cp development/bash/.bash* development/bash/.archive
  for filename in "${updates[@]}"; do
    echo "Downloading: .${filename}"
    echo "Source: https://raw.githubusercontent.com/niall-byrne/python-in-a-box/master/%7B%7Bcookiecutter.project_slug%7D%7D${filename}"
    curl -s -L "https://raw.githubusercontent.com/niall-byrne/python-in-a-box/master/%7B%7Bcookiecutter.project_slug%7D%7D${filename}" >".${filename}"
  done
  popd >/dev/null

  setup_bash

}
