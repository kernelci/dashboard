# pnpm remediation

Check `pnpm --version` without triggering a tool download. Use the version pinned in `packageManager`, when present. Inspect `pnpm-workspace.yaml`, catalogs, overrides, and all importers; identify each independent pnpm root. Follow the shared guardrails and reporting requirements in [SKILL.md](../SKILL.md).

## Trace affected dependencies

Use `pnpm why <package>` and `pnpm list <package> --depth Infinity` at the affected project root. For workspaces, use `pnpm -r why <package>` or `pnpm --filter <workspace-package> why <package>`. Inspect the lockfile when multiple versions or importers are involved.

Match installed versions against every advisory's vulnerable range. Alerts describe the default branch and may lag behind a local fix; an already safe local version needs verification, not another upgrade. Keep separate alert records even when one update fixes several alerts.

## Apply targeted fixes

Choose the smallest compatible change that escapes all applicable vulnerable ranges. The first patched version is a starting point: different major release lines can have separate fixes. Check advisory and release details instead of comparing version strings lexicographically or blindly taking the largest reported minimum.

### Direct dependencies

Use a targeted update at the appropriate root:

```bash
pnpm update <package>@<patched-version>
pnpm --filter <workspace-package> update <package>@<patched-version>
```

Use the workspace form only when needed. Preserve dependency sections, range style, and catalog conventions; update shared catalog declarations when they own the version. Avoid broad `--latest` upgrades or unrelated changes. If a fix requires a major upgrade, assess breaking changes and compatibility, apply the supported fix, and include it in the dedicated major-updates report.

### Transitive dependencies

Prefer a compatible parent dependency update or a targeted lockfile refresh that resolves a patched child within the parent's supported range. If that cannot fix the alert, use a narrowly scoped override and verify parent compatibility.

Use the override location supported by the pinned pnpm version and established by the repository. Current pnpm uses root `pnpm-workspace.yaml`:

```yaml
overrides:
  'parent-package@<affected-parent-range>><vulnerable-package>': '<patched-version>'
```

Older projects may use root `package.json` under `pnpm.overrides`. Preserve unrelated overrides and avoid competing definitions in both files. Check the pinned version's documentation if its supported location is unclear. Use a global package override only when appropriate for every affected dependency path. An override that crosses a major-version boundary requires evidence that each affected parent remains compatible; prefer a compatible parent update when available and report the major update. Report unresolved cases with reasons and next steps.

## Install and verify

- Run `pnpm install` at each affected project or workspace root to update its lockfile. If frozen-lockfile mode blocks an intentional manifest change, use `pnpm install --no-frozen-lockfile` for that update.
- Reinspect every affected dependency path and verify all resolved versions against the advisory ranges. Checking only the manifest or one installed copy is insufficient.
- Run the affected project's existing build, typecheck, and relevant tests as available. Use workspace filters where suitable; distinguish pre-existing failures from upgrade regressions.
- Use `pnpm audit --json` as a supplementary check when registry access is available. Findings may differ from GitHub's. Report failed or unavailable checks explicitly.
- Review the diff for expected manifest, workspace configuration, and lockfile changes. Investigate unrelated churn without discarding user changes.

## References

- [pnpm update](https://pnpm.io/cli/update) and [pnpm settings](https://pnpm.io/settings).
