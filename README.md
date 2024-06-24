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