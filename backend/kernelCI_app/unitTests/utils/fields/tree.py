tree_summary = ["common", "summary", "filters"]
tree_summary_common = ["tree_url", "hardware", "git_commit_tags"]
tree_summary_filters = ["all", "builds", "boots", "tests"]
tree_summary_summary = ["boots", "builds", "tests"]
tree_build_summary = ["status", "architectures", "configs", "issues", "unknown_issues"]
tree_test_summary = [
    "status",
    "architectures",
    "configs",
    "issues",
    "unknown_issues",
    "environment_compatible",
    "environment_misc",
    "fail_reasons",
    "failed_platforms",
]
tree_fast = [
    "id",
    "tree_name",
    "git_repository_branch",
    "git_repository_url",
    "git_commit_hash",
    "git_commit_name",
    "git_commit_tags",
    "patchset_hash",
    "start_time",
]

tree_listing = [
    "git_repository_branch",
    "git_repository_url",
    "git_commit_hash",
    "git_commit_tags",
    "git_commit_name",
    "start_time",
    "build_status",
    "test_status",
    "boot_status",
    "tree_names",
]
tree_listing_build_status = ["valid", "invalid", "null"]
tree_listing_test_status = [
    "fail",
    "error",
    "miss",
    "pass",
    "done",
    "skip",
    "null",
]
tree_commit_history = [
    "git_commit_hash",
    "git_commit_name",
    "git_commit_tags",
    "earliest_start_time",
    "builds",
    "boots",
    "tests",
]
tree_commit_history_tests = [
    "fail",
    "error",
    "miss",
    "pass",
    "done",
    "skip",
    "null",
]
tree_commit_history_builds = [
    "valid",
    "invalid",
    "null",
]
