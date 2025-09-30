base_checkout_data = {
    "checkout_id": "checkout123",
    "origin": "test",
    "tree_name": "mainline",
    "git_repository_url": "https://git.kernel.org",
    "git_repository_branch": "master",
    "git_commit_hash": "abc123",
    "git_commit_name": "commit1",
    "git_commit_tag": "v5.4",
    "pass_builds": 10,
    "fail_builds": 2,
    "null_builds": 1,
    "error_builds": 0,
    "miss_builds": 0,
    "done_builds": 0,
    "skip_builds": 0,
    "pass_tests": 50,
    "fail_tests": 5,
    "null_tests": 2,
    "error_tests": 1,
    "miss_tests": 0,
    "done_tests": 0,
    "skip_tests": 0,
    "pass_boots": 20,
    "fail_boots": 1,
    "null_boots": 0,
    "error_boots": 0,
    "miss_boots": 0,
    "done_boots": 0,
    "skip_boots": 0,
    "start_time": "2023-01-01T00:00:00",
    "origin_builds_finish_time": "2023-01-01T01:00:00",
    "origin_tests_finish_time": "2023-01-01T02:00:00",
}

checkout_data_with_list_tags = {
    **base_checkout_data,
    "git_commit_tags": [["v5.4"], ["v5.4.1"]],
}

checkout_data_with_string_tags = {
    **base_checkout_data,
    "git_commit_tags": '[["v5.4"], ["v5.4.1"]]',
}

checkout_data_with_invalid_json_tags = {
    **base_checkout_data,
    "git_commit_tags": "invalid json",
}

checkout_data_with_non_list_json_tags = {
    **base_checkout_data,
    "git_commit_tags": '{"not": "a_list"}',
}
