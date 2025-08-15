import pytest
from kernelCI_app.helpers.issueListing import (
    should_discard_issue_by_category,
    should_discard_issue_by_culprit,
    should_discard_issue_by_origin,
)
from kernelCI_app.typeModels.issues import CULPRIT_CODE


@pytest.mark.unit
class TestShouldDiscardIssue:
    def test_discard_by_culprit(self):
        assert (
            should_discard_issue_by_culprit(
                culprit_filters=set([CULPRIT_CODE]),
                record={
                    "culprit_code": True,
                    "culprit_harness": False,
                    "culprit_tool": False,
                },
            )
            is False
        )

        assert (
            should_discard_issue_by_culprit(
                culprit_filters=set([CULPRIT_CODE]),
                record={
                    "culprit_code": False,
                    "culprit_harness": True,
                    "culprit_tool": False,
                },
            )
            is True
        )

        assert (
            should_discard_issue_by_culprit(
                culprit_filters=set(),
                record={
                    "culprit_code": False,
                    "culprit_harness": False,
                    "culprit_tool": True,
                },
            )
            is False
        )

    def test_discard_by_origin(self):
        assert (
            should_discard_issue_by_origin(
                origin_filters=set(["maestro"]),
                issue_origin="maestro",
            )
            is False
        )

        assert (
            should_discard_issue_by_origin(
                origin_filters=set(["maestro"]),
                issue_origin="redhat",
            )
            is True
        )

        assert (
            should_discard_issue_by_origin(
                origin_filters=set(),
                issue_origin="maestro",
            )
            is False
        )

    def test_discard_by_categories(self):
        categories: list[str] = ["from_build", "new_build", "important"]

        assert (
            should_discard_issue_by_category(
                categories_filters=set(["from_build"]), issue_categories=categories
            )
            is False
        )

        assert (
            should_discard_issue_by_category(
                categories_filters=set(["error", "test"]),
                issue_categories=categories,
            )
            is True
        )

        assert (
            should_discard_issue_by_category(
                categories_filters=set(), issue_categories=categories
            )
            is False
        )
