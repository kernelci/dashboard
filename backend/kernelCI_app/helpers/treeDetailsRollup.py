from kernelCI_app.constants.process_pending import ROLLUP_STATUS_FIELDS
from kernelCI_app.constants.general import UNCATEGORIZED_STRING, UNKNOWN_STRING
from kernelCI_app.helpers.commonDetails import PossibleTabs, add_unfiltered_issue
from kernelCI_app.helpers.filters import (
    is_status_failure,
    should_filter_test_issue,
    should_increment_build_issue,
    should_increment_test_issue,
)
from kernelCI_app.helpers.misc import handle_misc
from kernelCI_app.typeModels.common import StatusCount
from kernelCI_app.typeModels.databases import (
    FAIL_STATUS,
    NULL_STATUS,
    build_fail_status_list,
    failure_status_list,
)
from kernelCI_app.typeModels.issues import Issue, IssueDict
from kernelCI_app.utils import create_issue_typed

ROLLUP_TEST_ID = "rollup_test"


def normalize_build_dict(row_dict: dict) -> dict:
    """Normalize a dict row from get_tree_details_builds into the shape
    expected by existing build-processing helpers."""
    row_dict["build_misc"] = handle_misc(row_dict.get("build_misc"))

    if row_dict.get("build_status") is None:
        row_dict["build_status"] = NULL_STATUS
    if row_dict.get("build_architecture") is None:
        row_dict["build_architecture"] = UNKNOWN_STRING
    if row_dict.get("build_compiler") is None:
        row_dict["build_compiler"] = UNKNOWN_STRING
    if row_dict.get("build_config_name") is None:
        row_dict["build_config_name"] = UNKNOWN_STRING

    if row_dict.get("issue_id") is None and is_status_failure(
        row_dict["build_status"], build_fail_status_list
    ):
        row_dict["issue_id"] = UNCATEGORIZED_STRING

    return row_dict


def process_build_filters(instance, row_data: dict) -> None:
    """Populate global filter sets and unfiltered build issues from a build row."""
    build_status = row_data["build_status"]
    issue_id = row_data.get("issue_id")
    issue_version = row_data.get("issue_version")
    incident_test_id = row_data.get("incident_test_id")

    instance.global_configs.add(row_data["build_config_name"])
    instance.global_architectures.add(row_data["build_architecture"])
    instance.global_compilers.add(row_data["build_compiler"])
    instance.unfiltered_origins["build"].add(row_data["build_origin"])

    if (build_misc := row_data["build_misc"]) is not None:
        instance.unfiltered_labs["build"].add(build_misc.get("lab", UNKNOWN_STRING))

    build_issue_id, build_issue_version, is_build_issue = should_increment_build_issue(
        issue_id=issue_id,
        issue_version=issue_version,
        incident_test_id=incident_test_id,
        build_status=build_status,
    )

    add_unfiltered_issue(
        issue_id=build_issue_id,
        issue_version=build_issue_version,
        should_increment=is_build_issue,
        issue_set=instance.unfiltered_build_issues,
        unknown_issue_flag_dict=instance.unfiltered_uncategorized_issue_flags,
        unknown_issue_flag_tab="build",
        is_failed_task=build_status == FAIL_STATUS,
    )


