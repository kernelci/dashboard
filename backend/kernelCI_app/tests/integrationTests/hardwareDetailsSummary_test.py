import pytest
from requests import Response
from http import HTTPStatus

from kernelCI_app.utils import string_to_json
from kernelCI_app.tests.utils.client.hardwareClient import HardwareClient
from kernelCI_app.tests.utils.commonTreeAsserts import (
    assert_common_summary_status_fields,
)
from kernelCI_app.tests.utils.fields import hardware
from kernelCI_app.tests.utils.asserts import (
    assert_has_fields_in_response_content,
    assert_status_code,
    assert_error_response,
)
from kernelCI_app.typeModels.hardwareDetails import HardwareDetailsPostBody
from kernelCI_app.constants.general import UNCATEGORIZED_STRING


INVALID_BODY_HARDWARE = {
    "id": "invalid_id",
    "body": HardwareDetailsPostBody(
        origin="",
        startTimestampInSeconds="",
        endTimestampInSeconds="",
        selectedCommits={},
        filter={},
    ),
}

INVALID_ID_HARDWARE = {
    "id": "invalid_id",
    "body": HardwareDetailsPostBody(
        origin="maestro",
        startTimestampInSeconds=1741356000,
        endTimestampInSeconds=1741788000,
        selectedCommits={},
        filter={},
    ),
}

# https://dashboard.kernelci.org/hardware/asus-CM1400CXA-dalboz?et=1741788000&st=1741356000
ASUS_HARDWARE = {
    "id": "asus-CM1400CXA-dalboz",
    "body": HardwareDetailsPostBody(
        origin="maestro",
        startTimestampInSeconds=1741356000,
        endTimestampInSeconds=1741788000,
        selectedCommits={},
        filter={},
    ),
}

# https://dashboard.kernelci.org/hardware/amlogic%2Cg12b?et=1741791600&st=1741359600
AMLOGIC_G12B_HARDWARE = {
    "id": "amlogic,g12b",
    "body": HardwareDetailsPostBody(
        origin="maestro",
        startTimestampInSeconds=1741359600,
        endTimestampInSeconds=1741791600,
        selectedCommits={},
        filter={},
    ),
}


client = HardwareClient()


