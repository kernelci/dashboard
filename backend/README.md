# Backend [![cov](https://kernelci.github.io/dashboard/badges/coverage.svg)](https://github.com/kernelci/dashboard/actions)

## Prerequisites

Before you begin, ensure you have the following installed on your system:

1.  **Poetry**: This project uses Poetry to manage dependencies and virtual environments. If you don't have it installed yet, follow the [official Poetry installation guide](https://python-poetry.org/docs/#installation).

2.  **Redis**: To run the backend outside of a Docker container, you will also need a running Redis instance.

## Installation

Once the prerequisites are in place, you can install the project's dependencies.

1.  Clone the repository and navigate to the `backend` directory.
2.  Run the installation command:
    ```sh
    poetry install
    ```

> NOTE: The **psycopg** library, used to connect to the PostgreSQL database, requires the PostgreSQL development libraries (libpq-dev) to be installed on your operating system. If these are not present, you may encounter an ImportError when the application tries to connect to the database and you should install it with apt or apt-get.

## IDE Configuration (Virtual Environment)

Running `poetry install` creates an isolated virtual environment (`.venv`) for this project. It is crucial to configure your IDE (like VS Code, PyCharm, etc.) to use the Python interpreter from this virtual environment.

To find the exact path to the Python executable inside the virtual environment, run the following command in your terminal:
```sh
poetry env info --executable
```

## Setting up the environment

### General

Start by exporting `DEBUG=True` in order to allow localhost connection and avoid CORS issues (**should NOT be set to True on production environments**).

In order to check messages from the `log_message` function, also export `ENABLE_LOGGING=True`.

It's possible to export `DEBUG_SQL_QUERY=True` if you want to see which SQL queries are made but it is quite verbose, so it's recommended to keep it as False unless needed.

### Databases

For the main database, the backend uses a series of `DB_` environment variables that have to be set such as:

```sh
export DB_NAME=kcidb
export DB_USER=your-email-here
export DB_PASSWORD=your-password-here-dont-forget-to-scape-special-characters
export DB_HOST=127.0.0.1
export DB_PORT=5432
export DB_ENGINE=django_prometheus.db.backends.postgresql
export DB_OPTIONS_CONNECT_TIMEOUT=16
```
> [!NOTE]
> It is possible to have authentication issues when escaping special characters. In some cases, it is necessary to add more than one backslash, while in others, no addition is needed. To assist with this, you can export `DEBUG_DB_VARS=True` to check the database connection info in the terminal, allowing you to determine if the characters got escaped as intended. **This variable should NOT be set to True in production**.

#### SQLite

Before running the server, you must also update a local SQLite database used for caching. You can simply run the [migrate-cache-db.sh](./migrate-cache-db.sh) script, which will update the migrations if needed and apply them.


## Running the server

After connecting to the database, execute the server with:

```sh
poetry run python3 manage.py runserver
```

## Helper scripts

We have a couple of useful scripts:

