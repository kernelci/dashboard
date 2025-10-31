from unittest.mock import patch, MagicMock, mock_open
from kernelCI_app.management.commands.helpers.log_excerpt_utils import (
    upload_logexcerpt,
    get_from_cache,
    set_in_cache,
    set_log_excerpt_ofile,
    process_log_excerpt_from_item,
    extract_log_excerpt,
    cache_logs_maintenance,
)
from kernelCI_app.tests.unitTests.helpers.fixtures.log_excerpt_data import (
    COMPRESSED_LOGEXCERPT,
    EXCERPT_HASH_MOCK,
    LOG_EXCERPT_MOCK,
    LOG_URL_MOCK,
    MOCK_CACHE_DICT,
    STORAGE_TOKEN_MOCK,
    STORAGE_URL_MOCK,
    SUBMISSION_MOCK,
    TMP_TEST_FILE_NAME,
    UPLOAD_URL_MOCK,
)


class TestUploadLogexcerpt:
    """Test upload_logexcerpt function."""

    # Test cases:
    # - successful upload
    # - couldn't upload log_excerpt

    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.VERBOSE", False)
    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.UPLOAD_URL",
        UPLOAD_URL_MOCK,
    )
    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.STORAGE_TOKEN",
        STORAGE_TOKEN_MOCK,
    )
    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.STORAGE_BASE_URL",
        STORAGE_URL_MOCK,
    )
    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.requests.post")
    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.tempfile.NamedTemporaryFile"
    )
    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.gzip.compress")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.remove")
    def test_upload_logexcerpt_success(
        self, mock_remove, mock_file_open, mock_gzip, mock_temp_file, mock_post
    ):
        """Test successful logexcerpt upload."""
        mock_temp_file_obj = MagicMock()
        mock_temp_file_obj.name = TMP_TEST_FILE_NAME
        mock_temp_file_obj.__enter__.return_value = mock_temp_file_obj
        mock_temp_file_obj.__exit__.return_value = None
        mock_temp_file.return_value = mock_temp_file_obj

        mock_gzip.return_value = COMPRESSED_LOGEXCERPT
        mock_file_open.read_data = COMPRESSED_LOGEXCERPT

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = upload_logexcerpt(LOG_EXCERPT_MOCK, EXCERPT_HASH_MOCK)

        mock_temp_file_obj.write.assert_called_once_with(COMPRESSED_LOGEXCERPT)
        mock_temp_file_obj.flush.assert_called_once()
        mock_gzip.assert_called_once_with(LOG_EXCERPT_MOCK.encode("utf-8"))

        mock_file_open.assert_called_once_with(TMP_TEST_FILE_NAME, "rb")

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "http://test-upload.com"
        assert kwargs["headers"] == {"Authorization": f"Bearer {STORAGE_TOKEN_MOCK}"}

        assert (
            result
            == f"{STORAGE_URL_MOCK}/logexcerpt/{EXCERPT_HASH_MOCK}/logexcerpt.txt.gz"
        )
        assert mock_remove.call_count == 1

    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.UPLOAD_URL",
        UPLOAD_URL_MOCK,
    )
    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.STORAGE_TOKEN",
        STORAGE_TOKEN_MOCK,
    )
    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.requests.post")
    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.tempfile.NamedTemporaryFile"
    )
    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.gzip.compress")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.remove")
    def test_upload_logexcerpt_failed_status_code(
        self, mock_remove, mock_file_open, mock_gzip, mock_temp_file, mock_post
    ):
        """Test logexcerpt upload with failed status code."""
        mock_temp_file_obj = MagicMock()
        mock_temp_file_obj.name = TMP_TEST_FILE_NAME
        mock_temp_file_obj.__enter__.return_value = mock_temp_file_obj
        mock_temp_file_obj.__exit__.return_value = None
        mock_temp_file.return_value = mock_temp_file_obj

        mock_gzip.return_value = COMPRESSED_LOGEXCERPT
        mock_file_open.read_data = COMPRESSED_LOGEXCERPT

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        result = upload_logexcerpt(LOG_EXCERPT_MOCK, EXCERPT_HASH_MOCK)

        assert result == LOG_EXCERPT_MOCK
        assert mock_remove.call_count == 1


class TestGetCache:
    """Test cache-related functions."""

    # Test cases:
    # - get and found cache
    # - get and not found cache

    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.CACHE_LOGS")
    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.cache_logs_lock")
    def test_get_from_cache_existing_key(self, mock_lock, mock_cache):
        """Test getting an existing key from cache."""
        mock_cache.__getitem__.side_effect = MOCK_CACHE_DICT.__getitem__
        mock_cache.get.side_effect = MOCK_CACHE_DICT.get

        mock_lock.__enter__ = MagicMock()
        mock_lock.__exit__ = MagicMock()

        result = get_from_cache(EXCERPT_HASH_MOCK)

        assert result == LOG_EXCERPT_MOCK

    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.CACHE_LOGS")
    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.cache_logs_lock")
    def test_get_from_cache_non_existing_key(self, mock_lock, mock_cache):
        """Test getting a non-existing key from cache."""
        mock_cache.__getitem__.side_effect = MOCK_CACHE_DICT.__getitem__
        mock_cache.get.side_effect = MOCK_CACHE_DICT.get

        mock_lock.__enter__ = MagicMock()
        mock_lock.__exit__ = MagicMock()

        result = get_from_cache("non_existing_hash")

        assert result is None


