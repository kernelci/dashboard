from unittest.mock import patch, MagicMock, mock_open, call

from kernelCI_app.tests.unitTests.helpers.fixtures.kcidbng_ingester_data import (
    ARCHIVE_SUBMISSIONS_DIR,
    INGEST_BATCH_SIZE_MOCK,
    MAINLINE_URL,
    SUBMISSION_DIRS_MOCK,
    SUBMISSION_FILEPATH_MOCK,
    TIME_MOCK,
    TREE_NAMES_MOCK,
    SUBMISSION_PATH_MOCK,
    SUBMISSION_FILE_MOCK,
    SUBMISSION_FILE_DATA_MOCK,
    SUBMISSION_FILENAME_MOCK,
)
from kernelCI_app.constants.ingester import AUTOMATIC_LAB_FIELD
import pytest

from kernelCI_app.management.commands.helpers.kcidbng_ingester import (
    SubmissionFileMetadata,
    standardize_tree_names,
    standardize_labs,
    prepare_file_data,
    consume_buffer,
    flush_buffers,
    ingest_submissions_parallel,
)


class TestStandardizeTreeNames:
    """Test cases for standardize_tree_names function."""

    # Test cases:
    # - replaces wrong name with correct name when git_url matches
    # - leaves name unchanged when git_url does not match
    # - leaves name unchanged when already correct
    # - leaves name unchanged when only git_repository_url is missing
    # - corrects name when only tree_name is missing or leaves it unchanged if url doesn't match

    def test_standardize_tree_names_with_matching_url(self):
        """Test that tree names are standardized when git_url matches."""
        input_data = {
            "checkouts": [
                {
                    "git_repository_url": (MAINLINE_URL),
                    "tree_name": "wrong_mainline_name",
                },
            ]
        }

        standardize_tree_names(input_data, TREE_NAMES_MOCK)

        assert input_data["checkouts"][0]["tree_name"] == "mainline"

    def test_standardize_tree_names_no_matching_url(self):
        """Test that tree names remain unchanged when git_url doesn't match."""
        input_data = {
            "checkouts": [
                {
                    "git_repository_url": "https://some.unexisting.repo.git",
                    "tree_name": "original_name",
                }
            ]
        }

        standardize_tree_names(input_data, TREE_NAMES_MOCK)

        assert input_data["checkouts"][0]["tree_name"] == "original_name"

    def test_standardize_tree_names_same_tree_name(self):
        """Test that tree names remain unchanged when already correct."""
        input_data = {
            "checkouts": [
                {
                    "git_repository_url": (MAINLINE_URL),
                    "tree_name": "mainline",
                }
            ]
        }

        standardize_tree_names(input_data, TREE_NAMES_MOCK)

        assert input_data["checkouts"][0]["tree_name"] == "mainline"

    def test_standardize_tree_names_missing_url(self):
        """Test with checkout missing git_repository_url."""
        input_data = {
            "checkouts": [
                {"tree_name": "mainline"},
                {"tree_name": "something_else"},
            ]
        }

        standardize_tree_names(input_data, TREE_NAMES_MOCK)

        assert input_data["checkouts"][0]["tree_name"] == "mainline"
        assert input_data["checkouts"][1]["tree_name"] == "something_else"

    def test_standardize_tree_names_missing_tree_name(self):
        """Test with checkouts missing tree_name. Either with correct url or with some other url."""
        input_data = {
            "checkouts": [
                {"git_repository_url": MAINLINE_URL},
                {"git_repository_url": "https://some.unexisting.repo.git"},
            ]
        }

        standardize_tree_names(input_data, TREE_NAMES_MOCK)

        assert input_data["checkouts"][0]["tree_name"] == "mainline"
        assert "tree_name" not in input_data["checkouts"][1]


