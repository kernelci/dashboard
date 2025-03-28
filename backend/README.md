# Backend

To run it, it's necessary to have Poetry installed. To run it outside the docker
you will also need to have redis installed and a server running. Then run,

```sh
poetry install
```

To configure the database connection, the Backend uses a `DB_DEFAULT` variable 
that must have a JSON string such as:

```sh
export DB_DEFAULT="{
    \"ENGINE\": \"${DB_DEFAULT_ENGINE:=django.db.backends.postgresql}\",
    \"NAME\": \"${DB_DEFAULT_NAME:=playground_kcidb}\",
    \"USER\": \"${DB_DEFAULT_USER:=<DB-USER>}\",
    \"PASSWORD\": \"<DB-PASSWORD>\",
    \"HOST\": \"${DB_DEFAULT_HOST:=127.0.0.1}\",
    \"PORT\": \"${DB_DEFAULT_PORT:=5432}\",
    \"CONN_MAX_AGE\": ${DB_DEAFULT_CONN_MAX_AGE:=null},
    \"OPTIONS\": {
      \"connect_timeout\": ${DB_DEFAULT_TIMEOUT:=2}
    }
}"
```
Attention to <DB-USER> and <DB-PASSWORD> placeholders

After connecting to Google Cloud, execute the server with:

```sh
poetry run python3 manage.py runserver
```

## Running unit tests
The backend includes unit tests covering some parts of the source code. To run the tests, use the following command:

```sh
poetry run pytest
```

This command runs the tests, splitted into 4 processes. Each process runs a test file. If a test fails for any reason, it's retried up to 4 times.
This behavior is due to the flags we are passing to `addopts` in the `pyproject.toml` settings file.
All unit test files must follow this naming convention: `*_test.py`.

endpoints using the built-in `requests` library from python. Because of that, it's necessary to be running the server for the django tests to be performed. When running pytest with the server


The django tests are being done 'externally', that means, instead of using the utilies the framework
has for testing (like `Client` from Django or `APIClient` from DRF) we are performing requests to the
endpoints using the built-in `requests` library from python. Because of that, it's necessary to be running
the server for the django tests to be performed. When running pytest with the server offline, all django 
tests will be skipped.

Also, since django tests might be slow (depending on the endpoint you are requesting, each test case
can take between 1.5s and 5s) we added a new command-line flag to run all test cases. By default, only a
subset of tests cases is run to save time, especially during push. To run all test cases, use the
`--run-all` flag:

```sh
poetry run pytest --run-all
```

The command above is also executed in our CI system, and every pull request must pass the tests before
it can be merged.

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


# Deploy instructions

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


# Requests
In the `/requests` directory we have scripts that execute requests to endpoints using [httpie](https://httpie.io/)


# Debug

For debugging we have two env variables

`DEBUG` and `DEBUG_SQL_QUERY` that can be set to `True` to enable debugging. The reason `DEBUG_SQL_QUERY` is separated is that it can be very verbose.

## Open API generate
You can update the OpenAPI schema by running the `generate-schema.sh` script


## Discord Webhook Integration

The webdashboard backend can send notifications to discord via a webhook. In order to enable that, export an environment variable with the URL to the discord webhook called `DISCORD_WEBHOOK_URL`, which should be in the structure of:

`export DISCORD_WEBHOOK_URL https://discord.com/api/webhooks/<webhook_id>/<webhook_token>`

For an introduction on discord webhooks, visit https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks.

For more detailed developer resources, visit https://discord.com/developers/docs/resources/webhook.

## IDE Specific:
You are free to use whichever tool you would like, but here are tips for specific IDEs


### (Optional): Running in PyCharm

In order to debug backend in PyCharm, just follow these steps:

 - open contents of `backend` in PyCharm
 - click over Python version at the bottom right window corner, then `Add New Interpreter` -> `Add Local Interpreter...`
 - click on `Poetry Environment`, select `Existing Interpreter` and then find `python` executable on correspondent folder.
 - at the top bar, on the bug icon, create a configuration with the following parameters:
   - in `Run` session of the dialog, select `script`, then find the script `manage.py` at the `backend` folder
   - at `script` name input, just enter `runserver`
   - at `Environment Variables`, enter the following values:
     - `DB_DEFAULT`: `{"ENGINE": "django.db.backends.postgresql", "NAME": "playground_kcidb", "USER": "<youremail>@profusion.mobi", "PASSWORD": "<yourpassword>", "HOST": "127.0.0.1", "PORT": "5432", "CONN_MAX_AGE": null, "OPTIONS": {"connect_timeout": 2, "sslmode": "disable"}}`
     - `DEBUG`: `True`

Quote character in password field is escaped normally with `\"` .
