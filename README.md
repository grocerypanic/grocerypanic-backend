# Project Documentation

## Don't Panic!

A kitchen inventory management app.

[Project Documentation](https://panic.readthedocs.io/)

#### Production Environment (release tag from the production branch)
[![panic-automation](https://github.com/niall-byrne/panic/workflows/panic%20Automation/badge.svg?branch=production)](https://github.com/niall-byrne/panic/actions)

[Production Deploy](https://grocerypanic.com)


#### Stage Environment (master branch)
[![panic-automation](https://github.com/niall-byrne/panic/workflows/panic%20Automation/badge.svg?branch=master)](https://github.com/niall-byrne/panic/actions)

[Stage Deploy](https://stage.grocerypanic.com)


## OpenAPI Specification

Once the development container is running, you can interact with the OpenApi Interface.

Launch the container (instructions below) then create an admin user so you can login:
- `cd /app/panic`
- `python manage.py autoadmin`
- Login via the admin interface: 
  - http://localhost:8080/admin  (admin/admin)
- View the OpenAPI interface: 
  - http://localhost:8080/swagger/

## Environment Configuration

[Environment Documentation](./environments/README.md)

## Database Schema Information

[Database Schema](./documentation/images/schema.png)

## Development Dependencies

You'll need to install:
 - [Docker](https://www.docker.com/) 
 - [Docker Compose](https://docs.docker.com/compose/install/)

## Setup the Development Environment

Build the development environment container (this takes a few minutes):
- `docker-compose build`

Start the environment container:
- `docker-compose up -d`

Spawn a shell inside the container:
- `./container`

## Install the Project Packages on your Host Machine
This is useful for making your IDE aware of what's installed in a venv.

- `pip install pipenv`
- `source scripts/dev`
- `dev setup` (Installs the requirements.txt in the `assets` folder.)
- `pipenv --venv` (To get the path of the virtual environment for your IDE.)

## Environment
The [local.env](environments/local.env) file can be modified to inject environment variable content into the container.

You can override the values set in this file by setting shell ENV variables prior to starting the container:
- `export GIT_HOOKS_PROTECTED_BRANCHES='.*'`
- `docker-compose kill` (Kill the current running container.)
- `docker-compose rm` (Remove the stopped container.)
- `docker-compose up -d` (Restart the dev environment, with a new container, containing the override.)
- `./container`

## Releases

- Deployment to stage is fully automated on every commit to develop.  You will need to use the admin environment to manually manage database migrations as needed.

- Deployment to production is trigged by a release tag.

#### Production Release Tags

- The tag should constitute a 'vD.DD' format where each D creates the version of the release.

- Once the tag is created, a github release draft is created, giving you the opportunity to review the changes before a deploy. Any database changes will need to be managed in the admin environment.

- Once the release is published, automatic deployment to production is triggered.  This is considered approval of the release.

## Database Migrations on Stage or Production

Use the Admin environment to peform database migrations against Stage or Production.
A cloudsql proxy will be launched, looking for a gcp service account key file named `service-account.json` in the root of this repository.

To start the admin environment:
- ensure the development environment is stopped: `docker-compose down`
- copy the `service-account.json` for prod or stage to the root of this repository
- set the ADMIN_ENVIRONMENT environment variable to either `stage` or `prod` accordingly
- start the admin environment: `docker-compose up -f admin.yml`
- enter the container using `./container`
- remove the `service-account.json` file after you're finished interacting with the environment.

**Note:**

The admin environment is the only way to access the production environment's admin console.

## Git Hooks
Git hooks are installed that will enforce linting and unit-testing on the specified branches.
The following environment variables can be used to customize this behavior:

- `GIT_HOOKS` (Set this value to 1 to enable the pre-commit hook)
- `GIT_HOOKS_PROTECTED_BRANCHES` (Customize this regex to specify the branches that should enforce the Git Hook on commit.)

## CLI Reference
The CLI is enabled by default inside the container, and is also available on the host machine.
Run the CLI without arguments to see the complete list of available commands: `$ dev`

## Installing Dev CLI on a OSX host (outside the container)

You need the Postgresql CLI installed, [here's](https://www.compose.com/articles/postgresql-tips-installing-the-postgresql-client/
) how on a Mac.

If you're on Mojave, you should run this command, prior to running `dev setup`:
- `export LDFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib"`