class TestSetCache:
    """Test set_in_cache function."""

    # Test cases:
    # - set cache successfully
    # - replaces existing cache value successfully

    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.VERBOSE", False)
    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.cache_logs_lock")
    def test_set_in_cache(self, mock_lock):
        """Test setting a value in cache."""
        mock_lock.__enter__ = MagicMock()
        mock_lock.__exit__ = MagicMock()

        test_cache_dict = {}
        with patch(
            "kernelCI_app.management.commands.helpers.log_excerpt_utils.CACHE_LOGS",
            test_cache_dict,
        ):
            set_in_cache(EXCERPT_HASH_MOCK, LOG_EXCERPT_MOCK)

            assert EXCERPT_HASH_MOCK in test_cache_dict
            assert test_cache_dict[EXCERPT_HASH_MOCK] == LOG_EXCERPT_MOCK

    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.VERBOSE", False)
    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.cache_logs_lock")
    def test_set_in_cache_replacing(self, mock_lock):
        """Test setting a value in cache."""
        mock_lock.__enter__ = MagicMock()
        mock_lock.__exit__ = MagicMock()

        test_cache_dict = {EXCERPT_HASH_MOCK: "old_value"}
        with patch(
            "kernelCI_app.management.commands.helpers.log_excerpt_utils.CACHE_LOGS",
            test_cache_dict,
        ):
            set_in_cache(EXCERPT_HASH_MOCK, LOG_EXCERPT_MOCK)

            assert test_cache_dict[EXCERPT_HASH_MOCK] == LOG_EXCERPT_MOCK


class TestSetLogExcerptOfile:
    """Test set_log_excerpt_ofile function."""

    # Test cases:
    # - set log_excerpt with no existing output_files
    # - set log_excerpt with existing output_files

    def test_set_log_excerpt_ofile_new_output_files(self):
        """Test setting log excerpt with no existing output_files."""

        result = set_log_excerpt_ofile(
            {
                "id": "test_build_123",
                "log_excerpt": "Original log excerpt to be replaced",
            },
            LOG_URL_MOCK,
        )

        assert result["log_excerpt"] is None
        assert "output_files" in result
        assert len(result["output_files"]) == 1
        assert result["output_files"][0] == {"name": "log_excerpt", "url": LOG_URL_MOCK}

    def test_set_log_excerpt_ofile_existing_output_files(self):
        """Test setting log excerpt with existing output_files."""

        result = set_log_excerpt_ofile(
            {
                "id": "test_build_456",
                "log_excerpt": "Original log excerpt to be replaced",
                "output_files": [
                    {"name": "existing_file", "url": "http://example.com/existing.txt"}
                ],
            },
            LOG_URL_MOCK,
        )

        assert result["log_excerpt"] is None
        assert len(result["output_files"]) == 2
        assert result["output_files"][1] == {"name": "log_excerpt", "url": LOG_URL_MOCK}


