import threading
from queue import Queue
from unittest.mock import patch, MagicMock, mock_open, call
from concurrent.futures import Future

from kernelCI_app.tests.unitTests.helpers.fixtures.kcidbng_ingester_data import (
    ARCHIVE_SUBMISSIONS_DIR,
    FAILED_SUBMISSIONS_DIR,
    FLUSH_TIMEOUT_SEC_MOCK,
    INGEST_BATCH_SIZE_MOCK,
    MAINLINE_URL,
    TIME_MOCK,
    TREE_NAMES_MOCK,
    SUBMISSION_PATH_MOCK,
    SUBMISSION_FILE_MOCK,
    SUBMISSION_FILE_DATA_MOCK,
    SUBMISSION_FILENAME_MOCK,
)
import pytest
from queue import Empty

from kernelCI_app.management.commands.helpers.kcidbng_ingester import (
    SubmissionFileMetadata,
    standardize_tree_names,
    prepare_file_data,
    consume_buffer,
    flush_buffers,
    db_worker,
    process_file,
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
        mock_standardize,
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
        mock_standardize.assert_called_once_with(expected_data, tree_names)
        mock_validate.assert_called_once()
        mock_upgrade.assert_called_once()
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
    def test_flush_buffers_empty_buffers(self, mock_consume):
        """Test flush_buffers with all empty buffers."""
        flush_buffers(
            issues_buf=[],
            checkouts_buf=[],
            builds_buf=[],
            tests_buf=[],
            incidents_buf=[],
        )

        mock_consume.assert_not_called()

    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.aggregate_checkouts_and_tests"
    )
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.out")
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.consume_buffer")
    @patch("django.db.transaction.atomic")
    @patch("time.time", side_effect=TIME_MOCK)
    def test_flush_buffers_with_items(
        self, mock_time, mock_atomic, mock_consume, mock_out, mock_aggregate
    ):
        """Test flush_buffers with items in buffers."""
        # Arbitrary amount of items in each buffer
        issues_buf = [MagicMock()]
        checkouts_buf = [MagicMock(), MagicMock()]
        builds_buf = []
        tests_buf = [MagicMock()]
        incidents_buf = []

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
        )

        expected_calls = [
            call(issues_buf, "issues"),
            call(checkouts_buf, "checkouts"),
            call(builds_buf, "builds"),
            call(tests_buf, "tests"),
            call(incidents_buf, "incidents"),
        ]
        mock_consume.assert_has_calls(expected_calls)

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

        assert mock_time.call_count == 2
        mock_atomic.assert_called_once()
        mock_aggregate.assert_called_once_with(
            checkouts_instances=checkouts_buf, tests_instances=tests_buf
        )

    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.aggregate_checkouts_and_tests"
    )
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.logger")
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.out")
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.consume_buffer")
    @patch("django.db.transaction.atomic")
    @patch("time.time", side_effect=TIME_MOCK)
    def test_flush_buffers_with_db_error(
        self,
        mock_time,
        mock_atomic,
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

        n_issues = len(issues_buf)
        n_checkouts = len(checkouts_buf)
        n_builds = len(builds_buf)
        n_tests = len(tests_buf)
        n_incidents = len(incidents_buf)
        total_items = n_issues + n_checkouts + n_builds + n_tests + n_incidents

        mock_consume.side_effect = Exception("Database error")

        flush_buffers(
            issues_buf=issues_buf,
            checkouts_buf=checkouts_buf,
            builds_buf=builds_buf,
            tests_buf=tests_buf,
            incidents_buf=incidents_buf,
        )

        # Doesn't expect to consume all buffers since the first one raises error and skips the rest
        mock_consume.assert_called_once_with(issues_buf, "issues")

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

        assert mock_time.call_count == 2
        mock_atomic.assert_called_once()
        mock_logger.error.assert_called_once_with(
            "Error during buffer flush: %s", mock_consume.side_effect
        )
        mock_aggregate.assert_not_called()


class TestDbWorker:
    """Test cases for db_worker function."""

    # Test cases:
    # - stop event is set (in a real scenario it would be set by another thread)
    # - less items than the limit for flushing
    # - more items than the limit for flushing
    # - time-based flush when idle

    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.flush_buffers")
    @patch("time.time", return_value=1000)
    def test_db_worker_stop_event(self, mock_time, mock_flush):
        """Test db_worker with stop event set."""
        test_queue = Queue()

        stop_event = threading.Event()
        stop_event.set()

        db_worker(stop_event, test_queue)

        assert test_queue.empty()
        assert test_queue.all_tasks_done
        assert mock_time.call_count == 1
        mock_flush.assert_called_once()

    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.flush_buffers")
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.VERBOSE", False)
    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.INGEST_BATCH_SIZE",
        10,
    )
    @patch("time.time", return_value=1000)
    def test_db_worker_with_item_then_none(self, mock_time, mock_flush):
        """Test db_worker processes one item and then stops with None poison pill."""
        test_queue = Queue()
        stop_event = threading.Event()

        mock_instances = {
            "issues": [MagicMock()],
            "checkouts": [MagicMock(), MagicMock()],
            "builds": [],
            "tests": [MagicMock()],
            "incidents": [],
        }
        test_queue.put((SUBMISSION_FILENAME_MOCK, mock_instances))
        test_queue.put(None)

        db_worker(stop_event, test_queue)

        assert test_queue.empty()
        assert mock_time.call_count == 1

        # The only flush is the last one after receiving None
        mock_flush.assert_called_once()

    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.flush_buffers")
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.out")
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.VERBOSE", True)
    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.INGEST_BATCH_SIZE", 5
    )
    @patch("time.time", return_value=TIME_MOCK)
    def test_db_worker_flush_on_batch_size_limit(self, mock_time, mock_out, mock_flush):
        """Test db_worker flushes when batch size limit is reached (5 individual items)."""
        test_queue = Queue()
        stop_event = threading.Event()

        mock_instances_1 = {
            "issues": [MagicMock()],
            "checkouts": [MagicMock(), MagicMock()],
            "builds": [],
            "tests": [],
            "incidents": [],
        }
        mock_instances_2 = {
            "issues": [],
            "checkouts": [],
            "builds": [MagicMock()],
            "tests": [MagicMock(), MagicMock()],
            "incidents": [],
        }
        test_queue.put(("test1.json", mock_instances_1))
        test_queue.put(("test2.json", mock_instances_2))
        test_queue.put(None)

        # NOTE: On a normal run, the list of items would be cleared from the flush,
        # meaning that we could add more items before the next flush, but since we're
        # mocking flush_buffers, the lists are not cleared
        db_worker(stop_event, test_queue)

        out_calls = [
            "Queued from test1.json: issues=1 checkouts=2 builds=0 tests=0 incidents=0",
            "Queued from test2.json: issues=0 checkouts=0 builds=1 tests=2 incidents=0",
        ]
        mock_out.assert_has_calls([call(out_calls[0]), call(out_calls[1])])
        assert test_queue.empty()
        # 2 flushes: one after reaching limit, one at the end
        assert mock_flush.call_count == 2
        assert mock_time.call_count == 2

    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.flush_buffers")
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.VERBOSE", True)
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.out")
    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.INGEST_FLUSH_TIMEOUT_SEC",
        FLUSH_TIMEOUT_SEC_MOCK,
    )
    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.INGEST_BATCH_SIZE",
        10,
    )
    @patch("time.time", side_effect=TIME_MOCK)
    def test_db_worker_time_based_flush(self, mock_time, mock_out, mock_flush):
        """Test db_worker triggers flush after timeout when idle."""
        stop_event = threading.Event()

        mock_instances = {
            "issues": [MagicMock()],
            "checkouts": [],
            "builds": [],
            "tests": [],
            "incidents": [],
        }
        n_issues_submission = len(mock_instances["issues"])
        n_checkouts_submission = len(mock_instances["checkouts"])
        n_builds_submission = len(mock_instances["builds"])
        n_tests_submission = len(mock_instances["tests"])
        n_incidents_submission = len(mock_instances["incidents"])
        total_items_submission = (
            n_issues_submission
            + n_checkouts_submission
            + n_builds_submission
            + n_tests_submission
            + n_incidents_submission
        )

        # Mock the queue.get() to return the item, then Empty exception, then None (poison pill)
        # The poison pill is needed otherwise the worker would run indefinitely
        mock_queue = MagicMock()
        mock_queue.get.side_effect = [
            (SUBMISSION_FILENAME_MOCK, mock_instances),
            Empty(),
            None,
        ]

        db_worker(stop_event, mock_queue)

        # 2 flushes: one after timeout, one at the end
        assert mock_flush.call_count == 2
        assert mock_time.call_count == 3

        out_calls = [
            "Queued from %s: "
            "issues=%d checkouts=%d builds=%d tests=%d incidents=%d"
            % (
                SUBMISSION_FILENAME_MOCK,
                n_issues_submission,
                n_checkouts_submission,
                n_builds_submission,
                n_tests_submission,
                n_incidents_submission,
            ),
            "Idle flush after %.1fs without new items (buffered=%d)"
            % (FLUSH_TIMEOUT_SEC_MOCK, total_items_submission),
        ]
        mock_out.assert_has_calls([call(out_calls[0]), call(out_calls[1])])


