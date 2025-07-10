import pytest
from requests import Response
from http import HTTPStatus

from kernelCI_app.utils import string_to_json
from kernelCI_app.tests.utils.client.treeClient import TreeClient
from kernelCI_app.tests.utils.commonTreeAsserts import (
    assert_common_summary_status_fields,
)
from kernelCI_app.tests.utils.fields import tree
from kernelCI_app.tests.utils.asserts import (
    assert_has_fields_in_response_content,
    assert_status_code,
    assert_error_response,
)
from kernelCI_app.typeModels.treeDetails import TreeQueryParameters
from kernelCI_app.constants.general import UNCATEGORIZED_STRING


INVALID_TREE = {
    "id": "invalid_id",
    "query": TreeQueryParameters(origin="", git_url="", git_branch=""),
}

# https://dashboard.kernelci.org/tree/a1c24ab822793eb513351686f631bd18952b7870?p=bt&tf%7Cb=a&tf%7Cbt=f&tf%7Ct=i&ti%7Cc=v6.14-rc3-18-ga1c24ab822793&ti%7Cch=a1c24ab822793eb513351686f631bd18952b7870&ti%7Cgb=for-kernelci&ti%7Cgu=https%3A%2F%2Fgit.kernel.org%2Fpub%2Fscm%2Flinux%2Fkernel%2Fgit%2Farm64%2Flinux.git&ti%7Ct=arm64
ARM64_TREE = {
    "id": "a1c24ab822793eb513351686f631bd18952b7870",
    "query": TreeQueryParameters(
        origin="maestro",
        git_url="https://git.kernel.org/pub/scm/linux/kernel/git/arm64/linux.git",
        git_branch="for-kernelci",
    ),
}

# https://dashboard.kernelci.org/tree/ef143cc9d68aecf16ec4942e399e7699266b288f?ti%7Cc=ASB-2025-02-05_mainline-7916-gef143cc9d68ae&ti%7Cch=ef143cc9d68aecf16ec4942e399e7699266b288f&ti%7Cgb=android-mainline&ti%7Cgu=https%3A%2F%2Fandroid.googlesource.com%2Fkernel%2Fcommon&ti%7Ct=android
ANDROID_MAINLINE_TREE = {
    "id": "ef143cc9d68aecf16ec4942e399e7699266b288f",
    "query": TreeQueryParameters(
        origin="maestro",
        git_url="https://android.googlesource.com/kernel/common",
        git_branch="android-mainline",
    ),
}

client = TreeClient()


def pytest_generate_tests(metafunc):
    test_status_cases = [
        (ARM64_TREE, {"boot.status": "FAIL"}),
        (ARM64_TREE, {"test.status": "PASS"}),
    ]

    hardware_cases = [
        (ARM64_TREE, {"test.hardware": "arm,juno"}),
    ]

    issues_cases = [
        (
            ARM64_TREE,
            {"boot.issue": "maestro:e602fca280d85d8e603f7c0aff68363bb0cd7993,1"},
        ),
    ]

    invalid_filter_cases = [
        ("boot.status", "boots"),
        ("compiler", None),
        ("test.hardware", None),
        ("build.issue", "builds"),
    ]

    if "test_status_input" in metafunc.fixturenames:
        base_cases = test_status_cases
        extra_cases = []
        if metafunc.config.getoption("--run-all"):
            extra_cases = [
                (ARM64_TREE, {"boot.status": "ERROR"}),
                (ARM64_TREE, {"boot.status": "MISS"}),
                (ARM64_TREE, {"boot.status": "DONE"}),
                (ARM64_TREE, {"boot.status": "NULL"}),
                (ARM64_TREE, {"test.status": "ERROR"}),
                (ARM64_TREE, {"test.status": "MISS"}),
                (ARM64_TREE, {"test.status": "DONE"}),
                (ARM64_TREE, {"test.status": "NULL"}),
                (ARM64_TREE, {"boot.status": "PASS"}),
                (ARM64_TREE, {"boot.status": "SKIP"}),
                (ARM64_TREE, {"test.status": "SKIP"}),
                (ARM64_TREE, {"test.status": "FAIL"}),
            ]
        metafunc.parametrize("test_status_input", base_cases + extra_cases)

    if "hardware_input" in metafunc.fixturenames:
        base_cases = hardware_cases
        extra_cases = []
        if metafunc.config.getoption("--run-all"):
            extra_cases = [
                (ARM64_TREE, {"test.hardware": "acer-chromebox-cxi4-puff"}),
            ]
        metafunc.parametrize("hardware_input", base_cases + extra_cases)

    if "issues_input" in metafunc.fixturenames:
        base_cases = issues_cases
        extra_cases = []
        if metafunc.config.getoption("--run-all"):
            extra_cases = [
                (
                    ARM64_TREE,
                    {"test.issue": f"{UNCATEGORIZED_STRING},null"},
                ),
                (
                    ANDROID_MAINLINE_TREE,
                    {
                        "build.issue": "maestro:2ff8fe94f6d53f39321d4a37fe15801cedc93573,1"
                    },
                ),
            ]
        metafunc.parametrize("issues_input", base_cases + extra_cases)

    if "invalid_filters_input" in metafunc.fixturenames:
        base_cases = invalid_filter_cases
        extra_cases = []
        if metafunc.config.getoption("--run-all"):
            extra_cases = [
                ("test.status", "tests"),
                ("build.status", "builds"),
                ("config_name", None),
                ("architecture", None),
                ("boot.issue", "boots"),
                ("test.issue", "tests"),
            ]
        metafunc.parametrize("invalid_filters_input", base_cases + extra_cases)


