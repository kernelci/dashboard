from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from kernelCI_app.models import (
    Builds,
    Checkouts,
    CommitIdentity,
    CommitParents,
    Commits,
    Incidents,
    Issues,
)
from kernelCI_app.queries.issues import get_issue_next_checkout_data

TREE = {
    "origin": "test",
    "tree_name": "mainline",
    "git_repository_url": "https://example.com/linux.git",
    "git_repository_branch": "main",
}
START = datetime(2026, 1, 1, tzinfo=timezone.utc)


@pytest.fixture
def identity():
    return CommitIdentity.objects.create(name="Test", email="test@example.com")


def add_commit(identity, commit_hash, *parents):
    commit = Commits.objects.create(
        git_commit_hash=commit_hash,
        author_identity=identity,
        committer_identity=identity,
    )
    for order, parent in enumerate(parents):
        CommitParents.objects.create(commit=commit, parent=parent, ord=order)
    return commit


def add_checkout(checkout_id, commit_hash, minutes):
    return Checkouts.objects.create(
        id=checkout_id,
        git_commit_hash=commit_hash,
        start_time=START + timedelta(minutes=minutes),
        **TREE,
    )


def add_last_seen_issue(issue_id, commit_hash):
    issue = Issues.objects.create(id=issue_id, version=1, origin=TREE["origin"])
    checkout = add_checkout(f"{issue_id}-last", commit_hash, 0)
    build = Builds.objects.create(
        id=f"{issue_id}-build",
        checkout=checkout,
        origin=TREE["origin"],
    )
    Incidents.objects.create(
        id=f"{issue_id}-incident",
        issue=issue,
        issue_version=1,
        build=build,
        origin=TREE["origin"],
        field_timestamp=START,
    )


def next_checkout(issue_id):
    with (
        patch("kernelCI_app.queries.issues.get_query_cache", return_value=None),
        patch("kernelCI_app.queries.issues.set_query_cache"),
    ):
        rows = get_issue_next_checkout_data(issue_id_list=[issue_id])
    return rows[0]["checkout_id"]


@pytest.mark.django_db
def test_uses_first_parent_ancestry_instead_of_closest_start_time(identity):
    last = add_commit(identity, "last")
    middle = add_commit(identity, "middle", last)
    add_commit(identity, "next", middle)
    add_commit(identity, "unrelated")
    add_last_seen_issue("issue-linear", last.git_commit_hash)
    add_checkout("earlier-unrelated", "unrelated", 1)
    add_checkout("first-descendant", "next", 2)

    assert next_checkout("issue-linear") == "first-descendant"


@pytest.mark.django_db
def test_follows_only_first_parent_of_merge(identity):
    last = add_commit(identity, "last")
    other = add_commit(identity, "other")
    add_commit(identity, "merge-second-parent", other, last)
    add_commit(identity, "first-parent-descendant", last)
    add_last_seen_issue("issue-merge", last.git_commit_hash)
    add_checkout("merge-checkout", "merge-second-parent", 1)
    add_checkout("descendant-checkout", "first-parent-descendant", 2)

    assert next_checkout("issue-merge") == "descendant-checkout"


@pytest.mark.django_db
def test_disambiguates_children_with_later_checkouts(identity):
    last = add_commit(identity, "last")
    add_commit(identity, "child-a", last)
    add_commit(identity, "child-b", last)
    add_last_seen_issue("issue-children", last.git_commit_hash)
    add_checkout("later-child", "child-a", 2)
    add_checkout("earlier-child", "child-b", 1)

    assert next_checkout("issue-children") == "earlier-child"


@pytest.mark.django_db
def test_falls_back_to_start_time_when_last_commit_is_missing(identity):
    add_commit(identity, "known")
    add_last_seen_issue("issue-missing", "missing")
    add_checkout("fallback", "known", 1)
    add_checkout("later", "known", 2)

    assert next_checkout("issue-missing") == "fallback"
