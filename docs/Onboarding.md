# Getting Onboarded on the KernelCI dashboard project.

This onboarding is written in the form of Tasks that you you can complete to get acquainted with the KernelCI Dashboard project.

## Introduction
The KernCI Dashboard is composed by two main parts

1. The KernelCI Dashboard API
This API is responsible for querying the KernelCI database and returning the data to the KernelCI Dashboard frontend.
Here are made calculations and data processing to return the data in a way that the frontend can understand.
This API is written in Python and uses the Django Rest Framework.

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
> You can also ask for access in the #webdashboard channel in the KernelCI Slack.

> Remember:
> Always try to look to the production dashboard between tasks to see if you can assimilate the code to the project

### Task 0: Check you proxy and Database access
1. Check for the Proxy access in your e-mail, follow the instructions there to run proxy.
2. Check for database access in your e-mail, follow the instructions, try to connect to the database via CLI and see if it is working.

Definition of Done: You have access to the KernelCI Dashboard backend and database.


### Task 1: Run the Backend locally
1. Clone the KernelCI Dashboard repository from the following link: https://github.com/kernelci/dashboard
2. Read the main README.md file to understand the project structure and how to run the project. Don't forget to communicate if there is something that you don't understand and feel free to send a PR with improvements.
3. Go to the `backend` directory, see the README.md from the backend and try running the project locally.

You can use this script to run the backend with environment variables:
```bash
export DEBUG_SQL_QUERY=False # SQL Queries are very verbose, so it's better to keep this variable as False unless needed
export DEBUG=True 
#\"NAME\": \"${DB_DEFAULT_NAME:=playground_kcidb}\",
export DB_DEFAULT="{
    \"ENGINE\": \"${DB_DEFAULT_ENGINE:=django.db.backends.postgresql}\",
    \"NAME\": \"kcidb\",
    \"USER\": \"${DB_DEFAULT_USER:=<your-email-here>}\",
    \"PASSWORD\": \"<your-password-here-don't-forget-to-scape-special-characters>\", 
    \"HOST\": \"${DB_DEFAULT_HOST:=127.0.0.1}\",
    \"PORT\": \"${DB_DEFAULT_PORT:=5432}\",
    \"CONN_MAX_AGE\": ${DB_DEFAULT_CONN_MAX_AGE:=null},
    \"OPTIONS\": {
      \"connect_timeout\": ${DB_DEFAULT_TIMEOUT:=2}
    }
}"

poetry run python3 manage.py runserver
```

> Note:
> It is possible to have authentication issues when escaping special characters. In some cases, it is necessary to add more than one backslash, while in others, no addition is needed. To assist with this, when `DEBUG` is set to `True`, the default database info will be printed in the terminal, allowing you to determine if the characters got escaped as intended.

Definition of Done: You have the KernelCI Dashboard backend running locally.


### Task 2: Get acquainted with the backend

1. Install [httpie](https://github.com/httpie)
1. Check the folder `backend/requests` and see that there are multiple bash scripts file, those are httpie requests, try to run some of those. (If one of those requests is not working, it is a good opportunity to created a ticket or fix in a PR).
1. Try to see in the [KernelCI Dashboard](https://dashboard.kernelci.org/) to see if you can view where those calls are being made.
1. Try to see how the endpoints you can see where the URLs lead to in the `backend/kernelCI_app/urls.py` file.

Definition of Done: You have run some requests to the KernelCI Dashboard API and try to have a high level understanding of at least one endpoint from the dashboard to the database.


### Task 3: Get acquainted with the database
1. Install a Database management software like [DBeaver](https://dbeaver.io/) or [pgAdmin](https://www.pgadmin.org/) 
1. Connect to the KernelCI Database and try to see the tables and the data that is stored there.
1. Read this docs to understand the database: [Database Knowledge](../backend/docs/database-logic.md)
1. Try to make some SQL queries to see what you can do, feel free to look at the Backend code.

Definition of Done: Run a SQL query that gets all the tests from a specific Tree. (Feel free to choose any), you can post the query Result in the Github Issue.

### Task 4: Run the Frontend locally
1. Go to the `dashboard` directory, see the README.md from the frontend and try running the project locally.
1. Look at the folder `api` and see how the requests are made, copy and search for where those requests are being used and see if you can relate with the production dashboard.
1. Try to mess with the code, change some colors, add some logs, try to understand the code structure, if there is a library that you don't know, read the documentation on that.

Definition of Done: You have the KernelCI Dashboard frontend running locally.

### Task 5: Complete a real Task
1. Go to https://github.com/kernelci/dashboard/issues and search for issues with the label `good first issue`.
1. Pick any of those and assign to yourself. 
1. Put in the Current Sprint in the Github project if it is not there already.
1. Submit a PR (Don't forget to use conventional commits)
1. Address the feedback that you receive
1. Get the PR merged

Definition of Done: Get a Task done and merged in the KernelCI Dashboard project.



