#!/bin/bash

set -e

# shellcheck source=scripts/common/common.sh
source "$( dirname "${BASH_SOURCE[0]}" )/common/common.sh"

# shellcheck source=scripts/settings.sh
source "$( dirname "${BASH_SOURCE[0]}" )/settings.sh"

# shellcheck source=scripts/common/documentation.sh
source "$( dirname "${BASH_SOURCE[0]}" )/common/documentation.sh"

# Optional For Libraries
# shellcheck source=scripts/common/wheel.sh
# source "$( dirname "${BASH_SOURCE[0]}" )/common/wheel.sh"

# Add Additional Functionality Via Imports Here

# shellcheck source=scripts/common/stage.sh
source "$( dirname "${BASH_SOURCE[0]}" )/common/stage.sh"

# shellcheck source=scripts/common/production.sh
source "$( dirname "${BASH_SOURCE[0]}" )/common/production.sh"

case $1 in
  'build-docs')
    shift
    source_environment
    build_documentation "$@"
    ;;
  'deploy-stage')
    shift
    source_environment
    deploy_stage "$@"
    ;;
   'deploy-prod')
    shift
    source_environment
    deploy_prod "$@"
    ;;
  'fmt')
    shift
    source_environment
    fmt "$@"
    ;;
  'lint')
    shift
    source_environment
    lint "$@"
    ;;
  'lint-validate')
    shift
    source_environment
    lint_check "$@"
    ;;
  'reinstall-requirements')
    shift
    source_environment
    reinstall_requirements "$@"
    ;;
  'sectest')
    shift
    source_environment
    security "$@"
    ;;
  'setup')
    shift
    setup_bash "$@"
    setup_python "$@"
    ;;
  'shortlist')
    echo "build-docs deploy-prod deploy-stage fmt lint lint-validate reinstall-requirements sectest setup test test-coverage test-integration update"
    ;;
  'test')
    shift
    source_environment
    test_runner "$@"
    ;;
  'test-coverage')
    shift
    source_environment
    test_runner "coverage" "$@"
    ;;
  'test-integration')
    shift
    source_environment
    test_runner "integration" "$@"
    ;;
  'update')
    shift
    update_cli "$@"
    ;;
  *)
    echo "Valid Commands:"
    echo ' - build-docs              (Build Documentation)'
    echo ' - deploy-prod             (Deploy to Cloud RUn)'
    echo ' - deploy-stage            (Deploy to App Engine)'
    echo ' - fmt                     (Run the code formatters)'
    echo ' - lint                    (Run the linter)'
    echo ' - lint-validate           (Validate linting)'
    echo ' - reinstall-requirements  (Reinstall Packages'
    echo ' - sectest                 (Run security tests)'
    echo ' - setup                   (Setup/Reset environment)'
    echo ' - test                    (Run pytest)'
    echo ' - test-coverage           (Run pytest with coverage)'
    echo ' - test-integration        (Run pytest on integration tests)'
    echo ' - update                  (Update bash & the CLI)'
    ;;

esac
