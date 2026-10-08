---
name: fix-pnpm-dependabot-alerts
description: Fetch all open GitHub Dependabot vulnerability alerts and fix affected JavaScript or Node.js dependencies in pnpm projects, including workspaces and transitive dependencies. Use for Dependabot alert remediation with pnpm.
metadata:
  author: felipebergamin
---

# Fix pnpm Dependabot Alerts

Retrieve open alerts, trace affected dependency paths, apply compatible patched versions, and verify the resulting pnpm dependency graph.

## Mandatory guardrails

- **Never install missing tools.** Before running the workflow, check the required tools and the selected package manager. If any required tool, pinned tool version, plugin, or verification tool is unavailable, stop, list what is missing, and ask the user to install it before running the skill again. Do not install, bootstrap, auto-download, or switch to another tool to bypass this rule. Installing project dependencies with an already available package manager is allowed; installing the tools themselves is not.
- **Never edit lockfiles manually.** Read lockfiles for inspection, but create or update them only through the existing package manager CLI or the project's established dependency compiler/export CLI. Do not patch lockfile entries, hashes, versions, or metadata with editors, scripts, or text replacement. If the CLI cannot generate a valid lockfile, report the blocker.
- **Never perform major package upgrades.** Compare the current resolved version and proposed version using numeric semantic-version components (`<major>.<minor>.<patch>`). If the major component changes, notify the user and skip that package. This applies to direct dependencies, transitive dependencies, parent updates, overrides, and incidental resolver changes, even when an existing range allows the upgrade. Prefer a patched version in the current major when available. If versions cannot be interpreted confidently, skip and report rather than guessing.
- Check this major-version boundary before changing manifests or resolving dependencies. Keep targeted resolution within the existing major versions. If resolution nevertheless introduces a major upgrade, do not retain that upgrade: restore only this attempt's changes from a pre-change snapshot while preserving user changes, then retry within the allowed major or skip and report. Never repair the generated lockfile by hand.

## Prerequisites and scope

- Check `gh --version`, `gh auth status`, `jq --version`, and `pnpm --version`. Use the project's pinned pnpm version from `packageManager` when present.
- Resolve the repository with `gh repo view --json nameWithOwner,defaultBranchRef`; honor an explicitly supplied repository and GitHub host.
- Inspect repository instructions, `git status`, manifests, `pnpm-lock.yaml`, and `pnpm-workspace.yaml`. Identify each affected pnpm project or workspace root; a repository can contain several independent lockfiles.
- If authentication or alert access fails, report the error and required access. A 403/404 or incomplete response does not mean there are no alerts.
- Preserve user changes. Inspection-only requests authorize inspection; apply updates when remediation is requested. Commit, push, create PRs, merge, dismiss alerts, or post comments only when the user has authorized those actions.

## Monorepo alert routing

This repository contains two dependency projects:

| Project path | GitHub alert ecosystem | Dependency manager | Manifest and lockfile |
| --- | --- | --- | --- |
| `dashboard/` | `npm` | pnpm | `dashboard/package.json`, `dashboard/pnpm-lock.yaml` |
| `backend/` | `pip` | Poetry | `backend/pyproject.toml`, `backend/poetry.lock` |

Route each alert using both `security_vulnerability.package.ecosystem` and `dependency.manifest_path`. GitHub uses `npm` for pnpm dependencies and `pip` for Poetry dependencies. Fetch all pages before routing; do not assume every alert belongs to this skill's project.

Handle only `npm` alerts whose manifest path is under `dashboard/`; run dependency commands from `dashboard/`. Report `pip` alerts under `backend/` as belonging to the Django/Poetry skill and leave those dependencies unchanged.

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

Require successful JSON processing before proceeding. Retain raw pages for advisory details. Summarize total alerts and affected packages, manifests, severities, and patched versions. Handle npm ecosystem alerts mapped to pnpm projects; report other ecosystems or package managers as outside this skill's scope. Only a successfully fetched empty inventory means no open alerts. A null patched version means no published fix is identified, not that the alert is resolved.

## 2. Trace affected dependencies

Use `pnpm why <package>` and `pnpm list <package> --depth Infinity` at the affected project root. For workspaces, use `pnpm -r why <package>` or `pnpm --filter <workspace-package> why <package>`. Inspect the lockfile when multiple versions or importers are involved.

Match installed versions against every advisory's vulnerable range. Alerts describe the default branch and may lag behind a local fix; an already safe local version needs verification, not another upgrade. Keep separate alert records even when one update fixes several alerts.

## 3. Apply targeted fixes

Choose the smallest compatible change that escapes all applicable vulnerable ranges. The first patched version is a starting point: different major release lines can have separate fixes. Check advisory and release details instead of comparing version strings lexicographically or blindly taking the largest reported minimum.

### Direct dependencies

Use a targeted update at the appropriate root:

```bash
pnpm update <package>@<patched-version>
pnpm --filter <workspace-package> update <package>@<patched-version>
```

Use the workspace form only when needed. Preserve dependency sections, range style, and catalog conventions; update shared catalog declarations when they own the version. Avoid broad `--latest` upgrades or unrelated changes. If a fix requires a major upgrade, notify the user and skip that package.

### Transitive dependencies

Prefer a compatible parent dependency update or a targeted lockfile refresh that resolves a patched child within the parent's supported range. If that cannot fix the alert, use a narrowly scoped override and verify parent compatibility.

Use the override location supported by the pinned pnpm version and established by the repository. Current pnpm uses root `pnpm-workspace.yaml`:

```yaml
overrides:
  'parent-package@<affected-parent-range>><vulnerable-package>': '<patched-version>'
```

Older projects may use root `package.json` under `pnpm.overrides`. Preserve unrelated overrides and avoid competing definitions in both files. Check the pinned version's documentation if its supported location is unclear. Use a global package override only when appropriate for every affected dependency path. Never use an override to cross a package major-version boundary. Report unresolved cases with reasons and next steps.

## 4. Install and verify

- Run `pnpm install` at each affected project or workspace root to update its lockfile. If frozen-lockfile mode blocks an intentional manifest change, use `pnpm install --no-frozen-lockfile` for that update.
- Reinspect every affected dependency path and verify all resolved versions against the advisory ranges. Checking only the manifest or one installed copy is insufficient.
- Run the affected project's existing build, typecheck, and relevant tests as available. Use workspace filters where suitable; distinguish pre-existing failures from upgrade regressions.
- Use `pnpm audit --json` as a supplementary check when registry access is available. Findings may differ from GitHub's. Report failed or unavailable checks explicitly.
- Review the diff for expected manifest, workspace configuration, and lockfile changes. Investigate unrelated churn without discarding user changes.

GitHub alerts may remain open until the updated lockfile reaches the default branch and GitHub rescans it. Describe locally verified remediation without claiming GitHub has already closed the alerts.

## 5. Report results

Provide a compact table with alert number, package/manifest, previous and resolved versions, and outcome. Include checks run, unresolved alerts (including missing patches and out-of-scope ecosystems), and files changed. Explain any override and compatibility tradeoff. Report skipped major upgrades with current and required versions, and any missing tools.

## References

- Adapted in English and narrowed to pnpm from [kexplo's fix-js-dependabot-alerts](https://github.com/kexplo/skills/blob/main/skills/fix-js-dependabot-alerts/SKILL.md).
- [GitHub CLI pagination](https://cli.github.com/manual/gh_api)
- [pnpm update](https://pnpm.io/cli/update) and [pnpm settings](https://pnpm.io/settings)
