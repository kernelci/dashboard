---
name: fix-django-dependabot-alerts
description: Fetch all open GitHub Dependabot alerts and remediate vulnerable Python dependencies in Django backends using the project's existing Poetry, uv, or requirements workflow. Use for Django backend dependency security fixes, including transitive dependencies.
metadata:
  author: felipebergamin
---

# Fix Django Dependabot Alerts

Retrieve every open alert, trace vulnerable Python dependencies, apply compatible fixes, and verify the Django backend.

## Mandatory guardrails

- **Never install missing tools.** Before running the workflow, check the required tools and the selected package manager. If any required tool, pinned tool version, plugin, or verification tool is unavailable, stop, list what is missing, and ask the user to install it before running the skill again. Do not install, bootstrap, auto-download, or switch to another tool to bypass this rule. Installing project dependencies with an already available package manager is allowed; installing the tools themselves is not.
- **Never edit lockfiles manually.** Read lockfiles for inspection, but create or update them only through the existing package manager CLI or the project's established dependency compiler/export CLI. Do not patch lockfile entries, hashes, versions, or metadata with editors, scripts, or text replacement. If the CLI cannot generate a valid lockfile, report the blocker.
- **Never perform major package upgrades.** Compare the current resolved version and proposed version using numeric semantic-version components (`<major>.<minor>.<patch>`). If the major component changes, notify the user and skip that package. This applies to direct dependencies, transitive dependencies, parent updates, overrides, and incidental resolver changes, even when an existing range allows the upgrade. Prefer a patched version in the current major when available. If versions cannot be interpreted confidently, skip and report rather than guessing.
- Check this major-version boundary before changing manifests or resolving dependencies. Keep targeted resolution within the existing major versions. If resolution nevertheless introduces a major upgrade, do not retain that upgrade: restore only this attempt's changes from a pre-change snapshot while preserving user changes, then retry within the allowed major or skip and report. Never repair the generated lockfile by hand.

## Prerequisites and scope

- Check `gh --version`, `gh auth status`, and `jq --version`. Resolve the repository with `gh repo view --json nameWithOwner,defaultBranchRef`; honor the user's explicit repository and GitHub host.
- Read repository instructions, inspect `git status`, and identify backend project roots, Python versions, `manage.py`, dependency manifests, lockfiles, and CI commands.
- Detect the existing dependency manager from lockfiles and documented commands: `poetry.lock` for Poetry, `uv.lock` for uv, or requirements inputs/constraints and their documented compiler. Use the pinned tool version. A `pyproject.toml` or build backend alone does not identify the package manager. If several lockfiles coexist, establish which CI/deployment consumes before editing them.
- Preserve user changes, dependency groups, extras, environment markers, private sources, and the existing manager. Use a project virtual environment; do not modify system Python or switch managers as part of remediation.
- Inspection-only requests authorize inspection; apply updates when remediation is requested. Commit, push, create PRs, merge, dismiss alerts, or post comments only when authorized by the user.
- Authentication or alert access failures require reporting the error and required access. A 403/404 or incomplete response is not an empty inventory.

## Monorepo alert routing

This repository contains two dependency projects:

| Project path | GitHub alert ecosystem | Dependency manager | Manifest and lockfile |
| --- | --- | --- | --- |
| `dashboard/` | `npm` | pnpm | `dashboard/package.json`, `dashboard/pnpm-lock.yaml` |
| `backend/` | `pip` | Poetry | `backend/pyproject.toml`, `backend/poetry.lock` |

Route each alert using both `security_vulnerability.package.ecosystem` and `dependency.manifest_path`. GitHub uses `npm` for pnpm dependencies and `pip` for Poetry dependencies. Fetch all pages before routing; do not assume every alert belongs to this skill's project.

Handle only `pip` alerts whose manifest path is under `backend/`; use Poetry and run dependency commands from `backend/`. Report `npm` alerts under `dashboard/` as belonging to the pnpm skill and leave those dependencies unchanged. The alternative Python manager guidance below applies only if the backend has explicitly migrated away from Poetry; confirm the current files and repository instructions first.

If the ecosystem and manifest path disagree, the path is absent, or the alert points outside these project roots, inspect the referenced files before acting. Do not guess ownership or modify the other project. Report ambiguous or unmapped alerts separately; grouping fixes must preserve manifest ownership even when package names overlap.

## 1. Fetch every page of open alerts


Run from the target repository.

```bash
alerts_dir=$(mktemp -d)
gh api --method GET --paginate --slurp \
  -H 'Accept: application/vnd.github+json' \
  'repos/kernelci/dashboard/dependabot/alerts?state=open&per_page=100' \
  > "$alerts_dir/pages.json"
```

Check the exit status before processing the file. On any failure, stop alert processing: partial pages must not be used as a complete inventory. `--paginate` follows pagination links until exhausted; `--slurp` wraps all pages in an outer array. A page size of 100 alone does not fetch all alerts.

