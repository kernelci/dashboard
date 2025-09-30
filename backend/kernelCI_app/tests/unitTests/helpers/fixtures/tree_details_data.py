from kernelCI_app.constants.general import UNKNOWN_STRING


def create_row(**overrides):
    """Create minimal row data with only necessary fields."""
    field_mapping = {
        "test_status": 7,
        "test_path": 4,
        "test_environment_compatible": 12,
        "build_architecture": 18,
        "build_compiler": 20,
        "build_config_name": 21,
        "build_status": 24,
        "issue_id": 34,
        "issue_version": 35,
    }

    base_row = [
        "test123",  # test_id
        "test_origin",  # test_origin
        "env_comment",  # env_comment
        "{}",  # env_misc
        "test.path",  # test_path
        "test_comment",  # test_comment
        "http://log.com",  # test_log_url
        "PASS",  # test_status
        "2024-01-15T10:00:00Z",  # test_start_time
        100,  # test_duration
        1,  # test_incident_id
        "{}",  # test_misc
        ["hardware1"],  # test_environment_compatible
        "build123",  # build_id
        "build_origin",  # build_origin
        "build_comment",  # build_comment
        "2024-01-15T09:00:00Z",  # build_start_time
        200,  # build_duration
        "x86_64",  # build_architecture
        "make",  # build_command
        "gcc",  # build_compiler
        "defconfig",  # build_config_name
        "http://config.com",  # build_config_url
        "http://build_log.com",  # build_log_url
        "PASS",  # build_status
        "{}",  # build_misc
        "checkout123",  # checkout_id
        "https://git.kernel.org",  # checkout_git_repository_url
        "master",  # checkout_git_repository_branch
        "v5.4",  # checkout_git_commit_tag
        "origin",  # checkout_origin
        "incident123",  # incident_id
        "test123",  # incident_test_id
        True,  # incident_is_culprit
        "issue123",  # issue_id
        1,  # issue_version
        "issue_comment",  # issue_comment
        "http://issue.com",  # issue_report_url
    ]

    for key, value in overrides.items():
        if key in field_mapping:
            base_row[field_mapping[key]] = value

    return base_row


base_current_row = create_row()

current_row_with_none_values = create_row(
    test_path=None,
    test_status=None,
    test_environment_compatible=None,
    build_architecture=None,
    build_compiler=None,
    build_config_name=None,
    build_status=None,
    issue_id=None,
    issue_version=None,
)

current_row_with_fail_status = create_row(
    test_status="FAIL",
    build_status="FAIL",
    issue_id=None,
    issue_version=None,
)


def create_summary_row_data(**overrides):
    """Create minimal row data for summary tests."""
    base_data = {
        "test_status": "FAIL",
        "build_config_name": "defconfig",
        "build_architecture": "x86_64",
        "build_compiler": "gcc",
        "test_platform": "x86_64",
        "test_error": "Test error",
        "test_environment_compatible": "hardware1",
        "test_origin": "test",
    }
    base_data.update(overrides)
    return base_data


def create_filter_row_data(**overrides):
    """Create minimal row data for filter tests."""
    base_data = {
        "build_id": "build123",
        "test_id": "test123",
        "issue_id": "issue123",
        "issue_version": 1,
        "incident_test_id": "test123",
        "build_status": "FAIL",
        "test_status": "FAIL",
        "test_path": "test.specific",
        "build_config_name": "defconfig",
        "build_architecture": "x86_64",
        "build_compiler": "gcc",
        "build_origin": "build_origin",
        "test_origin": "test_origin",
    }
    base_data.update(overrides)
    return base_data


base_row_data = create_summary_row_data()

row_data_with_unknown_compatible = create_summary_row_data(
    test_environment_compatible=UNKNOWN_STRING,
    test_status="PASS",
)

build_only_row_data = create_filter_row_data(
    test_id=None,
    incident_test_id=None,
    test_status=None,
    test_path=None,
    test_origin=None,
)

test_only_row_data = create_filter_row_data(
    build_id=None,
    issue_id="issue456",
    issue_version=2,
    test_path="boot.test",
    build_status=None,
    build_config_name=None,
    build_architecture=None,
    build_compiler=None,
    build_origin=None,
)

combined_row_data = create_filter_row_data()


def create_mock_instance(**overrides):
    """Create minimal mock instance for tests."""
    base_instance = {
        "global_configs": set(),
        "global_architectures": set(),
        "global_compilers": set(),
        "unfiltered_origins": {"build": set(), "test": set()},
        "unfiltered_build_issues": set(),
        "unfiltered_test_issues": set(),
        "unfiltered_uncategorized_issue_flags": {"build": False, "test": False},
    }
    base_instance.update(overrides)
    return base_instance


base_mock_instance = create_mock_instance()

build_only_mock_instance = create_mock_instance(
    unfiltered_origins={"build": set()},
    unfiltered_uncategorized_issue_flags={"build": False},
)

test_only_mock_instance = create_mock_instance(
    unfiltered_origins={"boot": set()},
    unfiltered_boot_issues=set(),
    unfiltered_uncategorized_issue_flags={"boot": False},
)