* [migrate-cache-db.sh](./migrate-cache-db.sh) will create and apply migrations for the cache SQLite database. This runs automatically when running on docker, but you have to run it mannually otherwise.
* [migrate-app-db.sh](./migrate-app-db.sh) will create and apply migrations for the main app, generally used for the local database. This does not run automatically in order to avoid potential problems. Be aware that *if* you have write permissions to the production database it will be changed, so double check that you are connected to the right one (but usually developers won't have write access to the production database anyway).

It is important to note that Django automatically creates migrations based on changes to the models when running the first command of the scripts above. You can edit the migrations manually, and you can also run the commands by hand if you want more control over it.

* [copy_db_data.sh](./scripts/copy_db_data.sh) will copy 7 days of data from you `DB_DEFAULT` to your `DASH_DB`. You can also modify the script for a custom interval, and you can check the [update_db](./kernelCI_app/management/commands/update_db.py) command for other arguments such as `--table` and `--origins`.
* [generate-schema.sh](./generate-schema.sh) will automatically generate the OpenAPI schema for the endpoints. Please use it whenever the ins and outs of endpoints change.


## Running tests

The backend includes unit and integration tests covering some parts of the source code. For detailed information about integration tests, including setup instructions and best practices, see the [Integration Tests documentation](../docs/IntegrationTests.md).

To run all tests, use the following command:

```sh
poetry run pytest
```

To run only the unit tests, use:
```sh
poetry run pytest -m unit
```

Similarly, to run only the integration tests, use:
```sh
poetry run pytest -m integration
```

Since these integration tests might be slow (depending on the endpoint you are requesting, each test case
can take between 1.5s and 5s) we added a command-line flag to run all test cases. By default, only a
subset of tests cases is run to save time. To run all integration test cases, use the
`--run-all` flag:
```sh
poetry run pytest -m integration --run-all
```

> **Performance Tip**: To make tests run significantly faster, use the local database instead of the production database. See the [Integration Tests documentation](../docs/IntegrationTests.md) for detailed setup instructions.

These commands run the tests, splitted into 4 processes. Each process runs a test file. If a test fails for any reason, it's retried up to 4 times.
This behavior is due to the flags we are passing to `addopts` in the `pyproject.toml` settings file.
All test files must follow this naming convention: `*_test.py`. Unit tests must be under a folder with "unit" in its name, and integration tests must be under a folder with "integration" in its name.

The django tests are being done 'externally', that means, instead of using the utilies the framework
has for testing (like `Client` from Django or `APIClient` from DRF) we are performing requests to the
endpoints using the built-in `requests` library from python. Because of that, it's necessary to be running
the server for the django tests to be performed. When running pytest with the server offline, all django 
tests will be skipped.

The tests are also executed in our CI system, and every pull request must pass the tests before
it can be merged.

### Performance tests

The project includes two types of performance testing:

1. **Pytest-Benchmark**: For benchmarking backend components like the ingestion system.

2. **K6**: For load testing API endpoints. Though this is not intrinsically from the backend, it tests the requests to the endpoint and doesn't require the frontend to work.

For detailed information on both types of performance testing, including setup instructions and best practices, see the [performanceTests.md file](../docs/performanceTests.md).


## Cron jobs

We have support for cron jobs using django-crontab. To set up cron jobs, edit the `CRONJOBS` variable in /backend/kernelCI/settings.py

To run said cron jobs locally, execute
```poetry run ./manage.py crontab add```
You don't need to run the backend or server for those cron jobs to work, they will be run in your machine.
You can also use other args such as `show` to show the cron jobs and `remove` to remove them.

These cron jobs will also be automatically executed from the backend container if you are running with docker.
You can check that the cron jobs are listed inside the docker container with
```docker exec -it dashboard-backend-1 crontab -l```
or
```docker exec -it dashboard-backend-1 poetry run ./manage.py crontab show```

If you are a developer and want to skip the cron job setup while you're testing, you can also export `SKIP_CRONJOBS=True` to skip cron jobs entirely.


## Deploy instructions

To check if it is ready for a deploy you can run 
```sh
poetry run python3 manage.py check --deploy
```

To generate a `DJANGO_SECRET_KEY` 
you can use
```sh
openssl rand -base64 22
```

or
```sh
export DJANGO_SECRET_KEY=$(openssl rand -base64 22)
```
We are not using sessions or anything like that right now, so changing the secret key won't be a big deal.


## Requests
In the `/requests` directory we have scripts that execute requests to endpoints using [httpie](https://httpie.io/). They serve as examples of how you could use the API, and what responses you can expect. If you are contributing to some endpoint and change any of the responses, please remember to update those files.

## Debug

For debugging we have four env variables:

- `DEBUG`: Required for local development, returns more data on errors, should not be set to True on production;
- `DEBUG_SQL_QUERY`: logs every query made, can be verbose;
- `DEBUG_DB_VARS`: logs the database connection vars, to check if the characters were escaped correctly, should not be set to True on production;
- `ENABLE_LOGGING`: enables general debug logging.


## Discord Webhook Integration

The webdashboard backend can send notifications to discord via a webhook. In order to enable that, export an environment variable with the URL to the discord webhook called `DISCORD_WEBHOOK_URL`, which should be in the structure of:

`export DISCORD_WEBHOOK_URL https://discord.com/api/webhooks/<webhook_id>/<webhook_token>`

For an introduction on discord webhooks, visit https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks.

For more detailed developer resources, visit https://discord.com/developers/docs/resources/webhook.


## Email notifications

The email notification system is used with cron jobs to be able to send regular updates about specific actions to the relevant recipients. You can check more information about it on [notifications.md](../docs/notifications.md)


## IDE Specific:
You are free to use whichever tool you would like, but here are tips for specific IDEs

## Monitoring and Metrics

The project includes monitoring using Prometheus and Grafana. See the [monitoring documentation](docs/monitoring.md) for detailed information about.

### (Optional): Running in PyCharm

In order to debug backend in PyCharm, just follow these steps:

 - open contents of `backend` in PyCharm
 - click over Python version at the bottom right window corner, then `Add New Interpreter` -> `Add Local Interpreter...`
 - click on `Poetry Environment`, select `Existing Interpreter` and then find `python` executable on correspondent folder.
 - at the top bar, on the bug icon, create a configuration with the following parameters:
   - in `Run` session of the dialog, select `script`, then find the script `manage.py` at the `backend` folder
   - at `script` name input, just enter `runserver`
   - at `Environment Variables`, enter the following values:
     - `DB_ENGINE`: `django.db.backends.postgresql`, `DB_NAME`: `dashboard`, `DB_USER`: `<youremail>@profusion.mobi`, `DB_PASSWORD`: `<yourpassword>`, `DB_HOST`: `127.0.0.1`, `DB_PORT`: `5432`, `DB_OPTIONS_CONNECT_TIMEOUT`: `16`
     - `DEBUG`: `True`

Quote character in password field is escaped normally with `\"` .
