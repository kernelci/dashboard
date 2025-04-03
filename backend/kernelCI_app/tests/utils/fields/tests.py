issue_tests_expected_fields = [
    "id",
    "status",
    "path",
    "start_time",
    "environment_compatible",
    "environment_misc",
    "tree_name",
    "git_repository_branch",
]

test_details_expected_fields = [
    "field_timestamp",
    "id",
    "build_id",
    "status",
    "path",
    "log_excerpt",
    "log_url",
    "misc",
    "environment_misc",
    "start_time",
    "environment_compatible",
    "output_files",
    "input_files",
    "compiler",
    "architecture",
    "config_name",
    "git_commit_hash",
    "git_repository_branch",
    "git_repository_url",
    "git_commit_tags",
    "tree_name",
    "origin",
]

status_history_response_expected_fields = [
    "status_history",
    "regression_type",
]

status_history_item_fields = [
    "id",
    "status",
    "start_time",
    "git_commit_hash",
]