class TestStandardizeLabs:
    """Test cases for standardize_labs function."""

    # Test cases:
    # - builds/tests with missing misc field
    # - builds/tests with misc but not lab field
    # - empty builds/tests data
    # - builds/tests with real/automatic labs/runtimes

    def test_standardize_labs_missing_misc(self):
        """Test with builds/tests missing misc field."""
        input_data = {
            "builds": [
                {"id": "build1"},
            ],
            "tests": [
                {"id": "test1"},
            ],
        }

        standardize_labs(input_data)

        assert "misc" not in input_data["builds"][0]
        assert "misc" not in input_data["tests"][0]

    def test_standardize_labs_missing_lab_runtime(self):
        """Test with builds/tests having misc but missing lab/runtime field."""
        input_data = {
            "builds": [
                {
                    "misc": {
                        "other_field": "value",
                    }
                },
            ],
            "tests": [
                {
                    "misc": {
                        "platform": "x86",
                    }
                },
            ],
        }

        standardize_labs(input_data)

        assert "lab" not in input_data["builds"][0]["misc"]
        assert AUTOMATIC_LAB_FIELD not in input_data["builds"][0]["misc"]
        assert "runtime" not in input_data["tests"][0]["misc"]
        assert AUTOMATIC_LAB_FIELD not in input_data["tests"][0]["misc"]

    def test_standardize_labs_empty_data(self):
        """Test with empty builds and tests."""
        input_data = {
            "builds": [],
            "tests": [],
        }

        standardize_labs(input_data)

        assert input_data["builds"] == []
        assert input_data["tests"] == []

    def test_standardize_labs_mixed_builds_and_tests(self):
        """Test with a mix of automatic and real labs/runtimes."""
        input_data = {
            "builds": [
                {"misc": {"lab": "shell"}},
                {"misc": {"lab": "collabora"}},
                {"misc": {"lab": "k8s-cluster"}},
            ],
            "tests": [
                {"misc": {"runtime": "shell"}},
                {"misc": {"runtime": "lava-lab"}},
                {"misc": {"runtime": "k8s"}},
            ],
        }

        standardize_labs(input_data)

        # Build 0: shell -> automatic_lab
        assert "lab" not in input_data["builds"][0]["misc"]
        assert input_data["builds"][0]["misc"][AUTOMATIC_LAB_FIELD] == "shell"

        # Build 1: real lab stays
        assert input_data["builds"][1]["misc"]["lab"] == "collabora"
        assert AUTOMATIC_LAB_FIELD not in input_data["builds"][1]["misc"]

        # Build 2: k8s* -> automatic_lab
        assert "lab" not in input_data["builds"][2]["misc"]
        assert input_data["builds"][2]["misc"][AUTOMATIC_LAB_FIELD] == "k8s-cluster"

        # Test 0: shell -> automatic_lab
        assert "runtime" not in input_data["tests"][0]["misc"]
        assert input_data["tests"][0]["misc"][AUTOMATIC_LAB_FIELD] == "shell"

        # Test 1: real runtime stays
        assert input_data["tests"][1]["misc"]["runtime"] == "lava-lab"
        assert AUTOMATIC_LAB_FIELD not in input_data["tests"][1]["misc"]

        # Test 2: k8s -> automatic_lab
        assert "runtime" not in input_data["tests"][2]["misc"]
        assert input_data["tests"][2]["misc"][AUTOMATIC_LAB_FIELD] == "k8s"


