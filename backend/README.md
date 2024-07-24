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

Finnaly execute the server with:

```sh
poetry run python3 manage.py runserver
```