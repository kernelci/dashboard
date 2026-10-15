---
name: fix-dependabot-alerts
description: Fetch all open GitHub Dependabot alerts and remediate vulnerable dependencies in the KernelCI Dashboard monorepo, routing frontend npm alerts to pnpm and backend pip alerts to Django/Poetry. Report every major package update separately.
---

# Fix Dependabot alerts

Fetch one complete inventory, route alerts to their dependency projects, apply compatible fixes, and verify each affected graph. Honor explicit frontend-only, backend-only, or inspection-only scope. For an unqualified repository remediation request, handle both projects.

## Guardrails

- **Never install missing tools or change the existing ones.** Check required tools and pinned versions before running the affected workflow. If a required tool, version, plugin, or verification tool is unavailable, stop that project's workflow, list what is missing, and ask the user to install it before rerunning. Do not bootstrap, auto-download, switch managers, or use another version to bypass this rule. Installing project dependencies with an already available manager is allowed. A blocker in one project does not prevent authorized work in the other; report the blocked project explicitly.
- **Never edit lockfiles manually.** Generate lockfiles and exports only with the existing package manager or established compiler/export CLI. If it cannot produce a valid lockfile, report the blocker.
- Preserve user changes, dependency sections, groups, extras, sources, markers, and catalog conventions. Snapshot files before resolution so only this attempt's changes can be restored if necessary.
- Major package updates are allowed when needed for remediation. Prefer the smallest compatible fix and avoid unrelated modernization or broad latest-version upgrades. Assess breaking changes and compatibility before applying a major update. This does not permit upgrading the package-manager tools themselves.
- Commit, push, create PRs, merge, dismiss alerts, or post comments only when the user has authorized those actions.
- Use [show-me-your-work](../show-me-your-work/SKILL.md) for the decision trail. Keep logging separate from the dependency procedures.

## Prerequisites and routing

Check `gh --version`, `gh auth status`, and `jq --version`. Resolve the target with `gh repo view --json nameWithOwner,defaultBranchRef`; honor an explicitly supplied repository and GitHub host. Read repository instructions, inspect `git status`, manifests, lockfiles, and documented CI commands.

| Project | Alert ecosystem | Manager | Authoritative files | Procedure |
| --- | --- | --- | --- | --- |
| `dashboard/` | `npm` | pnpm | `dashboard/package.json`, `dashboard/pnpm-lock.yaml` | [pnpm](references/pnpm.md) |
| `backend/` | `pip` | Poetry | `backend/pyproject.toml`, `backend/poetry.lock` | [Django/Poetry](references/django-poetry.md) |

Read the reference for each affected, authorized project before tracing or updating its dependencies. Check its manager and pinned version without triggering automatic tool installation. Run dependency commands from that project root. Alternative Python-manager guidance applies only after an explicit backend migration confirmed by files and repository instructions.

Route using both `security_vulnerability.package.ecosystem` and `dependency.manifest_path`. GitHub calls pnpm dependencies `npm` and Poetry dependencies `pip`. If the path is missing, outside these roots, or inconsistent with the ecosystem, inspect the referenced files before acting. Report unresolved ownership separately; do not guess. Preserve manifest ownership when grouping fixes, even when package names overlap.

## Fetch every page once

Use the resolved repository and host in the API endpoint. For the canonical repository:

```bash
alerts_dir=$(mktemp -d)
gh api --method GET --paginate --slurp \
  -H 'Accept: application/vnd.github+json' \
  'repos/kernelci/dashboard/dependabot/alerts?state=open&per_page=100' \
  > "$alerts_dir/pages.json"
```

Check the exit status before processing. On failure, stop alert processing; partial pages are not a complete inventory. A 403/404 or authentication failure is not an empty result. Report the error and required access.

After a successful fetch, flatten and deduplicate by alert number while retaining distinct advisories and manifests:

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

Require successful JSON processing. Retain raw pages for advisory details. Summarize alert counts, packages, manifests, severities, and fixes. Only a successfully fetched empty inventory means no open alerts. A null patched version means no published fix is identified; investigate and report it.

## Apply and verify

Follow the routed reference to trace direct and transitive paths, choose compatible patches, resolve, install, and run project checks. Match every resolved copy against every applicable advisory range. Dependabot reflects the default branch and may lag behind safe local versions; verify those without upgrading again.

