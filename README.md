# Project Documentation

## Don't Panic!

A kitchen inventory management app.

[Project Documentation](https://grocerypanic-backend.readthedocs.io/)

#### Production Environment (release tag from the production branch)
[![panic-automation](https://github.com/grocerypanic/grocerypanic-backend/workflows/panic%20Automation/badge.svg?branch=production)](https://github.com/grocerypanic/grocerypanic-backend/actions)

[Production Deploy](https://grocerypanic.com)


#### Stage Environment (main branch)
[![panic-automation](https://github.com/grocerypanic/grocerypanic-backend/workflows/panic%20Automation/badge.svg?branch=main)](https://github.com/grocerypanic/grocerypanic-backend/actions)

[Stage Deploy](https://stage.grocerypanic.com)


## OpenAPI Specification
<!-- markdown-link-check-disable -->

Once the development container is running, you can interact with the OpenApi Interface.

Launch the container (instructions below) then create a default admin user:
- `cd /app/panic`
- `python manage.py autoadmin`
- Login via the admin interface: 
  - http://localhost:8080/admin  (admin/admin)
- View the OpenAPI interface: 
  - http://localhost:8080/swagger/

<!-- markdown-link-check-enable -->
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

- `pip install poetry`
- `source scripts/dev`
- `dev setup` (Installs the requirements.txt in the `assets` folder.)
- `poetry env info -p` (To get the path of the virtual environment for your IDE.)

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

- Deployment to production is triggered by a release tag.

#### Production Release Tags

- The tag should follow [semantic versioning](https://semver.org/): "vDD.DD.DD" 

- Once the tag is created, a GitHub release draft is created, giving you the opportunity to review the changes before a deployment. Any database changes will need to be managed in the admin environment.

- Once the release is published, automatic deployment to production is triggered.  This is considered approval of the release.

## Database Migrations on Stage or Production

Use the Admin environment to perform database migrations against Stage or Production.
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
Git hooks are installed that will enforce linting, unit-testing and other basic checks on the `production` and `main` branches.

The default configuration is to use the `pre-push` hook, with the goal being to prevent any unnecessary rebasing of the main branch, regardless of the circumstances around the commit.

## CLI Reference
The CLI is enabled by default inside the container, and is also available on the host machine.
Run the CLI without arguments to see the complete list of available commands: `$ dev`

(This is mostly useful for setting up a venv for your IDE, it's recommended to use the container's managed environment.)