class TestPrepareFileData:
    """Test cases for prepare_file_data function."""

    # Test cases:
    # - empty file
    # - successful execution
    # - file error

    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.VERBOSE", True)
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.logger")
    @patch("os.remove")
    def test_prepare_file_data_empty_file(self, mock_remove, mock_logger):
        """Test prepare_file_data with empty file."""
        mock_file = SubmissionFileMetadata(
            name=SUBMISSION_FILENAME_MOCK,
            path=SUBMISSION_PATH_MOCK,
            size=0,
        )
        tree_names = {}

        result_data, result_metadata = prepare_file_data(mock_file, tree_names)

        assert result_data is None
        assert result_metadata is None
        mock_remove.assert_called_once_with(SUBMISSION_PATH_MOCK)
        mock_logger.info.assert_called_once_with(
            "File %s is empty, skipping, deleting", SUBMISSION_PATH_MOCK
        )

    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.CONVERT_LOG_EXCERPT",
        True,
    )
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.VERBOSE", False)
    @patch("kcidb_io.schema.V5_3.validate")
    @patch("kcidb_io.schema.V5_3.upgrade")
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.standardize_labs")
    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.standardize_tree_names"
    )
    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.extract_log_excerpt"
    )
    @patch("builtins.open", new_callable=mock_open, read_data=SUBMISSION_FILE_MOCK)
    @patch("time.time", side_effect=TIME_MOCK)
    def test_prepare_file_data_success(
        self,
        mock_time,
        mock_file_open,
        mock_extract_log,
        mock_standardize_tree,
        mock_standardize_labs,
        mock_upgrade,
        mock_validate,
    ):
        """Test successful file preparation."""
        mock_file = SubmissionFileMetadata(
            name=SUBMISSION_FILENAME_MOCK,
            path=SUBMISSION_PATH_MOCK,
            size=100,
        )
        tree_names = {"url": "name"}

        result_data, result_metadata = prepare_file_data(mock_file, tree_names)

        expected_data = SUBMISSION_FILE_DATA_MOCK

        assert result_data == expected_data
        assert result_metadata["fsize"] == 100
        assert result_metadata["processing_time"] == 1
        assert mock_time.call_count == 2
        mock_extract_log.assert_called_once_with(expected_data)
        mock_standardize_tree.assert_called_once_with(expected_data, tree_names)
        mock_validate.assert_called_once()
        mock_upgrade.assert_called_once()
        mock_standardize_labs.assert_called_once_with(expected_data)
        mock_file_open.assert_called_once_with(SUBMISSION_PATH_MOCK, "r")

    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.logger")
    @patch("builtins.open", side_effect=FileNotFoundError("File not found"))
    def test_prepare_file_data_file_error(self, mock_file_open, mock_logger):
        """Test prepare_file_data with file read error."""
        mock_file = SubmissionFileMetadata(
            name=SUBMISSION_FILENAME_MOCK,
            path=SUBMISSION_PATH_MOCK,
            size=100,
        )
        tree_names = {}

        result_data, result_metadata = prepare_file_data(mock_file, tree_names)

        assert result_data is None
        assert "error" in result_metadata
        mock_logger.error.assert_called()
        mock_file_open.assert_called_once()


class TestConsumeBuffer:
    """Test cases for consume_buffer function."""

    # Test cases:
    # - buffer with items
    # - empty buffer
    # - trying to insert in an invalid table

    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.INGEST_BATCH_SIZE",
        INGEST_BATCH_SIZE_MOCK,
    )
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.out")
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.connections")
    @patch("time.time", side_effect=TIME_MOCK)
    def test_consume_buffer_with_items(self, mock_time, mock_connections, mock_out):
        """Test consume_buffer with items in buffer."""
        table_name = "issues"
        # TODO: test with a real example
        mock_buffer = [MagicMock(), MagicMock()]
        mock_cursor = MagicMock()
        mock_connections["default"].cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        consume_buffer(mock_buffer, table_name)

        assert mock_time.call_count == 2
        mock_cursor.executemany.assert_called_once()
        mock_out.assert_called_once()

    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.out")
    @patch("time.time")
    def test_consume_buffer_empty_buffer(self, mock_time, mock_out):
        """Test consume_buffer with empty buffer."""
        mock_model = MagicMock()

        consume_buffer([], "issues")

        mock_model.objects.bulk_create.assert_not_called()
        mock_time.assert_not_called()
        mock_out.assert_not_called()

    def test_consume_buffer_wrong_table(self):
        """Test consume_buffer with invalid table name raises KeyError."""
        with pytest.raises(KeyError):
            mock_model = MagicMock()
            consume_buffer([mock_model], "another")


