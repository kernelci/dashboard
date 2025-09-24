from kernelCI_app.typeModels.common import (
    StatusCount,
    GroupedStatus,
    make_default_validator,
)


class TestStatusCount:
    """Test cases for StatusCount class."""

    def test_status_count_increment_valid(self):
        """Test StatusCount increment with valid status."""
        status = StatusCount()
        status.increment("PASS")
        assert status.PASS == 1

    def test_status_count_increment_none(self):
        """Test StatusCount increment with None status."""
        status = StatusCount()
        status.increment(None)
        assert status.NULL == 1

    def test_status_count_increment_unknown(self):
        """Test StatusCount increment with unknown status."""
        status = StatusCount()
        status.increment("UNKNOWN_STATUS")
        # Should not raise exception, just log the error
        assert status.PASS == 0
        assert status.ERROR == 0
        assert status.FAIL == 0
        assert status.SKIP == 0
        assert status.MISS == 0
        assert status.DONE == 0
        assert status.NULL == 0

    def test_status_count_addition(self):
        """Test StatusCount addition."""
        status1 = StatusCount(PASS=5, FAIL=1)
        status2 = StatusCount(PASS=3, ERROR=2)

        result = status1 + status2

        assert result.PASS == 8
        assert result.FAIL == 1
        assert result.ERROR == 2


class TestGroupedStatus:
    """Test cases for GroupedStatus."""

    def test_grouped_status_creation(self):
        """Test GroupedStatus creation."""
        grouped = GroupedStatus(success=3, failed=2, inconclusive=1)
        assert grouped["success"] == 3
        assert grouped["failed"] == 2
        assert grouped["inconclusive"] == 1


class TestMakeDefaultValidator:
    """Test cases for make_default_validator function."""

    def test_make_default_validator(self):
        """Test make_default_validator function."""
        validator = make_default_validator("default_value")

        result = validator.func(None)
        assert result == "default_value"

        result = validator.func("actual_value")
        assert result == "actual_value"