def process_rollup_filters(instance, row_dict: dict) -> None:
    """Populate unfiltered issue/origin/lab sets from a rollup row."""
    issue_id = row_dict.get("issue_id")
    issue_version = row_dict.get("issue_version")
    is_boot_row = row_dict["is_boot"]

    incident_test_id = ROLLUP_TEST_ID if issue_id is not None else None

    test_issue_id, test_issue_version, is_test_issue = should_increment_test_issue(
        issue_id=issue_id,
        issue_version=issue_version,
        incident_test_id=incident_test_id,
    )

    if is_boot_row:
        issue_set = instance.unfiltered_boot_issues
        origin_set = instance.unfiltered_origins["boot"]
        lab_set = instance.unfiltered_labs["boot"]
        flag_tab: PossibleTabs = "boot"
    else:
        issue_set = instance.unfiltered_test_issues
        origin_set = instance.unfiltered_origins["test"]
        lab_set = instance.unfiltered_labs["test"]
        flag_tab: PossibleTabs = "test"

    has_failures = row_dict.get("issue_uncategorized", False)
    add_unfiltered_issue(
        issue_id=test_issue_id,
        issue_version=test_issue_version,
        should_increment=is_test_issue,
        issue_set=issue_set,
        is_failed_task=has_failures,
        unknown_issue_flag_dict=instance.unfiltered_uncategorized_issue_flags,
        unknown_issue_flag_tab=flag_tab,
    )

    test_origin = row_dict.get("test_origin", UNKNOWN_STRING)
    test_lab = row_dict.get("test_lab", UNKNOWN_STRING) or UNKNOWN_STRING
    origin_set.add(test_origin)
    lab_set.add(test_lab)


def rollup_test_or_boot_filtered_out(
    instance,
    *,
    row_dict: dict,
    is_boot_row: bool,
) -> bool:
    """Check if a rollup row is filtered by test/boot filters."""
    issue_id = row_dict.get("issue_id")
    issue_version = row_dict.get("issue_version")

    if issue_id is None and row_dict.get("issue_uncategorized", False):
        issue_id = UNCATEGORIZED_STRING

    incident_test_id = ROLLUP_TEST_ID if issue_id is not None else None
    path_group = row_dict.get("path_group", UNKNOWN_STRING)
    test_origin = row_dict.get("test_origin")
    test_platform = row_dict.get("test_platform")

    if is_boot_row:
        path_filter = instance.filters.filterBootPath
        issue_filters = instance.filters.filterIssues["boot"]
        platform_filters = instance.filters.filterPlatforms["boot"]
        origin_filters = instance.filters.filter_boot_origin
    else:
        path_filter = instance.filters.filterTestPath
        issue_filters = instance.filters.filterIssues["test"]
        platform_filters = instance.filters.filterPlatforms["test"]
        origin_filters = instance.filters.filter_test_origin

    if path_filter != "" and path_filter not in path_group:
        return True

    if should_filter_test_issue(
        issue_filters=issue_filters,
        issue_id=issue_id,
        issue_version=issue_version,
        incident_test_id=incident_test_id,
    ):
        return True

    if len(platform_filters) > 0 and test_platform not in platform_filters:
        return True

    if len(origin_filters) > 0 and test_origin not in origin_filters:
        return True

    return False


def _get_rollup_status_filter(instance, *, is_boot_row: bool) -> set[str]:
    """Return the active status filter set for boots or tests."""
    if is_boot_row:
        return set(instance.filters.filterBootStatus)
    return set(instance.filters.filterTestStatus)


