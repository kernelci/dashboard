# KernelCI Dashboard
The goal of this project is to create a new KernelCI Web Dashboard to replace
the existing one available at https://linux.kernelci.org/.  
The new KernelCI Web Dashboard is a web application created to provide access
to static checks, build logs, boot logs and test results related to the Linux kernel
CI system. All that data will be provided by kcidb system from Linux
Foundation.

# Repository
What we have as a repository is a monorepo containing the *dashboard* (the web application) and a *backend*.

### Dashboard
A web app built with [React](https://react.dev/) + [Typescript](https://www.typescriptlang.org/), to see more information check the dashboard [README](dashboard/README.md).

### Backend
A Python http server built with [Django](https://www.djangoproject.com/) + [DRF](https://www.django-rest-framework.org/), to see more information check the backend [README](/backend/README.md).


# Build

Add a application_default_credentials.json file in the root of the project. To do so, follow the "Configure ADC with your Google Account" in the [link](https://cloud.google.com/docs/authentication/provide-credentials-adc#google-idp <https://cloud.google.com/docs/authentication/)provide-credentials-adc#google-idp>). Then, find the `application_default_credentials.json` on `home/.config/gcloud` and copy its content to the file you created.

Create secret files and add your password to playground_kcidb:
```sh
mkdir -p backend/runtime/secrets
uuidgen > backend/runtime/secrets/postgres_password_secret
```

If necessary, change the DB_DEFAULT_USER in the `backend/utils/entrypoint.sh` file.

Startup the services with
 ```sh
 docker compose up --build -d
 ```
 