hardware_listing_fields = [
    "hardware",
    "platform",
    "test_status_summary",
    "boot_status_summary",
    "build_status_summary",
]

status_summary_fields = ["FAIL", "PASS", "SKIP", "ERROR", "MISS", "NULL", "DONE"]

hardware_summary = ["common", "summary", "filters"]
hardware_summary_common = ["trees", "compatibles"]
hardware_summary_filters = ["all", "builds", "boots", "tests"]
hardware_summary_summary = ["boots", "builds", "tests"]
hardware_build_summary = [
    "status",
    "architectures",
    "configs",
    "issues",
    "unknown_issues",
]
hardware_test_summary = [
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

hardware_history_checkouts = [
    "git_commit_hash",
    "tree_name",
    "git_repository_branch",
    "git_repository_url",
    "git_commit_tags",
    "git_commit_name",
    "start_time",
]
