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

# shellcheck source=scripts/common/database.sh
source "$( dirname "${BASH_SOURCE[0]}" )/common/database.sh"

# shellcheck source=scripts/common/release.sh
source "$( dirname "${BASH_SOURCE[0]}" )/common/release.sh"

case $1 in
  'backup-prod')
    shift
    source_environment
    is_admin
    create_backup "prod"
    ;;
  'backup-stage')
    shift
    source_environment
    is_admin
    create_backup "stage"
    ;;
  'build-docs')
    shift
    source_environment
    build_documentation "$@"
    ;;
  'build-toctree')
    shift
    source_environment
    build_toctree "$@"
    ;;
  'check-release')
    source_environment
    check_release
    ;;
  'check-toctree')
    shift
    source_environment
    check_toctree "$@"
    ;;
  'deploy-stage')
    shift
    source_environment
    is_admin
    deploy_appengine "stage"
    ;;
   'deploy-prod')
    shift
    source_environment
    is_admin
    deploy_appengine "prod"
    ;;
  'fmt')
    shift
    source_environment
    fmt "$@"
    ;;
  'fmt-diff')
    shift
    source_environment
    fmt_diff "$@"
    ;;
  'lint')
    shift
    source_environment
    lint "$@"
    ;;
  'lint-diff')
    shift
    source_environment
    lint_diff "$@"
    ;;
  'lint-extras')
    shift
    source_environment
    lint_extras "$@"
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
    echo "backup-prod backup-stage build-docs build-toctree check-release check-toctree deploy-prod deploy-stage fmt fmt-diff lint lint-diff lint-extras reinstall-requirements sectest setup test test-coverage test-integration types update"
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
  'types')
    shift
    source_environment
    type_check "$@"
    ;;
  'update')
    shift
    update_cli "$@"
    ;;
  *)
    echo "Valid Commands:"
    echo ' - backup-prod             (ADMIN ONLY: snapshot the active database)'
    echo ' - backup-stage            (ADMIN ONLY: snapshot the active database)'
    echo ' - build-docs              (Build Documentation)'
    echo ' - build-toctree           (re/Build Documentation TocTree)'
    echo ' - check-release           (Check code is release ready)'
    echo ' - check-toctree           (Check Documentation TocTree)'
    echo ' - deploy-prod             (ADMIN ONLY: Deploy to Production)'
    echo ' - deploy-stage            (ADMIN ONLY: Deploy to Stage)'
    echo ' - fmt                     (Run the code formatters)'
    echo ' - fmt-diff                (Run the code formatters on modified files.)'
    echo ' - lint                    (Run the linter)'
    echo ' - lint-diff               (Run the linter on modified files.)'
    echo ' - lint-extras             (Run pydocstyle, isort, ect.)'
    echo ' - reinstall-requirements  (Reinstall Packages'
    echo ' - sectest                 (Run security tests)'
    echo ' - setup                   (Setup/Reset environment)'
    echo ' - test                    (Run pytest)'
    echo ' - test-coverage           (Run pytest with coverage)'
    echo ' - test-integration        (Run pytest on integration tests)'
    echo ' - types                   (Run mypy)'
    echo ' - update                  (Update bash & the CLI)'
    ;;

esac
