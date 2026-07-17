#!/usr/bin/env bash
# Usage:
#   ./tree-report-get.sh
#   GIT_BRANCH=for-next TREE_NAME=mediatek GIT_URL=https://git.kernel.org/pub/scm/linux/kernel/git/mediatek/linux.git ./tree-report-get.sh
#   MIN_AGE_IN_HOURS=24 MAX_AGE_IN_HOURS=48 ./tree-report-get.sh
# Env: GIT_BRANCH, GIT_URL, ORIGIN, TREE_NAME (set TREE_NAME= empty to omit),
#      MIN_AGE_IN_HOURS (default 0), MAX_AGE_IN_HOURS (default 24)

GIT_BRANCH="${GIT_BRANCH:-master}"
GIT_URL="${GIT_URL:-https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git}"
ORIGIN="${ORIGIN:-maestro}"
TREE_NAME="${TREE_NAME-mainline}"
MIN_AGE_IN_HOURS="${MIN_AGE_IN_HOURS:-0}"
MAX_AGE_IN_HOURS="${MAX_AGE_IN_HOURS:-24}"

args=(
  "http://localhost:8000/api/tree-report/"
  "git_branch==${GIT_BRANCH}"
  "git_url==${GIT_URL}"
  "origin==${ORIGIN}"
  "min_age_in_hours==${MIN_AGE_IN_HOURS}"
  "max_age_in_hours==${MAX_AGE_IN_HOURS}"
)
if [[ -n "${TREE_NAME}" ]]; then
  args+=("tree_name==${TREE_NAME}")
fi

http "${args[@]}"