def request_data(base_tree: dict, filters: dict | None = None) -> tuple[Response, dict]:
    tree_id = base_tree["id"]
    query = base_tree["query"]
    response = client.get_tree_details_summary(
        tree_id=tree_id, query=query, filters=filters
    )
    content = string_to_json(response.content.decode())
    return response, content


@pytest.mark.parametrize(
    "base_tree, status_code, has_error_body",
    [
        (INVALID_TREE, HTTPStatus.OK, True),
        (ARM64_TREE, HTTPStatus.OK, False),
    ],
)
def test_no_filters(base_tree, status_code, has_error_body):
    response, content = request_data(base_tree)
    assert_status_code(response=response, status_code=status_code)
    if has_error_body:
        assert_error_response(response_content=content)
    else:
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


def test_filter_test_status(test_status_input):
    """
    Tests for the status filter for both boots and tests
    (couldn't add build to the same test function because it has a different nomenclature).
    This test only for when 1 status is being passed to the filter
    """
    base_tree, filters = test_status_input
    response, content = request_data(base_tree, filters)
    assert_status_code(response=response, status_code=HTTPStatus.OK)
    assert "error" not in content

    # filter task = 'boot' | 'test' and response task = 'boots' | 'tests'
    task, value = list(filters.items())[0]
    task = task.split(".")[0] + "s"

    assert_common_summary_status_fields(content, task, value)
    task_summary = content["summary"][task]

    assert "environment_compatible" in task_summary
    for compatible in task_summary["environment_compatible"].values():
        for status, count in compatible.items():
            if status != value:
                assert count == 0

    assert "environment_misc" in task_summary
    for platform in task_summary["environment_misc"].values():
        for status, count in platform.items():
            if status != value:
                assert count == 0

    assert "architectures" in task_summary
    for arch in task_summary["architectures"]:
        for status, count in arch["status"].items():
            if status != value:
                assert count == 0


@pytest.mark.parametrize(
    "base_tree, filters",
    [
        (ANDROID_MAINLINE_TREE, {"build.status": "PASS"}),
        (ANDROID_MAINLINE_TREE, {"build.status": "FAIL"}),
        (ANDROID_MAINLINE_TREE, {"build.status": "NONE"}),
    ],
)
def test_filter_build_status(base_tree, filters):
    """
    Tests for the status filter for builds
    This test only for when 1 status is being passed to the filter
    """
    response, content = request_data(base_tree, filters)
    assert_status_code(response=response, status_code=HTTPStatus.OK)
    assert "error" not in content

    value = list(filters.values())[0]

    assert_common_summary_status_fields(content, "builds", value)
    task_summary = content["summary"]["builds"]

    assert "architectures" in task_summary
    for arch in task_summary["architectures"].values():
        for status, count in arch.items():
            if status == "compilers":
                continue
            if status != value:
                assert count == 0


@pytest.mark.parametrize(
    "base_tree, filters",
    [
        (ARM64_TREE, {"config_name": "defconfig"}),
    ],
)
def test_filter_config_name(base_tree, filters):
    response, content = request_data(base_tree, filters)
    assert_status_code(response=response, status_code=HTTPStatus.OK)
    assert "error" not in content

    values = list(filters.values())

    assert "summary" in content
    for task in ["builds", "boots", "tests"]:
        assert task in content["summary"]
        task_summary = content["summary"][task]
        assert "configs" in task_summary

        for config in task_summary["configs"].keys():
            assert config in values