def process_rollup_summary(instance, *, row_dict: dict, is_boot_row: bool) -> None:
    """Accumulate pre-aggregated test/boot counts from a rollup row into
    the instance's summary accumulators."""
    build_config = row_dict["build_config_name"]
    build_arch = row_dict["build_architecture"]
    build_compiler = row_dict["build_compiler"]
    hardware_key = row_dict["hardware_key"]
    test_platform = row_dict.get("test_platform")
    test_origin = row_dict.get("test_origin", UNKNOWN_STRING)
    test_lab = row_dict.get("test_lab", UNKNOWN_STRING) or UNKNOWN_STRING

    status_filter = _get_rollup_status_filter(instance, is_boot_row=is_boot_row)

    # Skip row entirely if status filter excludes all its statuses
    if status_filter:
        has_matching_status = any(
            row_dict.get(field_name, 0) > 0 and status_name in status_filter
            for status_name, field_name in ROLLUP_STATUS_FIELDS.items()
        )
        if not has_matching_status:
            return

    if is_boot_row:
        status_summary = instance.bootStatusSummary
        arch_summary_map = instance.bootArchSummary
        config_map = instance.bootConfigs
        platforms_failing = instance.bootPlatformsFailing
        env_compatible = instance.bootEnvironmentCompatible
        env_misc = instance.bootEnvironmentMisc
        origin_summary = instance.boot_summary["origins"]
        typed_summary = instance.boot_summary_typed
    else:
        status_summary = instance.testStatusSummary
        arch_summary_map = instance.test_arch_summary
        config_map = instance.test_configs
        platforms_failing = instance.testPlatformsWithErrors
        env_compatible = instance.testEnvironmentCompatible
        env_misc = instance.testEnvironmentMisc
        origin_summary = instance.test_summary["origins"]
        typed_summary = instance.test_summary_typed

    arch_key = "%s-%s" % (build_arch, build_compiler)
    arch_entry = arch_summary_map.setdefault(
        arch_key,
        {"arch": build_arch, "compiler": build_compiler, "status": {}},
    )
    config_entry = config_map.setdefault(build_config, {})

    is_env_compatible = hardware_key != UNKNOWN_STRING and hardware_key != test_platform

    has_failure_counts = False

    for status_name, field_name in ROLLUP_STATUS_FIELDS.items():
        count = row_dict.get(field_name, 0)
        if count <= 0:
            continue
        if status_filter and status_name not in status_filter:
            continue

        status_summary[status_name] = status_summary.get(status_name, 0) + count
        arch_entry["status"][status_name] = (
            arch_entry["status"].get(status_name, 0) + count
        )
        config_entry[status_name] = config_entry.get(status_name, 0) + count

        if is_env_compatible:
            env_compatible[hardware_key][status_name] += count
        else:
            env_misc[test_platform][status_name] += count

        origin_entry = origin_summary.setdefault(test_origin, StatusCount())
        setattr(
            origin_entry,
            status_name,
            getattr(origin_entry, status_name) + count,
        )

        lab_entry = typed_summary.labs.setdefault(test_lab, StatusCount())
        setattr(lab_entry, status_name, getattr(lab_entry, status_name) + count)

        if is_status_failure(status_name):
            has_failure_counts = True

    if has_failure_counts:
        platforms_failing.add(test_platform)


def process_rollup_issues(instance, *, row_dict: dict, is_boot_row: bool) -> None:
    """Accumulate issue information from a rollup row."""
    issue_id = row_dict.get("issue_id")
    issue_version = row_dict.get("issue_version")
    issue_comment = row_dict.get("issue_comment")
    issue_report_url = row_dict.get("issue_report_url")

    incident_test_id = ROLLUP_TEST_ID if issue_id is not None else None

    test_issue_id, test_issue_version, can_insert_issue = should_increment_test_issue(
        issue_id=issue_id,
        issue_version=issue_version,
        incident_test_id=incident_test_id,
    )

    failure_counts = [
        (status, row_dict.get(ROLLUP_STATUS_FIELDS[status], 0))
        for status in failure_status_list
    ]

    if test_issue_id and test_issue_version is not None and can_insert_issue:
        table: IssueDict = (
            instance.boot_issues_dict if is_boot_row else instance.test_issues_dict
        )
        current_issue: Issue | None = table.get((test_issue_id, test_issue_version))
        if current_issue:
            for status, count in failure_counts:
                for _ in range(count):
                    current_issue.incidents_info.increment(status)
        else:
            first_status = next((s for s, c in failure_counts if c > 0), None)
            table[(test_issue_id, test_issue_version)] = create_issue_typed(
                issue_id=test_issue_id,
                issue_version=test_issue_version,
                issue_comment=issue_comment,
                issue_report_url=issue_report_url,
                starting_count_status=first_status,
            )
            for status, count in failure_counts:
                remaining = count - 1 if status == first_status else count
                for _ in range(max(0, remaining)):
                    table[(test_issue_id, test_issue_version)].incidents_info.increment(
                        status
                    )

    elif row_dict.get("issue_uncategorized", False):
        status_filter = _get_rollup_status_filter(instance, is_boot_row=is_boot_row)
        if not status_filter or "FAIL" in status_filter:
            fail_count = row_dict.get("fail_tests", 0)
            if is_boot_row:
                instance.failed_boots_with_unknown_issues += fail_count
            else:
                instance.failed_tests_with_unknown_issues += fail_count