def pytest_generate_tests(metafunc):
    test_status_cases = [
        (ASUS_HARDWARE, {"boot.status": "FAIL"}),
        (ASUS_HARDWARE, {"test.status": "PASS"}),
    ]

    hardware_cases = [
        (ASUS_HARDWARE, {"test.hardware": "arm,juno"}),
    ]

    issues_cases = [
        (
            ASUS_HARDWARE,
            {"boot.issue": "maestro:da694c56147298d223ee432ad8d6a8ee311b773a,1"},
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
                (ASUS_HARDWARE, {"boot.status": "ERROR"}),
                (ASUS_HARDWARE, {"boot.status": "MISS"}),
                (ASUS_HARDWARE, {"boot.status": "DONE"}),
                (ASUS_HARDWARE, {"boot.status": "NULL"}),
                (ASUS_HARDWARE, {"test.status": "ERROR"}),
                (ASUS_HARDWARE, {"test.status": "MISS"}),
                (ASUS_HARDWARE, {"test.status": "DONE"}),
                (ASUS_HARDWARE, {"test.status": "NULL"}),
                (ASUS_HARDWARE, {"boot.status": "PASS"}),
                (ASUS_HARDWARE, {"boot.status": "SKIP"}),
                (ASUS_HARDWARE, {"test.status": "SKIP"}),
                (ASUS_HARDWARE, {"test.status": "FAIL"}),
            ]
        metafunc.parametrize("test_status_input", base_cases + extra_cases)

    if "hardware_input" in metafunc.fixturenames:
        base_cases = hardware_cases
        extra_cases = []
        if metafunc.config.getoption("--run-all"):
            extra_cases = [
                (ASUS_HARDWARE, {"test.hardware": "acer-chromebox-cxi4-puff"}),
            ]
        metafunc.parametrize("hardware_input", base_cases + extra_cases)

    if "issues_input" in metafunc.fixturenames:
        base_cases = issues_cases
        extra_cases = []
        if metafunc.config.getoption("--run-all"):
            extra_cases = [
                (
                    ASUS_HARDWARE,
                    {"test.issue": f"{UNCATEGORIZED_STRING},null"},
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


def request_data(
    base_hardware: dict, filters: dict | None = None
) -> tuple[Response, dict]:
    hardware_id = base_hardware["id"]
    body = base_hardware["body"]
    if filters is not None:
        body.filter = {f"filter_{f}": v for f, v in filters.items()}
    response = client.post_hardware_details_summary(hardware_id=hardware_id, body=body)
    content = string_to_json(response.content.decode())
    return response, content


@pytest.mark.parametrize(
    "base_hardware, status_code, has_error_body",
    [
        (INVALID_BODY_HARDWARE, HTTPStatus.BAD_REQUEST, True),
        (INVALID_ID_HARDWARE, HTTPStatus.OK, True),
        (ASUS_HARDWARE, HTTPStatus.OK, False),
    ],
)
def test_no_filters(base_hardware, status_code, has_error_body):
    response, content = request_data(base_hardware)
    assert_status_code(response=response, status_code=status_code)
    if has_error_body:
        assert_error_response(response_content=content)
    else:
        assert_has_fields_in_response_content(
            fields=hardware.hardware_summary, response_content=content
        )
        assert_has_fields_in_response_content(
            fields=hardware.hardware_summary_summary,
            response_content=content["summary"],
        )
        assert_has_fields_in_response_content(
            fields=hardware.hardware_summary_common, response_content=content["common"]
        )
        assert_has_fields_in_response_content(
            fields=hardware.hardware_summary_filters,
            response_content=content["filters"],
        )
        assert_has_fields_in_response_content(
            fields=hardware.hardware_test_summary,
            response_content=content["summary"]["tests"],
        )
        assert_has_fields_in_response_content(
            fields=hardware.hardware_test_summary,
            response_content=content["summary"]["boots"],
        )
        assert_has_fields_in_response_content(
            fields=hardware.hardware_build_summary,
            response_content=content["summary"]["builds"],
        )


def test_filter_test_status(test_status_input):
    """
    Tests for the status filter for both boots and tests
    (couldn't add build to the same test function because it has a different nomenclature).
    This test only for when 1 status is being passed to the filter
    """
    base_hardware, filters = test_status_input
    response, content = request_data(base_hardware, filters)
    assert_status_code(response=response, status_code=HTTPStatus.OK)
    assert "error" not in content

    # filter task = 'boot' | 'test' and response task = 'boots' | 'tests'
    task, value = list(filters.items())[0]
    task = task.split(".")[0] + "s"

    assert_common_summary_status_fields(content, task, value)
    task_summary = content["summary"][task]

    assert "environment_compatible" in task_summary
    assert task_summary["environment_compatible"] is None

    assert "environment_misc" in task_summary
    assert task_summary["environment_misc"] is None

    assert "architectures" in task_summary
    for arch in task_summary["architectures"]:
        for status, count in arch["status"].items():
            if status != value:
                assert count == 0


@pytest.mark.parametrize(
    "base_hardware, filters",
    [
        (ASUS_HARDWARE, {"build.status": "PASS"}),
        (ASUS_HARDWARE, {"build.status": "FAIL"}),
        (ASUS_HARDWARE, {"build.status": "NULL"}),
    ],
)
def test_filter_build_status(base_hardware, filters):
    """
    Tests for the status filter for builds
    This test only for when 1 status is being passed to the filter
    """
    response, content = request_data(base_hardware, filters)
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
    "base_hardware, filters",
    [
        (ASUS_HARDWARE, {"config_name": "defconfig+kcidebug+x86-board"}),
    ],
)
def test_filter_config_name(base_hardware, filters):
    response, content = request_data(base_hardware, filters)
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
    "base_hardware, filters",
    [
        (ASUS_HARDWARE, {"architecture": "i386"}),
    ],
)
def test_filter_architectures(base_hardware, filters):
    response, content = request_data(base_hardware, filters)
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
    "base_hardware, filters",
    [
        (ASUS_HARDWARE, {"compiler": "gcc-12"}),
    ],
)
def test_filter_compiler(base_hardware, filters):
    response, content = request_data(base_hardware, filters)
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


@pytest.mark.parametrize(
    "base_hardware, filters",
    [
        (AMLOGIC_G12B_HARDWARE, {"boot.platform": ["meson-g12b-a311d-khadas-vim3"]}),
        (AMLOGIC_G12B_HARDWARE, {"test.platform": ["meson-g12b-a311d-libretech-cc"]}),
    ],
)
def test_platform(base_hardware, filters):
    response, content = request_data(base_hardware, filters)
    assert_status_code(response=response, status_code=HTTPStatus.OK)
    assert "error" not in content

    # filter task = 'boot' | 'test' and response task = 'boots' | 'tests'
    task, values = list(filters.items())[0]
    task = task.split(".")[0] + "s"

    assert "summary" in content
    assert task in content["summary"]
    task_summary = content["summary"][task]
    assert "platforms" in task_summary
    assert len(task_summary["platforms"].keys()) == len(values)
    for value in values:
        assert value in task_summary["platforms"]

    status_count = {s: 0 for s in task_summary["status"]}
    for platform in task_summary["platforms"].values():
        for status, count in platform.items():
            status_count[status] += count

    for status, count in status_count.items():
        assert task_summary["status"][status] == count


def test_filter_issues(issues_input):
    base_hardware, filters = issues_input
    response, content = request_data(base_hardware, filters)
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
    pass_count = task_summary["status"].get("PASS", task_summary["status"].get("valid"))
    assert pass_count == 0


def test_invalid_filters(invalid_filters_input):
    empty_test = {
        "architectures": [],
        "origins": {},
        "configs": {},
        "environment_compatible": None,
        "environment_misc": None,
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

    empty_summary = {
        "builds": empty_build,
        "boots": empty_test,
        "tests": empty_test,
    }

    filter, local_field = invalid_filters_input
    response, content = request_data(ASUS_HARDWARE, {filter: "invalid_filter,null"})
    assert_status_code(response=response, status_code=HTTPStatus.OK)
    assert "error" not in content
    assert "summary" in content
    if local_field is None:
        assert content["summary"] == empty_summary
    else:
        assert content["summary"][local_field] == empty_summary[local_field]
