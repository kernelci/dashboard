# Tree Compare

High-level overview of the Tree Compare feature: side-by-side comparison of builds, boots, and tests between two revisions of the same tree/branch.

## Purpose

Given a tree name and branch, pick two commit hashes (side A and side B) and answer:

- How did overall pass/fail/inconclusive counts move from A → B?
- Which individual builds / boots / tests changed category (regressions, fixes, new failures, etc.)?

Entry point: **Compare revisions** on Tree Details (`TreeCompareLink`), which opens:

`/tree/{treeName}/{branch}/compare?hashA=…&hashB=…&origin=…`

## User flow

1. Open compare from Tree Details (current revision pre-fills as side A).
2. Choose / swap revisions via the revision selector (commit history + shortcuts: previous commit, branch head, swap sides).
3. Read the summary matrix (fixes, regressions, pass/fail/other counts per builds / boots / tests).
4. Drill into **Changed results** tabs (Builds / Boots / Tests). Quick change-type chips add or remove their status pairs; custom From/To pairs can be added too (default: `PASS → FAIL` and `FAIL → PASS`). Last edited pairs are remembered in localStorage when the URL omits `statusPair`.

URL search state owns: `hashA`, `hashB`, `origin`, `currentPageTab`, and optional `statusPair`.

## Change categories (A → B)

Statuses are grouped into **PASS**, **FAIL**, and **INCONCLUSIVE** (everything else, including null). Absent on one side is treated as missing (`null` / `—`).

| Change | Meaning (simplified) |
| ------ | -------------------- |
| `regression` | PASS → FAIL or INCONCLUSIVE |
| `fixed` | FAIL → PASS or INCONCLUSIVE |
| `newFailure` | missing/INCONCLUSIVE → FAIL |
| `stillFailing` | FAIL → FAIL |
| `newPass` | missing/INCONCLUSIVE → PASS |
| `appeared` | missing → INCONCLUSIVE |
| `disappeared` | present on A, missing on B |

Backend SQL aggregates (`_CHANGE_COUNT_SELECT` in `queries/tree.py`) and the frontend `deriveCompareChange` helper must stay in sync.

## Architecture

```
Tree Details ──► /tree/.../compare (UI)
                      │
                      ├─ GET .../compare          → summary + change counts
                      ├─ GET .../compare/builds   → paired build rows
                      ├─ GET .../compare/boots    → paired boot rows
                      └─ GET .../compare/tests    → paired test rows
```

### Backend

| Piece | Role |
| ----- | ---- |
| `TreeCompareView` | Summary: per-side status counts + change counts for builds/boots/tests |
| `TreeCompareBuildsView` | Diff rows keyed by config / arch / compiler |
| `TreeDetailsBootsCompare` / `TreeDetailsTestsCompare` | Diff rows keyed by path / config / arch / platform |
| `helpers/treeCompare.py` | Accumulators, response shaping, compare filter SQL helpers |
| `queries/tree.py` | Pairing queries + change-count aggregates |
| `typeModels/treeCompare.py` | Request/response models |

Routes live under `tree/<tree_name>/<git_branch>/compare…` and are registered **before** the `…/<commit_hash>/…` routes so `compare` is not captured as a commit hash.

Identity filters (config, arch, compiler, hardware, …) apply **before** the A/B join. Status filters apply **after** pairing so a PASS→FAIL transition is not rewritten as a “new failure”. Duration/issue filters are not wired on compare yet.

### Frontend

| Piece | Role |
| ----- | ---- |
| `pages/TreeCompare/TreeComparePage.tsx` | Page shell: revisions, summary, tabs |
| `api/treeCompare.ts` | React Query hooks for the four endpoints |
| `utils/treeCompareDiff.ts` | Map API rows → UI rows; derive/filter change types |
| `types/tree/TreeCompare.ts` | Types + URL search schema |
| Breakdown tables / summary / revision selector | Under `pages/TreeCompare/components/` |

The UI maps API `status_a` / `status_b` into change types client-side for the tables; the summary change counts come from the backend.

## Pairing model

Compare joins the same logical item across the two commits:

- **Builds**: config + architecture + compiler
- **Boots / tests**: path + config + architecture + platform

Only rows that differ in grouped status (or exist on only one side) show up in the breakdown endpoints; the summary endpoint also reports absolute pass/fail/inconclusive totals per side and deltas.

## Tests

- Backend unit tests: helpers, queries, and views under `backend/kernelCI_app/tests/unitTests/…treeCompare…`
- Frontend unit tests: `dashboard/src/utils/treeCompareDiff.test.ts`
- Playwright: `dashboard/e2e/tree-compare.spec.ts` (page load with mocked APIs)
