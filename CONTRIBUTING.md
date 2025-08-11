# Contributing to KernelCI Dashboard

KernelCI Dashboard is an open-source project and contributions of all kinds are welcome — bug reports, fixes, features, tests, and documentation. This guide explains how to get started, report issues, and submit changes.

## Before you start

- Read the README for an overview of the monorepo.
- We recommend following the Onboarding guide to set up your environment and learn the project workflow.
- New to the project? Pick an issue labeled "good first issue".

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

## Conventional Commits

### Suggested commit format

We recommend following the Conventional Commits specification (https://www.conventionalcommits.org/en/v1.0.0/#specification), which has the following format:

```shell
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types usually are:

1. fix: meaning the commit patches a bug in the codebase.
2. feat: the commit introduces a new feature to the codebase.
3. feat! or fix!: the commit introduces a breaking API change.
4. Other types are allowed, for example: build, cli, test, docs.

When a commit introduces a breaking change in the API it is recommended to add a BREAKING CHANGE: footer.

To provide contextual information, a scope may be provided alongside the type. This needs to be contained within parenthesis, for example, `feat(parser): add ability to parse arrays`.

You can find more details on the Conventional Commits specification site.

## Make your code pass automated code checks

- Backend
  - See backend/README.md for environment and commands
  - Run linters, tests, and type checks locally; apply formatting
- Frontend
  - See dashboard/README.md for scripts and commands
  - Run linters, tests, and type checks; ensure the app builds
- CI
  - Make a Pull Request and wait for someone to approve the execution of GitHub Actions; if any check fail, they must be fixed for your PR to be approved

## Pull requests

- Reference related issues (e.g., Closes #123)
- Describe the motivation, approach, and any trade-offs
- Include screenshots/GIFs for UI changes
- Wait for someone to approve the execution of Github Actions. Ensure CI is green before requesting reviews
- Take a look at merged PRs to see examples of good descriptions and commit messages

## Communication and help

- Ask questions or seek feedback by opening an issue
- You can also reach the team in the #webdashboard channel on the [KernelCI Discord](https://discord.gg/GRv3RhUa6P)

## Licensing

By contributing, you agree that your contributions will be licensed under the project’s LICENSE file.
