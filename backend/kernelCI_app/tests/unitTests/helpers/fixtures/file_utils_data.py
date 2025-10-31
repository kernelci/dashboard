TREES_PATH_TESTING = "/test/trees.yaml"

mainline_url = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"
next_url = "https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git"
stable_url = "https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git"

BASE_TREES_FILE = {
    "trees": {
        "mainline": {"url": mainline_url},
        "next": {"url": next_url},
        "stable": {"url": stable_url},
    }
}

EXPECTED_PARSED_TREES_FILE = {
    mainline_url: "mainline",
    next_url: "next",
    stable_url: "stable",
}


BASE_FILE_NAME = "test_file.json"
NONEXISTING_FILE_NAME = "nonexistent_file.json"
TESTING_FAILED_DIR = "/failed/dir"

EXISTING_DIRECTORY = "/existing/directory"
MISSING_DIRECTORY = "/missing/directory"
DENIED_DIRECTORY = "/denied/directory"
NOT_A_DIRECTORY = "/not/a/directory.file"
INACCESSIBLE_DIRECTORY = "/inaccessible/directory"

SPOOL_DIR_TESTING = "/spool"
FAIL_SPOOL_SUBDIR = "failed"
ARCHIVE_SPOOL_SUBDIR = "archive"
