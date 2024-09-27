# Backend

To run it, it's necessary to have Poetry installed. Then run,

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
