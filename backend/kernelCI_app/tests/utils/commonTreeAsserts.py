from typing import Literal
from kernelCI_app.typeModels.databases import StatusValues
from kernelCI_app.tests.utils.asserts import (
    assert_has_fields_in_response_content,
    assert_build_filters,
    assert_boots_filters,
    assert_tests_filters,
)
from kernelCI_app.tests.utils.fields import tree

type SummaryFields = Literal["builds", "boots", "tests"]


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


def assert_tree_commit_history_fields(tree_data: dict) -> None:
    assert_has_fields_in_response_content(
        fields=tree.tree_commit_history, response_content=tree_data
    )
    assert_has_fields_in_response_content(
        fields=tree.tree_commit_history_tests, response_content=tree_data["tests"]
    )
    assert_has_fields_in_response_content(
        fields=tree.tree_commit_history_tests, response_content=tree_data["boots"]
    )
    assert_has_fields_in_response_content(
        fields=tree.tree_commit_history_builds, response_content=tree_data["builds"]
    )


def execute_builds_asserts(pytestconfig, content: dict, filters: dict) -> None:
    assert "builds" in content
    if "builds" in content and len(content["builds"]) > 0:
        first_build = content["builds"][0]

        assert_has_fields_in_response_content(
            fields=tree.tree_builds_expected_fields, response_content=first_build
        )

        assert_build_filters(filters=filters, build=first_build)

        if pytestconfig.getoption("--run-all") and len(content["builds"]) > 1:
            for build in content["builds"][1:]:
                assert_has_fields_in_response_content(
                    fields=tree.tree_builds_expected_fields, response_content=build
                )

                assert_build_filters(filters=filters, build=build)


def execute_boots_asserts(pytestconfig, content: dict, filters: dict) -> None:
    assert "boots" in content
    if "boots" in content and len(content["boots"]) > 0:
        first_boot = content["boots"][0]

        assert_has_fields_in_response_content(
            fields=tree.tree_tests_expected_fields, response_content=first_boot
        )

        assert_boots_filters(filters=filters, boot=first_boot)

        if pytestconfig.getoption("--run-all") and len(content["boots"]) > 1:
            for boot in content["boots"][1:]:
                assert_has_fields_in_response_content(
                    fields=tree.tree_tests_expected_fields, response_content=boot
                )

                assert_boots_filters(filters=filters, boot=boot)


def execute_tests_asserts(pytestconfig, content: dict, filters: dict) -> None:
    assert "tests" in content
    if "tests" in content and len(content["tests"]) > 0:
        first_test = content["tests"][0]

        assert_has_fields_in_response_content(
            fields=tree.tree_tests_expected_fields, response_content=first_test
        )

        assert_tests_filters(filters=filters, test=first_test)

        if pytestconfig.getoption("--run-all") and len(content["tests"]) > 1:
            for test in content["tests"][1:]:
                assert_has_fields_in_response_content(
                    fields=tree.tree_tests_expected_fields, response_content=test
                )

                assert_tests_filters(filters=filters, test=test)


def execute_summary_asserts(content: dict) -> None:
    assert "summary" in content
    assert "common" in content
    assert "filters" in content
    assert_has_fields_in_response_content(
        fields=tree.tree_summary, response_content=content
    )
    assert_has_fields_in_response_content(
        fields=tree.tree_summary_summary, response_content=content["summary"]
    )
    assert_has_fields_in_response_content(
        fields=tree.tree_summary_common, response_content=content["common"]
    )
    assert_has_fields_in_response_content(
        fields=tree.tree_summary_filters, response_content=content["filters"]
    )
    assert_has_fields_in_response_content(
        fields=tree.tree_test_summary, response_content=content["summary"]["tests"]
    )
    assert_has_fields_in_response_content(
        fields=tree.tree_test_summary, response_content=content["summary"]["boots"]
    )
    assert_has_fields_in_response_content(
        fields=tree.tree_build_summary,
        response_content=content["summary"]["builds"],
    )
