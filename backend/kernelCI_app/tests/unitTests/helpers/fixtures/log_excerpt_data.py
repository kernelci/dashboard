UPLOAD_URL_MOCK = "http://test-upload.com"
STORAGE_TOKEN_MOCK = "test-token"
STORAGE_URL_MOCK = "http://test-storage.com"
TMP_TEST_FILE_NAME = "/tmp/test_file"
COMPRESSED_LOGEXCERPT = b"compressed_logexcerpt"
LOG_EXCERPT_MOCK = "Test log excerpt"
EXCERPT_HASH_MOCK = "somehash"
MOCK_CACHE_DICT = {EXCERPT_HASH_MOCK: LOG_EXCERPT_MOCK}

LOG_URL_MOCK = "http://example.com/logexcerpt.txt.gz"

SUBMISSION_MOCK = {
    "builds": [{"id": "build1", "log_excerpt": "test"}, {"id": "build2"}],
    "tests": [{"id": "test1", "log_excerpt": "test"}],
}