class TestFlushBuffers:
    """Test cases for flush_buffers function."""

    # Test cases:
    # - nothing to flush
    # - insertion success
    # - insertion error

    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.consume_buffer")
    @patch("os.rename")
    def test_flush_buffers_empty_buffers(self, mock_rename, mock_consume):
        """Test flush_buffers with all empty buffers."""
        flush_buffers(
            issues_buf=[],
            checkouts_buf=[],
            builds_buf=[],
            tests_buf=[],
            incidents_buf=[],
            buffer_files={},
            dirs=SUBMISSION_DIRS_MOCK,
            stat_ok=MagicMock(),
            stat_fail=MagicMock(),
            counter_lock=MagicMock(),
        )

        mock_consume.assert_not_called()
        mock_rename.assert_not_called()

    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.aggregate_checkouts_and_pendings"
    )
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.out")
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.consume_buffer")
    @patch("os.rename")
    @patch("django.db.transaction.atomic")
    @patch("time.time", side_effect=TIME_MOCK)
    def test_flush_buffers_with_items(
        self,
        mock_time,
        mock_atomic,
        mock_rename,
        mock_consume,
        mock_out,
        mock_aggregate,
    ):
        """Test flush_buffers with items in buffers."""
        # Arbitrary amount of items in each buffer
        issues_buf = [MagicMock()]
        checkouts_buf = [MagicMock(), MagicMock()]
        builds_buf = []
        tests_buf = [MagicMock()]
        incidents_buf = []
        buffer_files = {(SUBMISSION_FILENAME_MOCK, SUBMISSION_FILEPATH_MOCK)}

        stat_ok = MagicMock()
        stat_ok.value = 0
        stat_fail = MagicMock()
        stat_fail.value = 0
        counter_lock = MagicMock()

        n_issues = len(issues_buf)
        n_checkouts = len(checkouts_buf)
        n_builds = len(builds_buf)
        n_tests = len(tests_buf)
        n_incidents = len(incidents_buf)
        total_items = n_issues + n_checkouts + n_builds + n_tests + n_incidents

        flush_buffers(
            issues_buf=issues_buf,
            checkouts_buf=checkouts_buf,
            builds_buf=builds_buf,
            tests_buf=tests_buf,
            incidents_buf=incidents_buf,
            buffer_files=buffer_files,
            dirs=SUBMISSION_DIRS_MOCK,
            stat_ok=stat_ok,
            stat_fail=stat_fail,
            counter_lock=counter_lock,
        )

        expected_calls = [
            call(issues_buf, "issues"),
            call(checkouts_buf, "checkouts"),
            call(builds_buf, "builds"),
            call(tests_buf, "tests"),
            call(incidents_buf, "incidents"),
        ]
        mock_consume.assert_has_calls(expected_calls)

        # Verify stat_ok update
        # counter_lock enter/exit called
        assert counter_lock.__enter__.call_count >= 1

        # Inside of the function the `out` is called before the clear
        # So we check against the len of the original buffers
        mock_out.assert_called_once_with(
            "Flushed batch in %.3fs (%.1f items/s): "
            "issues=%d checkouts=%d builds=%d tests=%d incidents=%d"
            % (
                1,
                total_items,
                n_issues,
                n_checkouts,
                n_builds,
                n_tests,
                n_incidents,
            )
        )

        assert len(issues_buf) == 0
        assert len(checkouts_buf) == 0
        assert len(builds_buf) == 0
        assert len(tests_buf) == 0
        assert len(incidents_buf) == 0
        assert len(buffer_files) == 0

        mock_rename.assert_called_once_with(
            SUBMISSION_FILEPATH_MOCK,
            "/".join([ARCHIVE_SUBMISSIONS_DIR, SUBMISSION_FILENAME_MOCK]),
        )

        assert mock_time.call_count == 2
        mock_atomic.assert_called_once()
        mock_aggregate.assert_called_once_with(
            checkouts_instances=checkouts_buf,
            tests_instances=tests_buf,
            build_instances=builds_buf,
        )

    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.aggregate_checkouts_and_pendings"
    )
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.logger")
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.out")
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.consume_buffer")
    @patch("os.rename")
    @patch("django.db.transaction.atomic")
    @patch("time.time", side_effect=TIME_MOCK)
    def test_flush_buffers_with_db_error(
        self,
        mock_time,
        mock_atomic,
        mock_rename,
        mock_consume,
        mock_out,
        mock_logger,
        mock_aggregate,
    ):
        """Test flush_buffers with a database error (insertion error or any other)."""
        # Arbitrary amount of items in each buffer
        issues_buf = []
        checkouts_buf = [MagicMock()]
        builds_buf = [MagicMock(), MagicMock()]
        tests_buf = []
        incidents_buf = [MagicMock()]
        buffer_files = {(SUBMISSION_FILENAME_MOCK, SUBMISSION_FILEPATH_MOCK)}

        n_issues = len(issues_buf)
        n_checkouts = len(checkouts_buf)
        n_builds = len(builds_buf)
        n_tests = len(tests_buf)
        n_incidents = len(incidents_buf)
        total_items = n_issues + n_checkouts + n_builds + n_tests + n_incidents
        n_files = len(buffer_files)

        mock_consume.side_effect = Exception("Database error")

        stat_ok = MagicMock()
        stat_fail = MagicMock()
        counter_lock = MagicMock()

        flush_buffers(
            issues_buf=issues_buf,
            checkouts_buf=checkouts_buf,
            builds_buf=builds_buf,
            tests_buf=tests_buf,
            incidents_buf=incidents_buf,
            buffer_files=buffer_files,
            dirs=SUBMISSION_DIRS_MOCK,
            stat_ok=stat_ok,
            stat_fail=stat_fail,
            counter_lock=counter_lock,
        )

        # Doesn't expect to consume all buffers since the first one raises error and skips the rest
        mock_consume.assert_called_once_with(issues_buf, "issues")

        # Inside of the function the `out` is called before the clear
        # So we check against the len of the original buffers
        mock_out.assert_has_calls(
            [
                call("Moved %s files to pending retry directory" % n_files),
                call(
                    "Flushed batch in %.3fs (%.1f items/s): "
                    "issues=%d checkouts=%d builds=%d tests=%d incidents=%d"
                    % (
                        1,
                        total_items,
                        n_issues,
                        n_checkouts,
                        n_builds,
                        n_tests,
                        n_incidents,
                    )
                ),
            ]
        )

        assert len(issues_buf) == 0
        assert len(checkouts_buf) == 0
        assert len(builds_buf) == 0
        assert len(tests_buf) == 0
        assert len(incidents_buf) == 0
        assert len(buffer_files) == 0

        mock_rename.assert_called_once_with(
            SUBMISSION_FILEPATH_MOCK,
            "/".join([SUBMISSION_DIRS_MOCK["failed"], SUBMISSION_FILENAME_MOCK]),
        )

        assert mock_time.call_count == 2
        mock_atomic.assert_called_once()
        mock_logger.error.assert_called_once_with(
            "Error during buffer flush: %s", mock_consume.side_effect
        )
        mock_aggregate.assert_not_called()


