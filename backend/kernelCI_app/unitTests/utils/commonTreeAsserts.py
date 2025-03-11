from typing import Literal
from kernelCI_app.typeModels.databases import StatusValues
from kernelCI_app.unitTests.utils.asserts import assert_has_fields_in_response_content
from kernelCI_app.unitTests.utils.fields.tree import (
    tree_commit_history,
    tree_commit_history_builds,
    tree_commit_history_tests,
)

type SummaryFields = Literal["builds", "boots", "tests"]

FILTER_TO_VALID = {
    "true": "valid",
    "false": "invalid",
    "none": "null",
}


def assert_summary_issues(
    content: dict, task: SummaryFields, value: StatusValues
) -> None:
    task_summary = content["summary"][task]
    assert "issues" in task_summary
    assert "unknown_issues" in task_summary

    known_issues = len(task_summary["issues"])
    failed_tests = task_summary["status"].get(
        "FAIL", task_summary["status"].get("invalid")
    )

    if value in {"PASS", "valid"}:
        assert known_issues == 0
    elif value in {"FAIL", "invalid"}:
        if known_issues == 0 and failed_tests > 0:
            assert content["summary"][task]["unknown_issues"] == failed_tests
        else:
            assert content["summary"][task]["unknown_issues"] <= failed_tests


def assert_common_summary_status_fields(
    content: dict, task: SummaryFields, value: StatusValues
) -> None:
    assert "summary" in content
    assert task in content["summary"]
    task_summary = content["summary"][task]

    assert "status" in task_summary
    for status, count in task_summary["status"].items():
        if status != value:
            assert count == 0

    assert "configs" in task_summary
    for config in task_summary["configs"].values():
        for status, count in config.items():
            if status != value:
                assert count == 0

    assert_summary_issues(content, task, value)


def assert_tree_commit_history_fields(tree: dict) -> None:
    assert_has_fields_in_response_content(
        fields=tree_commit_history, response_content=tree
    )
    assert_has_fields_in_response_content(
        fields=tree_commit_history_tests, response_content=tree["tests"]
    )
    assert_has_fields_in_response_content(
        fields=tree_commit_history_tests, response_content=tree["boots"]
    )
    assert_has_fields_in_response_content(
        fields=tree_commit_history_builds, response_content=tree["builds"]
    )
