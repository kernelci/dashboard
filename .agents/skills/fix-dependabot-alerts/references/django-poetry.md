# Django and Poetry remediation

Confirm Python versions, `manage.py`, CI commands, and the manager actually consumed by deployment. This backend uses Poetry. Detect any explicit migration from lockfiles and documented commands: `poetry.lock` for Poetry, `uv.lock` for uv, or requirements inputs/constraints and their compiler. A `pyproject.toml` or build backend alone does not identify the manager. If lockfiles coexist, establish which CI/deployment consumes before editing.

Check the selected manager and pinned version before use, without automatic tool installation. Use the project virtual environment; do not modify system Python or switch managers. Preserve groups, extras, environment markers, private sources, and Python compatibility bounds. Follow the shared guardrails and reporting requirements in [SKILL.md](../SKILL.md).

## Trace affected backend dependencies

Map each alert's manifest to the project and to the files actually consumed by CI, containers, and deployment. Preserve distinct advisory and manifest records even when they refer to the same package. Generated requirements exports must be regenerated from their authoritative source.

Inspect the resolved graph and installed versions using the project's environment:

- Poetry: `poetry show --tree`, `poetry show <package>`.
- uv: `uv tree` and the lockfile; `uv pip list` for the selected project environment.
- requirements/pip: `python -m pip show <package>` and the compiled requirements/constraints. Use an existing graph tool if available; never install a missing graph tool.

Use Python distribution names, not import names. Normalize names by lowercasing and treating runs of hyphens, underscores, and dots alike. Distinguish runtime, development, optional, and platform-specific dependency paths. Check all resolved versions and supported Python/platform combinations against the relevant advisory ranges.

Dependabot describes the default branch and may lag behind local changes. Verify an already fixed dependency instead of upgrading again. A null first patched version needs investigation; report missing fixes explicitly.

## Choose and apply compatible fixes

Prefer the smallest change that escapes every applicable vulnerable range. Use PEP 440 version/specifier handling (for example, the project's available `packaging` library), not string comparison or npm semver assumptions. Advisory ranges may describe different patched release lines; inspect advisory details and release notes before choosing a version.

For Django, prefer a security patch in the current supported release line when available. Verify compatibility with the project's Python version, Django REST Framework, database drivers, middleware, authentication, and other affected integrations. If remediation requires a different major version, assess Django release notes, deprecations, migration requirements, and integration compatibility before applying it; include the update and verification results in the dedicated major-updates report. For a minor release-line update within the same major, assess deprecations and migration implications and keep unrelated modernization out of scope.

### Poetry

- Update the authoritative dependency declaration only if its existing range excludes the selected fix or its minimum should be tightened. Preserve PEP 621 or legacy Poetry syntax, extras, sources, groups, and compatible upper bounds.
- Run `poetry update <package>` (or a small set of affected packages) to resolve the fix within project constraints and update `poetry.lock`. Verify the selected version; a successful command alone does not prove remediation.
- Install using the repository's documented `poetry install` or `poetry sync` workflow and groups. Regenerate checked-in exports only with the existing export tooling.

### uv

- Adjust the existing declaration when necessary, preserving its group and markers.
- Use `uv lock --upgrade-package <package>` for a targeted lock update, then the project's `uv sync` workflow and groups. Inspect the selected version and any resolver changes.

### Requirements and pip-tools

- Edit the authoritative requirements input or constraint, preserving includes, markers, extras, and supported version bounds.
- For pip-tools, run the existing compile command with `--upgrade-package <package>`, retaining its output, hash, index, and constraint options. Regenerate hashes rather than editing a hashed output by hand.
- For directly maintained requirements, update the relevant pin/range and resolve/install via the project's established environment workflow. A `pip install --upgrade` that changes only the local environment does not fix the repository.

### Transitive vulnerabilities and resolver conflicts

Try a targeted lock refresh within the parent's supported child range, then a compatible parent update. Use constraints only when the manager actually consumes them and the resulting graph remains compatible. Python managers do not share pnpm's override mechanism: do not invent a Poetry override or bypass dependency checks with `--no-deps`.

If the parent excludes every patched child, find a compatible parent release or report the blocker. Do not force an incompatible child version. For every fix, retain the mapping to all alerts it addresses and verify that no vulnerable copy remains in another group or manifest.

## Verify the Django backend

Run checks in the project's environment (`poetry run`, `uv run`, or its virtualenv) and follow existing CI/test settings:

- Check manifest/lock consistency and dependency resolution. For Poetry use `poetry check`; for uv use `uv lock --check`. Run the environment's `python -m pip check` when pip is present, or the manager's supported equivalent.
- Reinspect locked and installed versions against every affected advisory. Account for optional groups and platform markers, not just one installed environment.
- Run `python manage.py check` using existing test/development settings. If model or migration compatibility is affected, run `python manage.py makemigrations --check --dry-run` where supported by the pinned Django version. These commands require configured services/settings; report missing prerequisites rather than fabricating settings.
- Run the repository's relevant pytest/pytest-django or Django test suite, plus existing lint/type checks where applicable. Prioritize affected API, authentication, ORM, middleware, and background-task behavior. Use an isolated test database and documented service setup; never run migrations against production as verification.
- Use an existing `pip-audit` workflow as a supplementary security check when available; findings can differ from GitHub's. Do not add an audit dependency solely to run this skill.
- Review expected manifest, lockfile, and generated export changes. Investigate unrelated churn while preserving user changes. Distinguish pre-existing failures, upgrade regressions, and checks blocked by unavailable services.

## References

- [Poetry commands](https://python-poetry.org/docs/cli/), [uv dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/), and [Django management commands](https://docs.djangoproject.com/en/stable/ref/django-admin/).
