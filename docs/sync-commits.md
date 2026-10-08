# Commit metadata sync

Two management commands fill `commits`, `commit_identity`, `commit_message`,
and `commit_parents` from git, not from KCIDB submissions. Author, committer,
subject, message, and ordered parents are properties of a git object. The same
hash can appear on many checkouts, so that data does not live on `checkouts`.

Parent epic: [#2079](https://github.com/kernelci/dashboard/issues/2079).
Schema: [#2089](https://github.com/kernelci/dashboard/issues/2089).
Parse / one-shot SHA fetch: [#2090](https://github.com/kernelci/dashboard/issues/2090).
This job: [#2109](https://github.com/kernelci/dashboard/issues/2109).

Entry points:

- Mirror: `backend/kernelCI_app/management/commands/sync_commit_mirror.py`
- Ingest: `backend/kernelCI_app/management/commands/sync_commit_ingest.py`
- Logic: `backend/kernelCI_app/helpers/commitSync.py`
- Parse / SHA fetch: `backend/kernelCI_app/helpers/gitCommit.py`

Postgres is the query store. Git is only an ingest cache. Request handlers
must not call git.

## Why a mirror, not checkout hashes

Filling only `DISTINCT checkouts.git_commit_hash` cannot walk first-parent
history when CI skipped a commit. The job therefore fetches the **ancestor
closure** of the branches we already see in checkouts, from an allowlist of
tree URLs (`tree-names.yaml`), into one persistent bare repo.

`--fill-gaps` is the fallback for hashes the mirror still does not cover. It
uses the one-shot SHA helper from #2090 (no parents).

The job never writes `checkouts.git_commit_message`.

## Tables

`commit_identity`: unique `(email, name)`. Missing name or email is stored as
`""`.

`commits`: surrogate `id`, unique `git_commit_hash`, `author_identity_id`,
`committer_identity_id`, author / committer dates, optional `fetched_from_url`.

`commit_message`: `commit_id` primary key, `subject`, `message` as UTF-8 bytes.

`commit_parents`: `commit_id`, `parent_id`, `ord` (`0` = first parent). No
stub rows. Inserts are topological so the parent row exists before the edge.

Join from `checkouts.git_commit_hash` for now. `commit_id` FKs on checkouts
are a later change.

## Storage

One **bare** repo at `GIT_MIRROR_DIR` (default `/var/lib/kernelci/git-mirror`).
Docker volume `git-mirror`, **not** `BACKEND_VOLUME_DIR`.

All allowlisted URLs are remotes of that one repo. Git shares objects across
remotes, so the first kernel tree is expensive and the rest mostly reuse it.

| Kind of fetch | Typical first pack |
|---|---|
| Server with `tree:0` (googlesource, gitlab, github) | hundreds of MB of commits |
| Server without filter (`git.kernel.org`) | ~3.5 GB (trees + blobs) |
| Later trees on the same object store | tens of MB of new objects |

Steady-state estimate for the current allowlist (~35 trees): **about 6–8 GiB**,
then daily deltas in the tens of MB. Cloning each tree into a throwaway repo
and deleting it would cost that 3.5 GB **per tree per run** (no object
sharing, no incremental fetch).

Throwaway clones for `--fill-gaps` go under `GIT_SCRATCH_DIR` (prefer tmpfs).

Tips seen at the end of a successful **ingest** are stored in `synced-tips` next
to the mirror. The next ingest does `rev-list --remotes` with each stored tip as a `^sha` on
stdin (git's `--not --stdin` does not exclude stdin lines).
Fetch-only does not touch that file.

When `sync_commit_mirror` finishes (including a failed run, and `--dry-run`),
it writes `GIT_MIRROR_DIR/mirror-size-bytes`: the apparent size of the mirror
in bytes. The write is a temp file in that directory, `fsync`, then replace.
With `PROMETHEUS_METRICS_ENABLED=true`, the metrics process exposes
`git_mirror_size_bytes` and `git_mirror_size_mtime_seconds` (Unix mtime of
that file). Prometheus alerts `GitMirrorSizeHigh` when the size stays above
10 GiB for 30 minutes. The series stay absent until the first completed fetch.

### Recreate the volume

A pack that slipped in unfiltered stays until the volume is wiped.

```bash
docker compose -f docker-compose.dev.yml stop backend
docker compose -f docker-compose.dev.yml rm -f backend
docker volume rm dashboard_git-mirror
docker compose -f docker-compose.dev.yml up -d backend
```

## Job flow

Three cron entries on the backend container:

- `0 4 * * *` `sync_commit_mirror` — remotes into the mirror. Does not write
  `commits` or `synced-tips`.
- `0 10 * * *` `sync_commit_ingest` — ingest new mirror objects (tip delta),
  then insert. Six hours later so a long first fetch is less likely to
  overlap; do not run both against the same `GIT_MIRROR_DIR` at once.
- `0 16 * * 0` `sync_commit_gc` — delete unreachable objects and repack.
  Sunday afternoon, so it does not hold the repo lock during either sync.

```
tree-names.yaml URLs
        |
        v
sync_commit_mirror
for each remote (sequential; git locks one repo)
        |
        +-- ls-remote: branch list + protocol v2 fetch= capabilities
        |
        +-- filter advertised?  git fetch --filter=tree:0 <checkout branches>
        |   otherwise           git fetch (no filter) <checkout branches>
        |                       or --skip-unfilterable → skip this remote
        |
        +-- GIT_MIRROR_SHALLOW_SINCE set, and this run is allowed to shorten
        |       → the same fetch also passes --shallow-since
        |
        +-- pack too big / incomplete / (filter promised but trees leaked)
        |       → drop new packs, restore refs and the shallow file;
        |         skip this remote this run
        |         (no HEAD retry: same server, same behaviour)
        v
sync_commit_ingest
rev-list new tips --not old tips  (topo, reverse)
tips the shallow file removed are dropped first
        |
        v
cat-file --batch in 2000-hash chunks → parse → insert commits then edges
        |
        v
write synced-tips
        |
        v
optional --fill-gaps (one-shot SHA fetch per missing checkout hash)
```

`sync_commit_mirror --dry-run` still fetches, so the mirror on disk changes.
It does not regenerate `tree-names.yaml` or write the database.

`sync_commit_ingest --dry-run` parses objects already in the mirror and writes
nothing to the database or `synced-tips`. It does not fetch. `--fill-gaps`
still fetches missing checkout SHAs and then discards them.

If `tree-names.yaml` is missing, a non-dry run regenerates it the same way
the ingester does (`treeproof`). Empty allowlist used to make the job a
silent no-op.

## Shallow window

`GIT_MIRROR_SHALLOW_SINCE` is empty by default, so fetches stay full-history.
Set it only after `sync_commit_ingest` has stored the history you want to keep.
On an empty mirror the first fetch would otherwise never download that history.

Git stores the boundary commits in `GIT_MIRROR_DIR/shallow`. It does not store
the date, so every later fetch that is allowed to shorten passes
`--shallow-since` again. That covers a new remote and moves the window forward.

A run passes the flag in two cases:

- The mirror has no `refs/remotes` yet.
- `synced-tips` exists and, before this fetch, nothing reachable is still
  pending ingest.

Otherwise the fetch is unchanged. A populated mirror that has never been
ingested, and a mirror whose last ingest failed, keep their current history.
A failed or rejected fetch restores the previous `shallow` file.

After the boundary moves, ingest ignores stored tips that `git cat-file -e`
can no longer see. The commits that remain reachable are parsed again.
Existing rows are left alone.

`sync_commit_gc` runs `git gc --prune=now` with `repack.writeBitmaps=false`.
Git's own repack progress is written straight to the terminal. Objects
behind the shallow boundary are removed in that run, and `mirror-size-bytes`
is rewritten afterwards. A bare repo writes a bitmap by
default, and a bitmap requires every reachable object. `--filter=tree:0`
omits trees and blobs, so the bitmap step aborts after the new pack is
written and the mirror grows. The mirror config sets the same option. It
does not pass `--aggressive` or `gc.repackFilter`. Promisor packs stay
promisor packs, so the omitted trees are not downloaded.

## What is fetched

Not `git fetch <remote>` (every topic branch since 2015).

For each URL, the job intersects `checkouts.git_repository_branch` with
`ls-remote --heads`. If nothing matches, it fetches `HEAD` only.

That is enough for first-parent walks between checkouts. Untested topic
branches stay out of the mirror on purpose.

## Filter vs full clone

`--filter=tree:0` is a **server** feature. The client cannot force it.

Protocol v2 capability line from a real probe:

- `android.googlesource.com`: `fetch=filter ref-in-want ...` → treeless works
- `git.kernel.org`: `fetch=shallow wait-for-done` → **no filter**; a
  `--filter=tree:0` fetch is silently a full clone

There is no porcelain for that advertisement. The job points
`GIT_TRACE_PACKET` at a temp file during `ls-remote` and looks for `filter`
on the `fetch=` line.

Default: still fetch unfilterable remotes. Object sharing makes the second
kernel.org tree cheap. `--skip-unfilterable` opts out (smaller disk, those
trees only covered by `--fill-gaps`).

We do **not** rewrite `git.kernel.org` URLs to `kernel.googlesource.com`.
The googlesource host is a valid mirror, but mapping URLs would split
identity from the treeproof allowlist and from `checkouts.git_repository_url`.

## Pack rejection

After each fetch, only **new** pack files are inspected.

Always reject:

- leftover `tmp_pack_*`
- pack larger than `MAX_REMOTE_PACK_BYTES` (6 GiB; runaway backstop)

If the server advertised filter, also reject packs that contain `tree` or
`blob` (broken promise). If it did not, trees/blobs are expected.

On reject: restore `refs/remotes/<name>/*` to the pre-fetch snapshot and
delete the new pack files. That remote is skipped **this run** only.

Do not retry `HEAD` after a rejected pack. The second download is the same
full clone.

## Parse and insert

`git cat-file --batch` over stdin, 2000 hashes at a time. Per-commit
`rev-parse` + `cat-file` is hundreds of times slower.

Each chunk is inserted before the next is parsed so a full-history import
does not hold every commit message in RAM. Order stays topological:
`rev-list --reverse --topo-order`, then chunks in that order.

`bulk_create(..., ignore_conflicts=True)`. A git object is immutable, so a
hash that is already stored is left alone rather than updated. Missing parent
rows skip the edge (logged); no stubs.

## Parallel fetch

Not implemented. `git fetch` takes a lock on a single repo, so threads
against `GIT_MIRROR_DIR` serialize or fail.

The useful pattern would be N throwaway bares in parallel, then a serial
`git fetch` into the persistent mirror. That is extra disk and extra
pressure on git.kernel.org. Measure incremental runs first: after the first
populate, most remotes send almost nothing.

## Commands

```bash
poetry run python manage.py sync_commit_mirror
poetry run python manage.py sync_commit_mirror --dry-run --verbose-git
poetry run python manage.py sync_commit_mirror --skip-unfilterable
poetry run python manage.py sync_commit_mirror --mirror-dir /path --fetch-timeout 1800

poetry run python manage.py sync_commit_ingest
poetry run python manage.py sync_commit_ingest --dry-run
poetry run python manage.py sync_commit_ingest --fill-gaps
poetry run python manage.py sync_commit_ingest --mirror-dir /path

poetry run python manage.py sync_commit_gc
poetry run python manage.py sync_commit_gc --mirror-dir /path
```

`sync_commit_mirror`:

| Flag | Effect |
|---|---|
| `--dry-run` | Still fetches into the mirror. Does not regenerate `tree-names.yaml` |
| `--skip-unfilterable` | Do not fetch servers without `fetch=filter` |
| `--verbose-git` | Git's own fetch progress on stdout (noisy in cron) |
| `--mirror-dir` | Override `GIT_MIRROR_DIR` |
| `--fetch-timeout` | Per-remote fetch timeout (default 1800s) |

`sync_commit_ingest`:

| Flag | Effect |
|---|---|
| `--dry-run` | No fetch, no DB writes, no `synced-tips`. `--fill-gaps` still fetches |
| `--fill-gaps` | One-shot SHA fetch for checkout hashes still missing |
| `--mirror-dir` | Override `GIT_MIRROR_DIR` |

`sync_commit_gc` takes `--mirror-dir`. It does nothing when the mirror does not exist.

Env:

- `GIT_MIRROR_DIR` — persistent bare repo
- `GIT_MIRROR_SHALLOW_SINCE` — optional cutoff (`90 days ago`). Empty keeps full history
- `GIT_SCRATCH_DIR` — ephemeral clones for `--fill-gaps`
- `BACKEND_VOLUME_DIR` — `tree-names.yaml` only

## Out of scope (follow-ups)

- `trees` / `named_refs` tables
- Rewriting readers of `checkouts.git_commit_message` / dropping that column
- First-parent “next checkout” queries ([#2092](https://github.com/kernelci/dashboard/issues/2092))
- Fetching git from request handlers