After a successful fetch, flatten and deduplicate by alert number. Retain distinct advisories and manifest paths for the same package:

```bash
jq '[.[][]] | unique_by(.number) | map({
  number,
  url: .html_url,
  ecosystem: .security_vulnerability.package.ecosystem,
  package: .security_vulnerability.package.name,
  manifest: .dependency.manifest_path,
  scope: .dependency.scope,
  relationship: .dependency.relationship,
  advisory: .security_advisory.ghsa_id,
  severity: .security_advisory.severity,
  vulnerable_range: .security_vulnerability.vulnerable_version_range,
  first_patched_version: (.security_vulnerability.first_patched_version.identifier // null)
})' "$alerts_dir/pages.json" > "$alerts_dir/alerts.json"
```

Require successful JSON processing before proceeding. Retain raw pages for advisory details. Summarize total alerts and affected packages, manifests, severities, and patched versions. Handle pip ecosystem alerts mapped to Python backend projects; report other ecosystems or package managers as outside this skill's scope. Only a successfully fetched empty inventory means no open alerts. A null patched version means no published fix is identified, not that the alert is resolved.

## 2. Trace affected backend dependencies

Map each alert's manifest to the project and to the files actually consumed by CI, containers, and deployment. Preserve distinct advisory and manifest records even when they refer to the same package. Generated requirements exports must be regenerated from their authoritative source.

Inspect the resolved graph and installed versions using the project's environment:

- Poetry: `poetry show --tree`, `poetry show <package>`.
- uv: `uv tree` and the lockfile; `uv pip list` for the selected project environment.
- requirements/pip: `python -m pip show <package>` and the compiled requirements/constraints. Use an existing graph tool if available; never install a missing graph tool.

Use Python distribution names, not import names. Normalize names by lowercasing and treating runs of hyphens, underscores, and dots alike. Distinguish runtime, development, optional, and platform-specific dependency paths. Check all resolved versions and supported Python/platform combinations against the relevant advisory ranges.

Dependabot describes the default branch and may lag behind local changes. Verify an already fixed dependency instead of upgrading again. A null first patched version needs investigation; report missing fixes explicitly.

## 3. Choose and apply compatible fixes

Prefer the smallest change that escapes every applicable vulnerable range. Use PEP 440 version/specifier handling (for example, the project's available `packaging` library), not string comparison or npm semver assumptions. Advisory ranges may describe different patched release lines; inspect advisory details and release notes before choosing a version.

For Django, prefer a security patch in the current supported release line when available. Verify compatibility with the project's Python version, Django REST Framework, database drivers, middleware, authentication, and other affected integrations. If remediation requires a different major version, notify the user and skip Django. For a minor release-line update within the same major, assess deprecations and migration implications and keep unrelated modernization out of scope.

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

## 4. Verify the Django backend

Run checks in the project's environment (`poetry run`, `uv run`, or its virtualenv) and follow existing CI/test settings:

- Check manifest/lock consistency and dependency resolution. For Poetry use `poetry check`; for uv use `uv lock --check`. Run the environment's `python -m pip check` when pip is present, or the manager's supported equivalent.
- Reinspect locked and installed versions against every affected advisory. Account for optional groups and platform markers, not just one installed environment.
- Run `python manage.py check` using existing test/development settings. If model or migration compatibility is affected, run `python manage.py makemigrations --check --dry-run` where supported by the pinned Django version. These commands require configured services/settings; report missing prerequisites rather than fabricating settings.
- Run the repository's relevant pytest/pytest-django or Django test suite, plus existing lint/type checks where applicable. Prioritize affected API, authentication, ORM, middleware, and background-task behavior. Use an isolated test database and documented service setup; never run migrations against production as verification.
- Use an existing `pip-audit` workflow as a supplementary security check when available; findings can differ from GitHub's. Do not add an audit dependency solely to run this skill.
- Review expected manifest, lockfile, and generated export changes. Investigate unrelated churn while preserving user changes. Distinguish pre-existing failures, upgrade regressions, and checks blocked by unavailable services.

GitHub alerts may stay open until fixes reach the default branch and GitHub rescans it. Report locally verified fixes without claiming the remote alerts have closed.

## 5. Report results

Provide a compact table with alert number, package/manifest, old and resolved versions, and outcome. Include manager used, files changed, checks run, unresolved alerts, missing fixes, and out-of-scope ecosystems. Report skipped major upgrades with current and required versions, missing tools, and compatibility blockers.

## References

- Inspired by [kexplo's Dependabot remediation workflow](https://github.com/kexplo/skills/blob/main/skills/fix-js-dependabot-alerts/SKILL.md).
- [GitHub CLI pagination](https://cli.github.com/manual/gh_api)
- [Poetry commands](https://python-poetry.org/docs/cli/), [uv dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/), and [Django management commands](https://docs.djangoproject.com/en/stable/ref/django-admin/)
