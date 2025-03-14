hardware_listing_fields = [
    "hardware_name",
    "platform",
    "test_status_summary",
    "boot_status_summary",
    "build_status_summary",
]

test_status_summary_fields = ["FAIL", "PASS", "SKIP", "ERROR", "MISS", "NULL", "DONE"]
build_status_summary_fields = ["valid", "invalid", "null"]

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