class TestProcessFile:
    """Test cases for process_file function."""

    # Test cases:
    # - error in metadata with successful move to failed dir
    # - error in metadata with exception when moving to failed dir
    # - no error but empty data
    # - error when archiving file
    # - process successfully

    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.move_file_to_failed_dir"
    )
    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.prepare_file_data"
    )
    def test_process_file_move_to_failed_dir(self, mock_prepare, mock_move_failed):
        """Test process_file with failed submission and correct move to failed dir."""
        mock_file = SubmissionFileMetadata(
            name=SUBMISSION_FILENAME_MOCK,
            path=SUBMISSION_PATH_MOCK,
            size=100,
        )

        mock_metadata = {"file": mock_file, "error": "Any error"}
        mock_prepare.return_value = (None, mock_metadata)

        test_queue = Queue()
        result = process_file(
            mock_file, {}, FAILED_SUBMISSIONS_DIR, ARCHIVE_SUBMISSIONS_DIR, test_queue
        )

        assert result is False
        mock_move_failed.assert_called_once()

    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.move_file_to_failed_dir",
    )
    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.prepare_file_data"
    )
    def test_process_file_prepare_error_with_move_exception(
        self, mock_prepare, mock_move_failed
    ):
        """Test process_file with failed submission and exception when moving to failed dir."""
        mock_file = SubmissionFileMetadata(
            name=SUBMISSION_FILENAME_MOCK,
            path=SUBMISSION_PATH_MOCK,
            size=100,
        )

        mock_metadata = {"file": mock_file, "error": "Any error"}
        mock_prepare.return_value = (None, mock_metadata)

        mock_move_failed.side_effect = Exception("Any Exception error")

        test_queue = Queue()
        result = process_file(
            mock_file, {}, FAILED_SUBMISSIONS_DIR, ARCHIVE_SUBMISSIONS_DIR, test_queue
        )

        # Same asserts as before because currently Exceptions are not treated
        assert result is False
        mock_move_failed.assert_called_once()

    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.move_file_to_failed_dir",
    )
    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.prepare_file_data"
    )
    def test_process_file_empty_file(self, mock_prepare, mock_move_failed):
        """Test process_file with empty file (already deleted)."""
        mock_file = SubmissionFileMetadata(
            name=SUBMISSION_FILENAME_MOCK,
            path=SUBMISSION_PATH_MOCK,
            size=0,
        )
        mock_metadata = {}
        mock_prepare.return_value = (None, mock_metadata)

        test_queue = Queue()
        result = process_file(
            mock_file, {}, FAILED_SUBMISSIONS_DIR, ARCHIVE_SUBMISSIONS_DIR, test_queue
        )

        assert result is True
        mock_move_failed.assert_not_called()

    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.logger")
    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.build_instances_from_submission"
    )
    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.prepare_file_data"
    )
    @patch("os.rename")
    def test_process_file_archive_error(
        self, mock_rename, mock_prepare, mock_build_instances, mock_logger
    ):
        """Test process_file with archiving error."""
        mock_file = SubmissionFileMetadata(
            name=SUBMISSION_FILENAME_MOCK,
            path=SUBMISSION_PATH_MOCK,
            fsize=100,
        )

        mock_metadata = {"file": mock_file, "fsize": 100}
        mock_prepare.return_value = (mock_file, mock_metadata)

        mock_instances_from_submission = {
            "issues": [],
            "checkouts": [],
            "builds": [],
            "tests": [],
            "incidents": [],
        }
        mock_build_instances.return_value = mock_instances_from_submission

        mock_rename.side_effect = Exception("Any Exception error, usually OSError")

        test_queue = Queue()
        result = process_file(
            mock_file,
            {},
            FAILED_SUBMISSIONS_DIR,
            ARCHIVE_SUBMISSIONS_DIR,
            test_queue,
        )

        assert result is False
        mock_logger.error.assert_called_once_with(
            "Error archiving file %s: %s", mock_file["name"], mock_rename.side_effect
        )

    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.build_instances_from_submission"
    )
    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.prepare_file_data"
    )
    @patch("os.rename")
    def test_process_file_success(
        self, mock_rename, mock_prepare, mock_build_instances
    ):
        """Test successful file processing."""
        mock_file = SubmissionFileMetadata(
            name=SUBMISSION_FILENAME_MOCK,
            path=SUBMISSION_PATH_MOCK,
            fsize=100,
        )

        mock_metadata = {"file": mock_file, "fsize": 100}
        mock_prepare.return_value = (mock_file, mock_metadata)

        mock_instances_from_submission = {
            "issues": [MagicMock()],
            "checkouts": [],
            "builds": [],
            "tests": [MagicMock()],
            "incidents": [],
        }
        mock_build_instances.return_value = mock_instances_from_submission

        test_queue = Queue()
        result = process_file(
            mock_file, {}, FAILED_SUBMISSIONS_DIR, ARCHIVE_SUBMISSIONS_DIR, test_queue
        )

        assert result is True
        mock_rename.assert_called_once_with(
            mock_file["path"], ARCHIVE_SUBMISSIONS_DIR + "/" + mock_file["name"]
        )

        # Check that item was queued
        assert not test_queue.empty()
        queued_item = test_queue.get()
        assert queued_item == (mock_file["name"], mock_instances_from_submission)


