MAINLINE_URL = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"

TREE_NAMES_MOCK = {
    MAINLINE_URL: "mainline",
}


SUBMISSION_PATH_MOCK = "/tmp/test_submission.json"
SUBMISSION_FILE_MOCK = '{"test": "data"}'
SUBMISSION_FILE_DATA_MOCK = {"test": "data"}
SUBMISSION_FILENAME_MOCK = "test_submission.json"
SUBMISSION_FILEPATH_MOCK = "/tmp/"


INGEST_BATCH_SIZE_MOCK = 255


FLUSH_TIMEOUT_SEC_MOCK = 1


FAILED_SUBMISSIONS_DIR = "submissions/failed"
ARCHIVE_SUBMISSIONS_DIR = "submissions/archive"
PENDING_RETRY_SUBMISSIONS_DIR = "submissions/pending_retry"

SUBMISSION_DIRS_MOCK = {
    "failed": FAILED_SUBMISSIONS_DIR,
    "archive": ARCHIVE_SUBMISSIONS_DIR,
    "pending_retry": PENDING_RETRY_SUBMISSIONS_DIR,
}


# Note: not all tests that call time.time() need 4 values,
# but it's simpler to have a single list.
TIME_MOCK = [1000, 1001, 1002, 1003]
