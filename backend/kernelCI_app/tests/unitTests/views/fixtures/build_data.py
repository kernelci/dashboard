from datetime import datetime

from kernelCI_app.typeModels.common import StatusCount

build_details_data = {
    "id": "test_build_123",
    "origin": "test_origin",
    "architecture": "test_architecture",
    "config_name": "test_config_name",
    "misc": None,
    "config_url": "test_config_url",
    "compiler": "test_compiler",
    "status": "PASS",
    "duration": 100,
    "log_url": "test_log_url",
    "start_time": datetime.now(),
    "git_repository_url": "test_url.com",
    "git_repository_branch": "test_branch",
    "checkout_id": "test_checkout_123",
    "command": "test_command",
    "comment": "test_comment",
    "tree_name": "test_tree_name",
    "git_commit_hash": "test_git_commit_hash",
    "git_commit_name": "test_git_commit_name",
    "git_commit_tags": ["test_git_commit_tag"],
    "origin": "test_origin",
    "log_excerpt": "test_log_excerpt",
    "input_files": None,
    "output_files": None,
    "build_origin": "test_build_origin",
}

base_issue_data = {
    "id": "test_issue_123",
    "version": 1,
    "comment": "test_comment",
    "report_url": "test_report_url",
    "incidents_info": StatusCount(
        DONE=0, PASS=1, FAIL=0, ERROR=0, SKIP=0, MISS=0, NULL=0
    ),
}

base_test_data = {
    "id": "test_test_123",
    "status": "PASS",
    "duration": 30,
    "path": "test_path",
    "start_time": datetime.now(),
    "environment_compatible": ["test_environment_compatible"],
    "environment_misc": {"test_environment_misc": "test_environment_misc"},
}