class TestIngestSubmissionsParallel:
    """Test cases for ingest_submissions_parallel function."""

    # Test cases:
    # - successful ingestion

    mock_file1 = MagicMock()
    mock_file1.name = SUBMISSION_FILENAME_MOCK
    mock_file1.stat.return_value.st_size = 1000

    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.out")
    @patch("multiprocessing.Process")
    @patch("multiprocessing.Queue")
    @patch("multiprocessing.Value")
    @patch("time.sleep")
    @patch("time.time", side_effect=TIME_MOCK)
    def test_ingest_submissions_parallel_success(
        self,
        mock_time,
        mock_sleep,
        mock_value,
        mock_queue_cls,
        mock_process,
        mock_out,
    ):
        """Test successful parallel ingestion."""
        mock_queue = MagicMock()
        mock_queue_cls.return_value = mock_queue

        mock_queue.empty.return_value = True
        mock_queue.qsize.return_value = 0

        self.mock_file1.path = SUBMISSION_FILEPATH_MOCK + SUBMISSION_FILENAME_MOCK
        mock_file2 = MagicMock()
        mock_file2.name = "file2.json"
        mock_file2.path = SUBMISSION_FILEPATH_MOCK + "file2.json"
        mock_file2.stat.return_value.st_size = 2000

        json_files = [self.mock_file1, mock_file2]

        mock_ok = MagicMock()
        mock_ok.value = 1
        mock_fail = MagicMock()
        mock_fail.value = 1
        mock_processed = MagicMock()
        mock_processed.value = len(json_files)

        mock_value.side_effect = [mock_ok, mock_fail, mock_processed]

        # Mock the process
        mock_process_instance = MagicMock()
        mock_process.return_value = mock_process_instance

        ingest_submissions_parallel(
            json_files=json_files,
            tree_names={},
            dirs=SUBMISSION_DIRS_MOCK,
            max_workers=2,
        )

        # Verify process was started and joined
        assert mock_process_instance.start.call_count == 2
        assert mock_process_instance.join.call_count == 2

        stat_ok = 1
        stat_fail = 1
        total_elapsed = 1

        total_bytes = (
            self.mock_file1.stat.return_value.st_size
            + mock_file2.stat.return_value.st_size
        )
        mb = total_bytes / (1024 * 1024)

        # We verify only the final call
        mock_out.assert_called_with(
            "Ingest cycle: %d files (ok=%d, fail=%d) in %.2fs | "
            "%.2f files/s | %.2f MB processed (%.2f MB/s)"
            % (
                len(json_files),
                stat_ok,
                stat_fail,
                total_elapsed,
                len(json_files) / total_elapsed,
                mb,
                mb / total_elapsed,
            ),
        )
