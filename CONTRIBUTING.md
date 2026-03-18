# Contributing to KernelCI Dashboard

KernelCI Dashboard is an open-source project and contributions of all kinds are welcome — bug reports, fixes, features, tests, and documentation. This guide explains how to get started, report issues, and submit changes.

## Before you start

- Read the README for an overview of the monorepo.
- We recommend following the [Onboarding guide](./docs/Onboarding.md) to set up your environment and learn the project workflow. **Start here** if this is your first setup.
- New to the project? Pick an issue labeled ["good first issue"](https://github.com/kernelci/dashboard/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

## Useful links

- README: [./README.md](./README.md)
- Onboarding guide: [./docs/Onboarding.md](./docs/Onboarding.md)
- Open issues: https://github.com/kernelci/dashboard/issues
- Good first issues: https://github.com/kernelci/dashboard/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22

## Reporting bugs

#### Did you find a bug?

- Ensure the bug was not already reported by searching on GitHub under Issues: https://github.com/kernelci/dashboard/issues
- If you're unable to find an open issue addressing the problem, open a new one: https://github.com/kernelci/dashboard/issues/new
  - Include a clear title and description
  - Add steps to reproduce, logs, and screenshots if applicable
  - Provide a code sample or an executable test case demonstrating the expected behavior that is not occurring

## How you can contribute

- Report bugs with clear reproduction steps and logs
- Propose enhancements with a brief problem statement and solution outline
- Submit pull requests that fix issues or improve code/docs
- Improve tests and developer experience

## Development workflow

1. Fork the repo and create a feature branch from main
2. Keep PRs focused and small; one change per PR
3. Follow Conventional Commits for commit messages (see Conventional Commits below)
4. Run services locally (backend, frontend, or Docker) as described in the Onboarding guide; ensure builds and checks pass
5. Update documentation and add tests when applicable
6. Ensure the PR passes automated checks; see the suggested workflow in the "Make your code pass automated code checks" section

### Guidelines for issues to create

We encourage actionable, well-defined issues. A good issue includes:
- A clear title and description of the problem or feature
- Steps to reproduce (for bugs), with logs and screenshots if applicable
- For features: a brief explanation of the desired behavior and why it would benefit the project

Examples of good issues:
- [Display Test Results Hierarchically: Group Test Cases Under Their Parent Test Suites](https://github.com/kernelci/dashboard/issues/1800)
- [Tree Details Page: each grouping of execution items in the tests execution list](https://github.com/kernelci/dashboard/issues/286)

### Guidelines for PRs to create

A good PR includes:
- A title that follows the Conventional Commits format (e.g., `fix(backend): correct pagination offset`)
- A body describing the motivation, approach, and any trade-offs
- Screenshots or GIFs for UI changes
- References to related issues (e.g., `Closes #123`)

Examples of good PRs:
- [feat(deploy): migrate compose-next to single-env deployment with profiles and prebuilt images](https://github.com/kernelci/dashboard/pull/1759)
- [fix: always initialize Prometheus multiproc directory on process_pending](https://github.com/kernelci/dashboard/pull/1789)

## Staging environment

If you don't have access to the production database, you can point the frontend to the staging API at `https://staging.dashboard.kernelci.org`. To do so, set `VITE_API_BASE_URL=https://staging.dashboard.kernelci.org` in your `dashboard/.env` file (copy from `dashboard/.env.example`). Ask for access in the `#webdashboard` channel on [KernelCI Discord](https://discord.gg/GRv3RhUa6P).

## Conventional Commits

### Suggested commit format

We recommend following the Conventional Commits specification (https://www.conventionalcommits.org/en/v1.0.0/#specification), which has the following format:

```shell
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types used in this project:

1. `fix`: the commit patches a bug in the codebase.
2. `feat`: the commit introduces a new feature to the codebase.
3. `feat!` or `fix!`: the commit introduces a breaking API change.
4. `style`: changes that do not affect the meaning of the code (formatting, whitespace).
5. `refactor`: a code change that neither fixes a bug nor adds a feature.
6. `docs`: documentation-only changes.
7. `test`: adding or correcting tests.
8. `build`: changes that affect the build system or external dependencies.
9. `ci`: changes to CI configuration files and scripts (e.g., GitHub Actions).
10. `chore`: other changes that don't modify src or test files.

When a commit introduces a breaking change in the API it is recommended to add a `BREAKING CHANGE:` footer.

 To provide contextual information, a scope may be provided alongside the type. This needs to be contained within parentheses, for example, `feat(parser): add ability to parse arrays`.

You can find more details on the Conventional Commits specification site.

## Make your code pass automated code checks

- Backend
  - See [backend/README.md](backend/README.md) for environment and commands
  - Run linting: `poetry run flake8`
  - Run type checks (optional but recommended): `poetry run mypy`
  - Run tests: `poetry run pytest`
  - Apply formatting with `poetry run black .` before committing; the `backend/pre-commit` and `backend/pre-push` hooks can help automate this — see [backend/README.md](backend/README.md) for installation instructions
- Frontend
  - See [dashboard/README.md](dashboard/README.md) for scripts and commands
  - Run linting: `pnpm lint`
  - Run unit tests: `pnpm test`
  - Run end-to-end tests: `pnpm e2e`
  - Ensure the app builds: `pnpm build`
- CI
  - Make a Pull Request and wait for someone to approve the execution of GitHub Actions; if any check fail, they must be fixed for your PR to be approved

## Pull requests

- Use a title that follows the Conventional Commits format (e.g., `fix(backend): correct pagination offset`)
- Reference related issues (e.g., Closes #123)
- Describe the motivation, approach, and any trade-offs
- Include screenshots/GIFs for UI changes
- Wait for someone to approve the execution of GitHub Actions. Ensure CI is green before requesting reviews
- At least one approval is required before merging
- Merge via the command line (fetch + merge), not the GitHub merge button
- Take a look at merged PRs to see examples of good descriptions and commit messages

## Communication and help

- Ask questions or seek feedback by opening an issue
- You can also reach the team in the #webdashboard channel on the [KernelCI Discord](https://discord.gg/GRv3RhUa6P)

## Licensing

By contributing, you agree that your contributions will be licensed under the project's [LICENSE](./LICENSE) file.
