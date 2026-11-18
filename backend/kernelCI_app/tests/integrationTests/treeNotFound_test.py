"""Exercise missing tree resources against real PostgreSQL checkouts."""

from unittest.mock import patch

import click
import pytest
from django.core.cache import cache
from kcidev.libs.dashboard import dashboard_fetch_summary
from rest_framework.test import APIClient

import requests
from kernelCI_app.models import Builds, Checkouts
from kernelCI_app.queries.tree import get_tree_not_found

pytestmark = pytest.mark.django_db
HASH = "29c6cdaac04a6989a7ed4ae4275ce4244e617f58"
BASE = f"/api/tree/stable/linux-6.1.y/{HASH}"


@pytest.fixture(autouse=True)
def checkout():
    cache.clear()
    return Checkouts.objects.create(
        id="not-found-checkout",
        origin="maestro",
        tree_name="stable",
        git_repository_branch="linux-6.1.y",
        git_repository_url="https://example.org/linux.git",
        git_commit_hash=HASH,
        git_commit_tags=["v6.1"],
    )


@pytest.mark.parametrize("endpoint", ["summary", "full"])
@pytest.mark.parametrize(
    ("tree", "branch", "commit", "origin", "resource"),
    [
        ("unknown", "linux-6.1.y", HASH, "maestro", "tree"),
        ("stable", "linux-5.925.y", HASH, "maestro", "branch"),
        ("stable", "linux-6.1.y", "unknown", "maestro", "commit"),
        ("stable", "linux-6.1.y", HASH, "other-origin", "tree"),
    ],
)
def test_missing_resource_preserves_200_error_contract(
    endpoint, tree, branch, commit, origin, resource
):
    response = APIClient().get(
        f"/api/tree/{tree}/{branch}/{commit}/{endpoint}", {"origin": origin}
    )
    assert response.status_code == 200
    assert response.json()["resource"] == resource
    assert response.json()["error"] == f"{resource.capitalize()} not found."


@pytest.mark.parametrize("endpoint", ["summary", "full"])
def test_checkout_without_results_is_not_missing(endpoint):
    with patch("kernelCI_app.views.treeDetailsView.send_discord_notification"):
        response = APIClient().get(f"{BASE}/{endpoint}")
    assert response.status_code == 200
    assert "resource" not in response.json()


@pytest.mark.parametrize("commit", [HASH, "v6.1"])
def test_existing_commit_or_tag_needs_only_one_existence_query(
    commit, django_assert_num_queries
):
    with django_assert_num_queries(1):
        assert (
            get_tree_not_found(
                origin="maestro",
                tree_name="stable",
                git_branch="linux-6.1.y",
                commit_hash=commit,
            )
            is None
        )


def test_commit_on_another_branch_is_missing(checkout):
    Checkouts.objects.create(
        id="other-branch",
        origin="maestro",
        tree_name="stable",
        git_repository_branch="linux-6.2.y",
        git_commit_hash="other-hash",
    )
    response = APIClient().get(f"/api/tree/stable/linux-6.2.y/{HASH}/summary")
    assert response.status_code == 200
    assert response.json()["resource"] == "commit"


@pytest.mark.parametrize("endpoint", ["summary", "full"])
def test_query_parameter_cannot_override_branch_in_path(endpoint):
    response = APIClient().get(
        f"/api/tree/stable/linux-5.925.y/{HASH}/{endpoint}",
        {"git_branch": "linux-6.1.y"},
    )
    assert response.status_code == 200
    assert response.json()["resource"] == "branch"


@pytest.mark.parametrize(
    ("path", "params", "resource"),
    [
        ("unknown/linux-6.1.y", {}, "tree"),
        ("stable/linux-5.925.y", {}, "branch"),
        ("stable/linux-6.1.y", {"commit_hash": "missing"}, "commit"),
    ],
)
def test_latest_shortcuts_report_missing_component(path, params, resource):
    response = APIClient().get(f"/api/tree/{path}", params)
    assert response.status_code == 200
    assert response.json()["resource"] == resource


def test_valid_tag_shortcut():
    response = APIClient().get("/api/tree/stable/linux-6.1.y", {"commit_hash": "v6.1"})
    assert response.status_code == 200
    assert response.json()["git_commit_hash"] == HASH


def test_filters_matching_nothing_are_not_missing(checkout):
    Builds.objects.create(
        id="passing-build", checkout=checkout, origin="maestro", status="PASS"
    )
    with patch(
        "kernelCI_app.views.treeDetailsSummaryView.get_tree_not_found"
    ) as existence:
        response = APIClient().get(f"{BASE}/summary", {"filter_build.status": "FAIL"})
    assert response.status_code == 200
    assert "error" not in response.json()
    assert response.json()["summary"]["builds"]["status"]["PASS"] == 0
    existence.assert_not_called()


def test_legacy_hash_route_respects_repository_and_branch():
    response = APIClient().get(
        f"/api/tree/{HASH}/summary",
        {"git_url": "https://example.org/linux.git", "git_branch": "missing"},
    )
    assert response.status_code == 200
    assert response.json()["resource"] == "branch"


@pytest.mark.parametrize(
    ("git_url", "branch", "commit", "message"),
    [
        ("https://example.org/missing.git", "linux-6.1.y", HASH, "Tree not found."),
        ("https://example.org/linux.git", "missing", HASH, "Branch not found."),
        (
            "https://example.org/linux.git",
            "linux-6.1.y",
            "missing",
            "Commit not found.",
        ),
    ],
)
def test_kci_dev_preserves_missing_resource_message(git_url, branch, commit, message):
    def get(url, **kwargs):
        api_response = APIClient().get(url)
        response = requests.Response()
        response.status_code = api_response.status_code
        response._content = api_response.content
        response.url = url
        return response

    with patch("kcidev.libs.dashboard.kcidev_session.get", side_effect=get) as fetch:
        with pytest.raises(click.ClickException, match=message):
            dashboard_fetch_summary("maestro", git_url, branch, commit, None, False)
    fetch.assert_called_once()
