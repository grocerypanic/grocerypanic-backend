#!/bin/bash

# Do Not Modify This File, It's Intended To Be Updated From Time to TIme
# INSTEAD: add additional functionality by adding separate library files
# Import your new libraries into the commander.sh script and add them to the CLI.

deploy_appengine() {

  # $1 "stage" or "prod"

  pushd "${PROJECT_HOME}" > /dev/null
    pushd "${PROJECT_NAME}" >/dev/null

        set -a
        # shellcheck disable=SC1091,SC1090
        source "../environments/${1}.env"

        ./manage.py collectstatic --no-input

        poetry export --without-hashes -f requirements.txt -o requirements.txt
        mv ../requirements.txt .
        cp "../environments/${1}.yaml" app.yaml

        while read -r line; do
          [[ -z "${line}" ]] && continue
          key="$(echo "${line}" | cut -d'=' -f1)"
          value=''
          value="${line/$key=/$value}"
          echo "  ${key}: \"${value}\"" >> app.yaml
        done < "../environments/${1}.env"
        gcloud auth activate-service-account --key-file=../service-account.json
        gcloud config set project "${GCP_PROJECT}"
        gcloud app deploy --version v1 --quiet
        rm app.yaml requirements.txt

    popd >/dev/null
  popd >/dev/null

}

fmt() {

  set -e

  pushd "${PROJECT_HOME}" >/dev/null
    echo "Running yapf ..."
    yapf -i --recursive "${PROJECT_NAME}/"
    echo "Running isort ..."
    isort .
  popd >/dev/null

}

fmt_diff() {
  set -e

  pushd "${PROJECT_HOME}" >/dev/null
    echo "Running yapf on DIFF ..."
    FILES=()
    IFS=" " read -r -a FILES <<< "$(git diff --name-only --diff-filter=d | grep -E '\.py$' | tr '\n' ' ')"
    yapf -i --recursive "${FILES[@]}"
    echo "Running isort on DIFF ..."
    isort "${FILES[@]}"
  popd >/dev/null
}

is_admin() {

  set -e
  if ! command -v gcloud > /dev/null; then
    echo "This command can only be run in an admin mode container."
    exit 127
  fi
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
    shellcheck_scripts
  popd >/dev/null

}

lint_diff() {
  echo "Running pylint on DIFF ..."
  pushd "${PROJECT_HOME}" >/dev/null
    FILES=()
    IFS=" " read -r -a FILES <<< "$(git diff --name-only --diff-filter=d | grep -E '\.py$' | tr '\n' ' ')"
    if [[ ${#FILES[@]} -gt 0 ]]; then
      pytest --pylint -m pylint --pylint-rcfile=.pylint.rc --pylint-jobs=3 "${FILES[@]}"
    fi
  popd >/dev/null
}

lint_extras() {
  pushd "${PROJECT_HOME}" >/dev/null
    echo "Checking docstrings ..."
    pydocstyle "${PROJECT_NAME}"
    pydocstyle --config=.pydocstyle.tests "${PROJECT_NAME}"
    echo "Checking imports ..."
    isort -c .
    shellcheck_scripts
  popd >/dev/null

}

reinstall_requirements() {

  set -e

  pushd "${PROJECT_HOME}" >/dev/null
    poetry install -E docs
  popd >/dev/null

}

security() {

  set -e

  pushd "${PROJECT_HOME}" >/dev/null
    bandit -r "${PROJECT_NAME}" -c .bandit.rc --ini .bandit -x tests
    poetry export --without-hashes -f requirements.txt -o requirements.txt
    safety check -r requirements.txt
    rm requirements.txt
  popd >/dev/null

}

setup_bash() {

  [[ ! -f /etc/container_release ]] && return

  for filename in /app/development/bash/.bash*; do
    echo "Symlinking ${filename} ..."
    ln -sf "${filename}" "/home/user/$(basename "${filename}")"
  done

  for filename in /app/development/dotfiles/.[^.]*; do
    echo "Symlinking ${filename} ..."
    ln -sf "${filename}" "/home/user/$(basename "${filename}")"
  done

}

setup_python() {

  unvirtualize

  pushd "${PROJECT_HOME}" >/dev/null
    if [[ ! -f /etc/container_release ]]; then
      set +e
      poetry env remove python >/dev/null 2>&1
      set -e
      poetry install -E docs
    fi
    source_environment
    reinstall_requirements
    unvirtualize
  popd >/dev/null

}

shellcheck_scripts() {
  pushd "${PROJECT_HOME}" >/dev/null
    echo "Running shellcheck ..."
    shellcheck -x scripts/*.sh
    shellcheck -x scripts/hooks/*
    shellcheck -x scripts/common/*.sh
  popd >/dev/null
}

source_environment() {

  if [[ ! -f /etc/container_release ]]; then

    unvirtualize

    # shellcheck disable=SC1090,SC1091
    source "$(poetry env info -p)/bin/activate"

  fi

  pushd "${PROJECT_HOME}" >/dev/null
    set +e
      cd .git/hooks
      ln -sf ../../scripts/hooks/pre-commit pre-commit
      ln -sf ../../scripts/hooks/pre-push pre-push
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

}
