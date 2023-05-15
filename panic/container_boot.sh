#!/bin/bash

echo "Development Server Starting ..."

# shellcheck disable=SC1091
source "$(poetry env info --path)/bin/activate"

pushd "panic" || exit 127

if [[ $1 == "admin" ]]; then
  cloud_sql_proxy --instances="${CLOUDSQLINSTANCE}"=tcp:0.0.0.0:5432 &
else
  # shellcheck disable=SC1091
  [[ -f "../environments/local_secret.env" ]] && source "../environments/local_secret.env"
  ./manage.py wait_for_db
  ./manage.py makemigrations
  ./manage.py migrate
  ./manage.py autoadmin
  ./manage.py autosocial google
  ./manage.py autosocial facebook
fi

while true; do
    ./manage.py runserver 0.0.0.0:8080
done