@pytest.mark.parametrize(
    "base_tree, filters",
    [
        (ARM64_TREE, {"architecture": "i386"}),
    ],
)
def test_filter_architectures(base_tree, filters):
    response, content = request_data(base_tree, filters)
    assert_status_code(response=response, status_code=HTTPStatus.OK)
    assert "error" not in content

    values = list(filters.values())

    assert "summary" in content
    for task in ["boots", "tests"]:
        assert task in content["summary"]
        task_summary = content["summary"][task]
        assert "architectures" in task_summary

        for arch in task_summary["architectures"]:
            assert arch["arch"] in values

    assert content["summary"]["builds"]
    task_summary = content["summary"]["builds"]
    assert "architectures" in task_summary

    for arch in task_summary["architectures"]:
        assert arch in values


@pytest.mark.parametrize(
    "base_tree, filters",
    [
        (ARM64_TREE, {"compiler": "gcc-12"}),
    ],
)
def test_filter_compiler(base_tree, filters):
    response, content = request_data(base_tree, filters)
    assert_status_code(response=response, status_code=HTTPStatus.OK)
    assert "error" not in content

    values = list(filters.values())

    assert "summary" in content
    for task in ["boots", "tests"]:
        assert task in content["summary"]
        task_summary = content["summary"][task]
        assert "architectures" in task_summary

        for arch in task_summary["architectures"]:
            assert arch["compiler"] in values

    assert "builds" in content["summary"]
    task_summary = content["summary"]["builds"]
    assert "architectures" in task_summary

    for arch in task_summary["architectures"].values():
        for compiler in arch["compilers"]:
            assert compiler in values


def test_filter_hardware(hardware_input):
    base_tree, filters = hardware_input
    response, content = request_data(base_tree, filters)
    assert_status_code(response=response, status_code=HTTPStatus.OK)
    assert "error" not in content

    values = list(filters.values())

    assert "summary" in content
    for task in ["boots", "tests"]:
        assert task in content["summary"]
        task_summary = content["summary"][task]

        assert "environment_compatible" in task_summary
        assert "environment_misc" in task_summary

        for compatible in task_summary["environment_compatible"]:
            assert compatible in values

        for platform in task_summary["environment_misc"]:
            assert platform in values


def test_filter_issues(issues_input):
    base_tree, filters = issues_input
    response, content = request_data(base_tree, filters)
    assert_status_code(response=response, status_code=HTTPStatus.OK)
    assert "error" not in content

    # filter task = 'boot' | 'test' and response task = 'boots' | 'tests'
    task, value = list(filters.items())[0]
    task = task.split(".")[0] + "s"
    id, version = value.split(",")

    assert "summary" in content
    assert task in content["summary"]
    task_summary = content["summary"][task]
    assert "issues" in task_summary

    if id == UNCATEGORIZED_STRING:
        assert not task_summary["issues"]
        assert "unknown_issues" in task_summary
        assert task_summary["unknown_issues"] > 0
    else:
        for issue in task_summary["issues"]:
            assert issue["id"] == id
            assert issue["version"] == int(version)

    assert "status" in task_summary
    pass_count = task_summary["status"].get("PASS")
    assert pass_count == 0


def test_invalid_filters(invalid_filters_input):
    empty_test = {
        "architectures": [],
        "origins": {},
        "configs": {},
        "environment_compatible": {},
        "environment_misc": {},
        "fail_reasons": {},
        "failed_platforms": [],
        "issues": [],
        "platforms": None,
        "status": {
            "ERROR": 0,
            "FAIL": 0,
            "MISS": 0,
            "NULL": 0,
            "PASS": 0,
            "SKIP": 0,
            "DONE": 0,
        },
        "unknown_issues": 0,
    }

    empty_build = {
        "architectures": {},
        "origins": {},
        "configs": {},
        "issues": [],
        "status": {
            "PASS": 0,
            "FAIL": 0,
            "NULL": 0,
            "ERROR": 0,
            "MISS": 0,
            "SKIP": 0,
            "DONE": 0,
        },
        "unknown_issues": 0,
    }

    empty_summary = {
        "builds": empty_build,
        "boots": empty_test,
        "tests": empty_test,
    }

    filter, local_field = invalid_filters_input
    response, content = request_data(ARM64_TREE, {filter: "invalid_filter,null"})
    assert_status_code(response=response, status_code=HTTPStatus.OK)
    assert "error" not in content
    assert "summary" in content
    if local_field is None:
        assert content["summary"] == empty_summary
    else:
        assert content["summary"][local_field] == empty_summary[local_field]
