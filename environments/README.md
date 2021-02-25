# Environment Variables

Each "Environment" has two sets of inputs for environment variables.

There are four supported environments:
- `local`
- `stage`
- `prod`
- `admin`

## Local Dev Environment Configuration


### [local.env](./local.env)

This file contains settings used only for local development, that are not privileged and can be kept in the code base to make setting up a development environment faster.


Development Environment Configuration
```bash
PYTHONPATH=/app/panic/
GIT_HOOKS=1
GIT_HOOKS_PROTECTED_BRANCHES="^(master|stage)"
```

Django and Postgresql Configuration
```bash
POSTGRES_USER=dbuser
POSTGRES_PASSWORD=supersecret
POSTGRES_DB=panic
POSTGRES_HOSTNAME=db
DJANGO_SECRET_KEY=hf8fsg-7k$16$@v69l)1y=hmrkd#czed9b%h20z)^#^gel-@*8
DJANGO_JWT_SECRET_KEY=LKEtEEk1rXLFkXqzIbFeGpCLBTskOOiUmiAXflLBXKorvqmtOvq05ZyhUPcIwoL6fZHs5bcU6w7UWPRBHOwPAXE1VI98YJY5UBvIM4zdohfJxtnG923JI9Ge
DJANGO_ENVIRONMENT=local
```

### [local_secret.env](./local_secret.env)

This file should NOT be checked in, and contains information for third party integrations.

```
GOOGLE_ID=<google service account for oauth logins>
GOOGLE_SECRET_KEY=<google secret key for oauth logins>
FACEBOOK_ID=<facebook app id for oauth logins>
FACEBOOK_SECRET_KEY=<facebook app secret for oauth logins>
DJANGO_EMAIL_PORT=<port number of SMTP server>
DJANGO_EMAIL_HOST=<hostname of SMTP server>
DJANGO_EMAIL_HOST_USER=<username of SMTP server>
DJANGO_EMAIL_HOST_PASSWORD=<password of SMTP server>
```

For local development, [mailtrap.io](https://mailtrap.io/) is a great resource for SMTP setup.

## Stage and Prod

Currently, both these environments are deployed onto AppEngine.
The deployment script parses a single `stage.env` or `prod.env` file with all the same values as the local environment,
and adds them to the app AppEngine environment config during deploy.  (This should be located in the `environments` folder).

These scripts are called via the `deploy-stage` and `deploy-prod` commands, from inside the development environment container.

The definitive list of required values for these environments is as follows:

```
POSTGRES_USER=<postgres user>
POSTGRES_PASSWORD=<postgres password>
POSTGRES_DB=<postgres database name>
POSTGRES_HOSTNAME=<postgres hostname -> "/cloudsql/GCP_PROJECT:GCP_REGION:CLOUD_SQL_Instance"
DJANGO_SECRET_KEY=<string for the secret key>
DJANGO_JWT_SECRET_KEY=<string for the jwt key>
DJANGO_ENVIRONMENT=<stage or prod>
DJANGO_EMAIL_PORT=<port number of SMTP server>
DJANGO_EMAIL_HOST=<hostname of SMTP server>
DJANGO_EMAIL_HOST_USER=<username of SMTP server>
DJANGO_EMAIL_HOST_PASSWORD=<password of SMTP server>
GOOGLE_ID=<google service account for oauth logins>
GOOGLE_SECRET_KEY=<google client key for oauth logins>
FACEBOOK_ID=<facebook app id for oauth logins>
FACEBOOK_SECRET_KEY=<facebook app secret for oauth logins>
CLOUDSQLINSTANCE=<string formatted as GCP_PROJECT:GCP_REGION:CLOUD_SQL_Instance >
WATCHMAN_TOKENS=<uuid or similar for watchman service)
GCP_PROJECT=<GCP_PROJECT ID>
```

## Admin Environment

Starting the admin environment locally gives you access to the production admin console.
You'll need an `admin.env` file (in the `environments` folder) containing the following:

```
POSTGRES_HOSTNAME=127.0.0.1
DJANGO_ENVIRONMENT=admin
GOOGLE_APPLICATION_CREDENTIALS=<path to a gcp key with access to the cloud sql instance>
```

This is in addition to the `prod.env` file which is also read, when you active the environment:
- `ADMIN_ENVIRONMENT=prod docker-compose-up -f admin.yml`
