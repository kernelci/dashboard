# Running in development

- Install the packager manager [pnpm](https://pnpm.io/installation)

- Install all dependencies with:

```sh
pnpm install
```

Create a .env.development file (Do not forget to check and set the variables and their values)

```sh
 cp .env.example .env.development
```

After establishing the connection with Google Cloud and running `backend`, run the `dashboard` dev server with

```sh
pnpm dev
```

## Running unit tests
The frontend includes unit tests covering some parts of the source code. To run the tests, use the following command:

```sh
pnpm test
```

# Routing and State Management

A big part of this project is to have shareable links
So we should use the URL to manage state as much as possible.

Also, we are using file based routing in the tanstack router, only files that starts with ~ are read by the Vite plugin.

# Feature Flags

They are used when we want to hide a feature for some users, without having to do branch manipulation.
Right now the only feature flag is for Dev only and it is controlled by the env 
`FEATURE_FLAG_SHOW_DEV=false` it is a boolean.
