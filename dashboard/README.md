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

Run the dev server with
```sh
pnpm dev
```

# Routing and State Management

A big part of this project is to have shareable links
So we should use the URL to manage state as much as possible.

Also, we are using file based routing in the tanstack router, only files that starts with ~ are read by the Vite plugin.