Review the full manifest and lockfile diff against the pre-change snapshot, including parent and incidental resolver changes. Investigate unrelated churn; restore only this attempt's changes and retry a narrower resolution when needed. Record previous and final resolved versions for all changed packages, not just those named by alerts.

Classify major updates using numeric semver components for npm and PEP 440 release components for Python, never lexical comparison. For each package and dependency path, compare old and new major components. With multiple versions, use graph paths to distinguish updates from added or removed copies. Report new major release lines introduced by the resolver; do not silently treat them as unrelated additions. If classification is uncertain, explain the uncertainty in the major-updates section rather than omitting the package.

GitHub alerts may remain open until the updated lockfiles reach the default branch and GitHub rescans them. Report locally verified remediation without claiming remote closure.

## Report results

Provide a compact table with alert number, advisory ID, package/manifest, previous and resolved versions, and outcome. Include managers used, files changed, checks and results, missing fixes/tools, compatibility blockers, ambiguous routing, and out-of-scope alerts. Explain any override and its compatibility tradeoff. Distinguish pre-existing failures, regressions, and blocked checks.

**Always include a dedicated `Major updates` section.** List every direct, transitive, parent, and incidental major update retained in the final changes, even if it has no alert of its own. For each, provide package, project/manifest, old and new resolved versions, why the update was needed, breaking changes or migration requirements, and compatibility checks with their results. Include resolver-introduced major lines and uncertain classifications. If there were none, explicitly write `No major updates.` Attempted updates that were reverted belong in the unresolved/blocker report, with the reason for reverting.

## Open a pull request when requested

This step applies only when the user requests a PR. Opening a remediation PR authorizes the necessary branch, commits, and push; it does not authorize merge, alert dismissal, unrelated GitHub comments, or history rewriting. For inspection or local-only requests, report results without publishing anything.

- Before applying fixes, create a dedicated branch from the requested base. Follow repository remote conventions; for KernelCI Dashboard, branch from `upstream/main`, not a fork's `origin/main`, unless instructed otherwise. Preserve existing local work and isolate the remediation in a separate worktree if needed. If fixes already exist locally, isolate only this task's changes without overwriting user changes.
- Complete the dependency verification and review the exact diff. Stage only remediation files, never unrelated user changes, credentials, local audit artifacts, or visual evidence. Follow repository commit conventions, including scope, `Signed-off-by`, and `Assisted-by`.
- Use [make-pr-easy-to-review](../make-pr-easy-to-review/SKILL.md) to prepare reviewer guidance and [unslop](../unslop/SKILL.md) for the description. Keep the final title and body aligned with the actual changes. Do not rewrite history or force-push without separate authorization.
- Put the remediation report described above in the PR body, including the alert/advisory table, files changed, reasons and override tradeoffs, verification commands and results, unresolved alerts, and blockers. Include the mandatory `Major updates` section even when there were none. Add clear, reproducible test instructions with prerequisites and expected results, and link relevant alerts, advisories, and supplied issues. Do not invent issue references.
- Follow repository requirements for frontend visual evidence. Exercise the affected flow and attach evidence to the PR using the supported `gh pr comment --attach` workflow; never commit evidence files. A request to open the PR authorizes these required evidence attachments. If the attachment capability or required verification tools are unavailable, report the blocker rather than installing tools or claiming evidence was attached.
- Push the task branch to the appropriate writable remote and open the PR against the resolved target repository and base. Open it as a **draft by default**, unless the user explicitly requests a ready-for-review PR. Use a structured body argument or an exact-text temporary file with `gh pr create --body-file` to preserve formatting. Do not create an empty PR if no remediation changes remain.
- Inspect the published PR's URL, title, body, base, head, draft state, and changed files. Check available CI results and report pending or failed checks accurately. Keep failed or blocked verification visible; do not mark the PR ready or request review until required checks pass. Return the PR link with the report and blockers. If publication fails, retain the local work and report the failed step without claiming a PR exists.
- In your PR body, add a quick note that the remediation was performed by an AI agent using the `fix-dependabot-alerts` skill and the PR must be reviewed carefully. Add the list of updated packages, their previous and resolved versions, and the reason for each update, include the link for the Dependabot advisory if available.

## References

- Adapted from [kexplo's Dependabot remediation workflow](https://github.com/kexplo/skills/blob/main/skills/fix-js-dependabot-alerts).