class TestProcessLogExcerptFromItem:
    """Test process_log_excerpt_from_item function."""

    # Test cases:
    # - small log excerpt (no processing)
    # - large log excerpt with cache
    # - large log excerpt without cache

    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.LOGEXCERPT_THRESHOLD",
        100,
    )
    def test_process_log_excerpt_small_not_processed(self):
        """Test processing small log excerpt that doesn't exceed threshold."""
        item = {"id": "test_build_789", "log_excerpt": "Short log"}
        original_item = item.copy()

        process_log_excerpt_from_item(item, "build")

        assert item == original_item

    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.LOGEXCERPT_THRESHOLD",
        10,
    )
    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.VERBOSE", False)
    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.get_from_cache",
    )
    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.set_in_cache",
    )
    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.set_log_excerpt_ofile",
    )
    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.upload_logexcerpt",
    )
    def test_process_log_excerpt_large_not_cached(
        self,
        mock_upload_logexcerpt,
        mock_set_log_excerpt_ofile,
        mock_set_in_cache,
        mock_get_from_cache,
    ):
        """Test processing large log excerpt not in cache."""

        def side_effect_set_log_excerpt_ofile(item, url):
            item["log_excerpt"] = None
            if "output_files" not in item or not isinstance(item["output_files"], list):
                item["output_files"] = []
            item["output_files"].append({"name": "log_excerpt", "url": url})

        mock_set_log_excerpt_ofile.side_effect = side_effect_set_log_excerpt_ofile

        mock_get_from_cache.return_value = None
        mock_upload_logexcerpt.return_value = "http://example.com/logexcerpt.txt.gz"

        item = {
            "id": "test_build_123",
            "log_excerpt": "Very long log excerpt that exceeds threshold",
        }

        process_log_excerpt_from_item(item, "build")

        mock_upload_logexcerpt.assert_called_once()
        mock_set_in_cache.assert_called_once()
        mock_set_log_excerpt_ofile.assert_called_once()
        assert item["log_excerpt"] is None
        assert "output_files" in item
        assert len(item["output_files"]) == 1

    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.LOGEXCERPT_THRESHOLD",
        10,
    )
    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.VERBOSE", False)
    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.get_from_cache",
    )
    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.set_in_cache",
    )
    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.set_log_excerpt_ofile",
    )
    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.upload_logexcerpt",
    )
    def test_process_log_excerpt_large_cached(
        self,
        mock_upload_logexcerpt,
        mock_set_log_excerpt_ofile,
        mock_set_in_cache,
        mock_get_from_cache,
    ):
        """Test processing large log excerpt already in cache."""

        def side_effect_set_log_excerpt_ofile(item, url):
            item["log_excerpt"] = None
            if "output_files" not in item or not isinstance(item["output_files"], list):
                item["output_files"] = []
            item["output_files"].append({"name": "log_excerpt", "url": url})

        mock_set_log_excerpt_ofile.side_effect = side_effect_set_log_excerpt_ofile

        mock_get_from_cache.return_value = LOG_URL_MOCK

        item = {
            "id": "test_build_456",
            "log_excerpt": "This is a very long log excerpt that exceeds threshold",
        }

        process_log_excerpt_from_item(item, "test")

        mock_upload_logexcerpt.assert_not_called()
        mock_set_in_cache.assert_not_called()
        mock_set_log_excerpt_ofile.assert_called_once()
        assert item["log_excerpt"] is None
        assert "output_files" in item
        assert len(item["output_files"]) == 1


class TestExtractLogExcerpt:
    """Test extract_log_excerpt function."""

    # Test cases:
    # - without storage token
    # - with builds and tests
    # - with none
    # - with empty builds/tests

    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.STORAGE_TOKEN", None
    )
    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.logger")
    def test_extract_log_excerpt_no_storage_token(self, mock_logger):
        """Test extract_log_excerpt without storage token."""
        extract_log_excerpt(SUBMISSION_MOCK)

        mock_logger.warning.assert_called_once_with(
            "STORAGE_TOKEN is not set, log_excerpts will not be uploaded"
        )

    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.STORAGE_TOKEN",
        STORAGE_TOKEN_MOCK,
    )
    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.process_log_excerpt_from_item"
    )
    def test_extract_log_excerpt_with_builds_and_tests(self, mock_process):
        """Test extract_log_excerpt with builds and tests."""
        extract_log_excerpt(SUBMISSION_MOCK)

        assert mock_process.call_count == 2
        mock_process.assert_any_call(
            item=SUBMISSION_MOCK["builds"][0], item_type="build"
        )
        mock_process.assert_any_call(item=SUBMISSION_MOCK["tests"][0], item_type="test")

    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.STORAGE_TOKEN",
        STORAGE_TOKEN_MOCK,
    )
    def test_extract_log_excerpt_empty_data(self):
        """Test extract_log_excerpt with empty data."""
        input_data = {}

        extract_log_excerpt(input_data)

    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.STORAGE_TOKEN",
        "test-token",
    )
    def test_extract_log_excerpt_no_builds_or_tests(self):
        """Test extract_log_excerpt with no builds or tests."""
        input_data = {"builds": [], "tests": []}

        extract_log_excerpt(input_data)


class TestCacheLogsMaintenance:
    """Test cache_logs_maintenance function."""

    # Test cases:
    # - if cache size exceeds limit, clear cache
    # - if cache size under limit, do nothing

    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.CACHE_LOGS_SIZE_LIMIT",
        3,
    )
    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.VERBOSE", True)
    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.CACHE_LOGS")
    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.cache_logs_lock")
    def test_cache_logs_maintenance_clear_when_over_limit(self, mock_lock, mock_cache):
        """Test cache maintenance clears cache when over limit."""
        mock_cache.__len__.return_value = 5
        mock_lock.__enter__ = MagicMock()
        mock_lock.__exit__ = MagicMock()

        cache_logs_maintenance()

        mock_cache.clear.assert_called_once()

    @patch(
        "kernelCI_app.management.commands.helpers.log_excerpt_utils.CACHE_LOGS_SIZE_LIMIT",
        10,
    )
    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.VERBOSE", False)
    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.CACHE_LOGS")
    @patch("kernelCI_app.management.commands.helpers.log_excerpt_utils.cache_logs_lock")
    def test_cache_logs_maintenance_no_clear_when_under_limit(
        self, mock_lock, mock_cache
    ):
        """Test cache maintenance doesn't clear cache when under limit."""
        mock_cache.__len__.return_value = 5
        mock_lock.__enter__ = MagicMock()
        mock_lock.__exit__ = MagicMock()

        cache_logs_maintenance()

        mock_cache.clear.assert_not_called()
