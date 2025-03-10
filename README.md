# KernelCI Dashboard

Our Web Dashboard to evaluate test results from the common results database([KCIDB](https://docs.kernelci.org/kcidb/)).
Available at [dashboard.kernelci.org](https://dashboard.kernelci.org).

The new KernelCI Web Dashboard is a web application created to provide access
to static checks, build logs, boot logs and test results related for the Linux kernel
CI/test ecosystem. All that data will be provided by [KCIDB](https://docs.kernelci.org/kcidb/)
system from the [KernelCI Foundation](https://kernelci.org/).

# Repository
What we have as a repository is a monorepo containing the *dashboard* (the web application) and a *backend*.

### Dashboard
A web app built with [React](https://react.dev/) + [Typescript](https://www.typescriptlang.org/), to see more information check the dashboard [README](dashboard/README.md).

### Backend
A Python http server built with [Django](https://www.djangoproject.com/) + [DRF](https://www.django-rest-framework.org/), to see more information check the backend [README](/backend/README.md).


# Build

Create a .env file in /dashboard (Do not forget to check and set the variables and their values)
```sh
 cp ./dashboard/.env.example ./dashboard/.env
```

Create a secret key for Django:
```sh
export DJANGO_SECRET_KEY=$(openssl rand -base64 22)
```
We are not using sessions or anything like that right now, so changing the secret key won't be a big deal.


Add a `application_default_credentials.json` file with your ADC in the root of the project.
```sh
gcloud auth application-default login
cp ~/.config/gcloud/application_default_credentials.json .
```

After setting up your connection with Google Cloud with the following commands:

```sh
cloud-sql-proxy kernelci-production:us-central1:postgresql2 &
gcloud auth application-default login
```

 If it doesn't work, check the [Configure ADC with your Google Account](https://cloud.google.com/docs/authentication/provide-credentials-adc#google-idp) documentation.

Create a secret file with the database password:
```sh
mkdir -p backend/runtime/secrets
echo <password> > backend/runtime/secrets/postgres_password_secret
```

If you are going to use a database user other than `kernelci`, set it to `DB_DEFAULT_USER`:
```sh
export DB_DEFAULT_USER=<user>
```
Startup the services:
 ```sh
 docker compose up --build -d
 ```

## Deploying to production

To deploy to prod you need to push a tag in the `release/YYYYMMDD.N` format
like: `release/20240910.0`

## Test results email reports

See details about our new [notifications](docs/notifications.md) system.

## Contributing 

There is an [onboarding guide](docs/Onboarding.md) to help get acquainted with the project.

