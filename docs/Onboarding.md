# Getting Onboarded on the KernelCI dashboard project.

This onboarding is written in the form of Tasks that you you can complete to get acquainted with the KernelCI Dashboard project.

## Introduction
The KernelCI Dashboard is composed by two main parts

1. The KernelCI Dashboard Backend
This API is responsible for querying the KernelCI database and returning the data to the KernelCI Dashboard frontend.
Here are made calculations and data processing to return the data in a way that the frontend can understand.
This API is written in Python and uses the Django Rest Framework.

Our backend also houses an email notification system and a submissions monitoring command, which are both disconnected from the frontend. The email notification system runs on a cron job, tracking changes on trees and reporting its status, regressions, fixes and more. You can check more details about it on [notifications.md](notifications.md). The submission monitoring - also known as "ingester" - is used to listen changes in a folder and insert json data into the database through the django models. See more information about it on [monitor_submissions.md](../backend/docs/monitor_submissions.md); the ingester is a port from the [kcidb-ng repository](https://github.com/kernelci/kcidb-ng).

2. The KernelCI Dashboard Frontend
This is the user interface that will be used to interact with the KernelCI Dashboard API.
Here the user can see the data returned by the API in a more user-friendly way and request diferents forms of visualization.
This frontend is written in TypeScript and uses the React library.

> Note:
> The Dashboard is live in the following link: [KernelCI Dashboard](https://dashboard.kernelci.org/)

## Tasks
> Note:
> In case you don't have access to the backend, feel free to use the staging api to run the Frontend Code and send PRs.
> https://staging.dashboard.kernelci.org:9000
> You can also ask for access in the #webdashboard channel in the KernelCI Discord.

> Remember:
> Always try to look to the production dashboard between tasks to see if you can assimilate the code to the project

### Task 0: Check your ssh and database access
In order to access the production database, you must be granted access to it first - ssh connection and database user. If you don't have access to the production database, you can point the environment variables from the main database to a local database.

1. Connect to the Azure database ssh bridge:

* Create a new SSH key and add it to your ssh agent. You can follow this [Github guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) for it (but you don't need to add the key to your Github account, it can stay only in your PC).
* Share the public SSH key to the database maintainer, so you can receive access to the SSH tunnel.
* Connect to the database via SSH tunnel with the provided URL.

2. You should ask for the creation of a new user/password for the database access. Once you have your credentials, connect to the database via `psql`, pgAdmin, DBeaver or any other postgresql manager.
3. Start up the local dashboard-db by starting its docker container and running the [migration script](../backend/migrate-app-db.sh). This secondary database is very useful for local development and you can modify it as much as you like.

Definition of Done: You have access to kcidb and created the local database.


### Task 1: Install and run redis locally
Redis is needed for the use of query cache in the backend, so it must be running before you start the backend. There are a couple of ways to install Redis ([see official docs](https://redis.io/docs/latest/operate/oss_and_stack/install/archive/install-redis/)), and any method is fine as long as you don't encounter any Redis-related errors when running Task 2 (starting the backend).

A simple way is through snap, which will run Redis as a background service and start it automatically when you boot your computer (if set to auto-start). Be careful when running the project with Docker, as you need to stop the local Redis server to avoid port conflicts. If installed via snap, you can check its status with `sudo snap services`, and start or stop it with `sudo snap start redis` or `sudo snap stop redis`.

Definition of Done: The Redis server is running and you do not encounter Redis-related errors when starting the backend in Task 2.


### Task 2: Run the Backend locally
1. Clone the KernelCI Dashboard repository from the following link: https://github.com/kernelci/dashboard
2. Go to the `backend` directory, see the [README.md](../backend/README.md) from the backend and run the project locally (read at least up to "Running the server").
3. At this point you should have already read the [main README](../README.md) file for a general context of the project and how to run it too. If there are any mistakes feel free to send a PR with corrections and changes.

Definition of Done: You have the KernelCI Dashboard backend running locally.


### Task 3: Get acquainted with the backend
> Note:
> Although the example requests use httpie, you can use any other request tool (such as curl, Postman, or Insomnia) to interact with the API.

1. Install [httpie](https://github.com/httpie)
2. Check the folder `backend/requests` and see that there are multiple bash scripts file, those are httpie requests, try to run some of those. (If one of those requests is not working, it is a good opportunity to created a ticket or fix in a PR).
3. Try to look in the [KernelCI Dashboard](https://dashboard.kernelci.org/) to see if you can view where those calls are being made.
4. Check the URL to endpoint relationship in the [backend/kernelCI_app/urls.py](../backend/kernelCI_app/urls.py) file.

Definition of Done: You have run some requests to the KernelCI Dashboard API and try to have a high level understanding of at least one endpoint from the dashboard to the database.


### Task 4: Get acquainted with the database
1. Install a Database management software like [DBeaver](https://dbeaver.io/) or [pgAdmin](https://www.pgadmin.org/) 
2. Connect to the KernelCI Database and try to see the tables and the data that is stored there.
3. Read this docs to understand the database: [Database Knowledge](../backend/docs/database-logic.md)
4. Make some direct SQL queries to see what you can do, feel free to look at the Backend code.
5. Move some data from kcidb to the dashboard_db by running the `update_db` command with `poetry run python3 manage.py update_db`. You don't need a lot of data, specially considering that the database is heavy. For now, just a couple of hours should suffice.

Definition of Done: Run a SQL query that gets all the tests from a specific Tree. (Feel free to choose any), post the query Result in the Github Issue.


### Task 5: Run the Frontend locally
1. Go to the `dashboard` directory, see the [README.md](../dashboard/README.md) from the frontend and try running the project locally.
2. Look at the folder `api` and see how the requests are made, search for where those functions are being used (where the requests are made) and see if you can relate with the production dashboard.
3. Try to mess with the code, change some colors, add some logs, try to understand the code structure, if there is a library that you don't know, read the documentation on that.

Definition of Done: You have the KernelCI Dashboard frontend running locally.


### Task 6: Run the project in docker

> [!TIP]
> Running the project with Docker is especially useful for testing, as the production instance also runs in containers. This setup provides a more similar environment to production and helps ensure consistency between development and deployment.

1. Make sure your backend, frontend, db ssh and Redis are **not** running locally.
  - If Redis is running and you installed it with snap, stop it with:
    ```bash
    sudo snap stop redis
    ```

2. Set up the `.env` files in the root of the project by copying the `.env.name.example` files and removing the `.example` at the end of the filenames. For the development you'll need to change the following variables in the .env.backend file:
```
DEBUG_SQL_QUERY=False
DEBUG=True

DB_NAME=dashboard
DB_USER=admin
DB_PASSWORD=admin
DB_HOST=dashboard_db  # Docker can't connect to the ssh tunnel host directly.
DJANGO_SECRET_KEY=$(openssl rand -base64 22)
```

If running the notification commands, you should add to your .env.backend the following variables:
```
EMAIL_HOST_USER=<your email>
EMAIL_HOST_PASSWORD=<your app password>
```
For the onboarding you can skip those, but do check out the [notifications](./notifications.md) part of the dashboard.

Other environment variables can be set as needed.

3. Start up the services with the command:

```bash
docker compose up --build -d
```

After starting the services, you can check if your Docker containers are running with:

```bash
docker ps
```

If any container fails or exits unexpectedly, you can inspect the logs with:

```bash
docker logs <container_id>
```

Definition of Done: The KernelCI Dashboard (backend and frontend) is running via Docker and accessible locally.

> [!NOTE]
> The Task 6 teaches you how to build and run the project locally during development. Note that you can also run the project using pre-built images generated by the [deploy-containers](../.github/workflows/deploy-containers.yaml) workflow, using the [docker-compose-next](../docker-compose-next.yml) file to pull and run these pre-built images without rebuilding them.

### Task 7: Complete a real Task
1. Go to https://github.com/kernelci/dashboard/issues and search for issues with the label `good first issue`.
2. Pick any of those and assign to yourself. 
3. Put in the Current Sprint in the Github project if it is not there already.
4. Submit a PR (Don't forget to use conventional commits)
5. Address the feedback that you receive
6. Get the PR merged

Definition of Done: Get a Task done and merged in the KernelCI Dashboard project.