class TestIngestSubmissionsParallel:
    """Test cases for ingest_submissions_parallel function."""

    # Test cases:
    # - successful ingestion
    # - processing exception
    # - KeyboardInterrupt during ingestion

    mock_file1 = MagicMock()
    mock_file1.name = SUBMISSION_FILENAME_MOCK
    mock_file1.stat.return_value.st_size = 1000

    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.out")
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.as_completed")
    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.ProcessPoolExecutor"
    )
    @patch("multiprocessing.Process")
    @patch("time.time", side_effect=TIME_MOCK)
    def test_ingest_submissions_parallel_success(
        self,
        mock_time,
        mock_process,
        mock_executor,
        mock_as_completed,
        mock_out,
    ):
        """Test successful parallel ingestion."""
        # Mock files and related data
        mock_file2 = MagicMock()
        mock_file2.name = "file2.json"
        mock_file2.stat.return_value.st_size = 2000

        json_files = [self.mock_file1, mock_file2]

        # Mock the process
        mock_process_instance = MagicMock()
        mock_process.return_value = mock_process_instance

        # Mock the futures and executor
        future1 = Future()
        future1.set_result(True)

        future2 = Future()
        future2.set_result(False)

        # Since we are using `with` in the function, we have to mock the ThreadPoolExecutor CLASS itself
        # After that, the class will call the __enter__ function and will return something else, so we
        # also have to mock that something else as the mock_executor_instance.
        # Then the instance will call a method (submit), so we need to mock that return too.
        mock_executor_instance = MagicMock()
        mock_executor_instance.submit.side_effect = [future1, future2]
        mock_executor.return_value.__enter__.return_value = mock_executor_instance

        # Since as_completed is a separate function, we also have to mock its behavior, and make it return
        # the futures that were set here, so that we can also control the return value of the future and
        # match it with the executor which will construct the `future_to_file` dict
        mock_as_completed.return_value = [future1, future2]

        ingest_submissions_parallel(
            json_files=json_files,
            tree_names={},
            archive_dir=ARCHIVE_SUBMISSIONS_DIR,
            failed_dir=FAILED_SUBMISSIONS_DIR,
            max_workers=2,
        )

        assert mock_time.call_count == 4

        # Verify thread was started and joined
        mock_process_instance.start.assert_called_once()
        mock_process_instance.join.assert_called_once()

        # Verify output messages
        stat_ok = 1
        stat_fail = 1
        total_processed_files = stat_ok + stat_fail
        total_elapsed = 3
        total_bytes = (
            self.mock_file1.stat.return_value.st_size
            + mock_file2.stat.return_value.st_size
        )
        mb = total_bytes / (1024 * 1024)

        # Only asserts the number and the last message in order to avoid race condition
        assert mock_out.call_count == 4
        mock_out.assert_called_with(
            "Ingest cycle: %d files (ok=%d, fail=%d) in %.2fs | "
            "%.2f files/s | %.2f MB processed (%.2f MB/s)"
            % (
                total_processed_files,
                stat_ok,
                stat_fail,
                total_elapsed,
                total_processed_files / total_elapsed,
                mb,
                mb / total_elapsed,
            ),
        )

    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.out")
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.as_completed")
    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.ProcessPoolExecutor"
    )
    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.logger")
    @patch("multiprocessing.Process")
    @patch("time.time", side_effect=TIME_MOCK)
    def test_ingest_submissions_parallel_processing_exception(
        self,
        mock_time,
        mock_process,
        mock_logger,
        mock_executor,
        mock_as_completed,
        mock_out,
    ):
        """Test ingestion with processing exception."""
        # Mock the thread
        mock_process_instance = MagicMock()
        mock_process.return_value = mock_process_instance

        # Mock the futures and executor
        future_result = Exception("Processing error")
        future1 = MagicMock()
        # Use side_effect to make result() raise the exception
        future1.result.side_effect = future_result

        mock_executor_instance = MagicMock()
        mock_executor_instance.submit.side_effect = [future1]
        mock_executor.return_value.__enter__.return_value = mock_executor_instance

        mock_as_completed.return_value = [future1]

        ingest_submissions_parallel(
            json_files=[self.mock_file1],
            tree_names={},
            archive_dir=ARCHIVE_SUBMISSIONS_DIR,
            failed_dir=FAILED_SUBMISSIONS_DIR,
            max_workers=2,
        )

        mock_logger.error.assert_called_once_with(
            "Exception processing %s: %s", self.mock_file1.name, future_result
        )

        assert mock_time.call_count == 3

        # Verify thread was started and joined
        mock_process_instance.start.assert_called_once()
        mock_process_instance.join.assert_called_once()

        # Verify output messages
        stat_ok = 0
        stat_fail = 1
        total_processed_files = stat_ok + stat_fail
        total_elapsed = 2
        total_bytes = self.mock_file1.stat.return_value.st_size
        mb = total_bytes / (1024 * 1024)

        # Only asserts the number and the last message in order to avoid race condition
        assert mock_out.call_count == 3
        mock_out.assert_called_with(
            "Ingest cycle: %d files (ok=%d, fail=%d) in %.2fs | "
            "%.2f files/s | %.2f MB processed (%.2f MB/s)"
            % (
                total_processed_files,
                stat_ok,
                stat_fail,
                total_elapsed,
                total_processed_files / total_elapsed,
                mb,
                mb / total_elapsed,
            ),
        )

    @patch("kernelCI_app.management.commands.helpers.kcidbng_ingester.out")
    @patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.ProcessPoolExecutor"
    )
    @patch("multiprocessing.Process")
    @patch("time.time", side_effect=TIME_MOCK)
    def test_ingest_submissions_keyboard_interruption(
        self,
        mock_time,
        mock_process,
        mock_executor,
        mock_out,
    ):
        """Test parallel ingestion with keyboard interruption."""
        json_files = [self.mock_file1]

        # Mock the thread
        mock_process_instance = MagicMock()
        mock_process.return_value = mock_process_instance

        # Mock executor to raise KeyboardInterrupt on submit
        mock_executor_instance = MagicMock()
        mock_executor_instance.submit.side_effect = KeyboardInterrupt()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance

        with pytest.raises(KeyboardInterrupt):
            ingest_submissions_parallel(
                json_files=json_files,
                tree_names={},
                archive_dir=ARCHIVE_SUBMISSIONS_DIR,
                failed_dir=FAILED_SUBMISSIONS_DIR,
                max_workers=2,
            )

        assert mock_time.call_count == 1

        # Verify thread was started and joined
        mock_process_instance.start.assert_called_once()
        mock_process_instance.join.assert_called_once()

        # Verify output messages
        total_bytes = self.mock_file1.stat.return_value.st_size
        out_calls = [
            "Spool status: %d .json files queued (%.2f MB)"
            % (len(json_files), total_bytes / (1024 * 1024)),
            "KeyboardInterrupt: stopping ingestion and flushing...",
        ]
        mock_out.assert_has_calls([call(c) for c in out_calls])
