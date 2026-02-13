# KernelCI Dashboard

Our Web Dashboard to evaluate test results from the common results database([KCIDB](https://docs.kernelci.org/kcidb/)).
Available at [dashboard.kernelci.org](https://dashboard.kernelci.org).

The new KernelCI Web Dashboard is a web application created to provide access
to static checks, build logs, boot logs and test results related for the Linux kernel
CI/test ecosystem. All that data will be provided by [KCIDB](https://docs.kernelci.org/kcidb/)
system from the [KernelCI Foundation](https://kernelci.org/).

## Repository
What we have as a repository is a monorepo containing the *dashboard* (the web application) and a *backend*.

### Dashboard
A web app built with [React](https://react.dev/) + [Typescript](https://www.typescriptlang.org/), to see more information check the dashboard [README](dashboard/README.md).

### Backend
A Python http server built with [Django](https://www.djangoproject.com/) + [DRF](https://www.django-rest-framework.org/), to see more information check the backend [README](/backend/README.md).


## Build

### Frontend

Create a .env file in /dashboard, check and set the variables and their values
```sh
 cp ./dashboard/.env.example ./dashboard/.env
```

With docker, you can start just the frontend with `docker compose up --build proxy`. It is also possible to run the dashboard outside of it for development purposes.

We use `pnpm` to help with the package management. Install the dependencies with
```sh
pnpm install
```

Then start the dev server with
```sh
pnpm dev
```

If you want to test the production state of the dashboard, use
```sh
pnpm build
pnpm preview
```

### Backend

Create a .env file in the base directory,
```sh
 cp .env.backend.example .env.backend
```

Create a secret key for Django:
```sh
export DJANGO_SECRET_KEY=$(openssl rand -base64 22)
```
We are not using sessions or anything like that right now, so changing the secret key won't be a big deal.

Since the production *database* is not open for the public, we use ssh tunneling with a whitelist to access it. This means that the docker setup currently can't access it, but we have a local database that is connected automatically if you don't change the env vars.

If you do use docker, you should create a secret file with the database password:
```sh
mkdir -p backend/runtime/secrets
echo <password> > backend/runtime/secrets/postgres_password_secret
```

If you are going to use a database user other than `kernelci`, set it to `DB_DEFAULT_USER`:
```sh
export DB_DEFAULT_USER=<user>
```

If you are setting up instance different than production KernelCI dashboard, you need to define CORS_ALLOWED_ORIGINS. On .env.backend:
```
CORS_ALLOWED_ORIGINS=["https://d.kernelci.org","https://dashboard.kernelci.org"]
```

It is also possible to run the backend outside of docker for development purposes. Simply run the ssh tunnel with the instructions sent to you by the database manager, then export the variables seen in [.env.backend.example](/.env.backend.example).

> For other optional envs, check the [backend README](backend/README.md).

### Common

Startup the services:
 ```sh
 docker compose up --build -d
 ```
 Docker exposes port 80 (that you don't need to enter in the URL) instead of 5173 and 8000 that is used when running the dashboard project outside of docker.
 So you can hit the frontend with `http://localhost`  and the backend with `http://localhost/api` when running locally.

Make sure that docker has the right permissions and has access to the environment variables. One way to do that is to set up a docker permission group.

If you are running the commands for exporting the environment variables and running docker separately, you can run docker with admin privileges and allowing environment variables with:
```sh
sudo -E docker compose up --build -d
```
Or you can also run the env exports and docker compose within the root user by running `sudo su`.

> Tip: you can create a quick script to set all the necessary envs and start the services. This will also allow docker to see the environment variables correclty. Example:

```sh
export DB_DEFAULT_USER=email@email.com
export DJANGO_SECRET_KEY=$(openssl rand -base64 22)
export DB_DEFAULT_NAME=kcidb
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."

docker compose up --build
```

> [Note] If you are going to run using only the local database, the DB_DEFAULT_NAME should be `dashboard` and the `DB_DEFAULT_USER` and `DB_DEFAULT_PASSWORD` should be `admin` (for now).
> After you define those values, also set the env var `USE_DASHBOARD_DB` to True, setting the local database as the default one.
> You could also set the DB_DEFAULT variables to point to the local database and leave `USE_DASHBOARD_DB` as False.


## Deploying to production

To deploy to prod you need to push a tag in the `release/YYYYMMDD.N` format
like: `release/20240910.0`

## Test results email reports

See details about our new [notifications](docs/notifications.md) system.

## Contributing 

Check out our [CONTRIBUTING.md](/CONTRIBUTING.md), and there is an [onboarding guide](docs/Onboarding.md) to help get acquainted with the project. Contributions are welcome!

