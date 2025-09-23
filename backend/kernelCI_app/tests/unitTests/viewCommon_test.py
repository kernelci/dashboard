from kernelCI_app.viewCommon import (
    _increment_status,
    create_details_build_summary,
)
from kernelCI_app.typeModels.common import StatusCount
from kernelCI_app.typeModels.commonDetails import (
    BaseBuildSummary,
    BuildHistoryItem,
)


def create_test_build_history_item(**kwargs):
    """Helper function to create BuildHistoryItem with default values."""
    defaults = {
        "id": "test_build_id",
        "status": "PASS",
        "config_name": "test_config",
        "architecture": "x86_64",
        "origin": "test_origin",
        "compiler": "gcc",
        "misc": {},
        "config_url": "http://example.com/config",
        "duration": 300,
        "log_url": "http://example.com/log",
        "start_time": "2024-01-15T12:00:00Z",
        "git_repository_url": "https://git.example.com/repo.git",
        "git_repository_branch": "main",
    }
    defaults.update(kwargs)
    return BuildHistoryItem(**defaults)


class TestIncrementStatus:
    def test_increment_status_pass(self):
        """Test incrementing PASS status."""
        status = StatusCount()
        initial_pass = status.PASS

        _increment_status(status, "PASS")

        assert status.PASS == initial_pass + 1

    def test_increment_status_fail(self):
        """Test incrementing FAIL status."""
        status = StatusCount()
        initial_fail = status.FAIL

        _increment_status(status, "FAIL")

        assert status.FAIL == initial_fail + 1

    def test_increment_status_error(self):
        """Test incrementing ERROR status."""
        status = StatusCount()
        initial_error = status.ERROR

        _increment_status(status, "ERROR")

        assert status.ERROR == initial_error + 1

    def test_increment_status_skip(self):
        """Test incrementing SKIP status."""
        status = StatusCount()
        initial_skip = status.SKIP

        _increment_status(status, "SKIP")

        assert status.SKIP == initial_skip + 1

    def test_increment_status_multiple_times(self):
        """Test incrementing the same status multiple times."""
        status = StatusCount()
        initial_pass = status.PASS

        _increment_status(status, "PASS")
        _increment_status(status, "PASS")
        _increment_status(status, "PASS")

        assert status.PASS == initial_pass + 3


class TestCreateDetailsBuildSummary:
    def test_create_details_build_summary_empty_builds(self):
        """Test creating build summary with empty builds list."""
        builds = []

        result = create_details_build_summary(builds)

        assert isinstance(result, BaseBuildSummary)
        assert result.status.PASS == 0
        assert result.status.FAIL == 0
        assert result.configs == {}
        assert result.architectures == {}
        assert result.origins == {}

    def test_create_details_build_summary_single_build(self):
        """Test creating build summary with single build."""
        build = create_test_build_history_item(
            id="build123",
            status="PASS",
            config_name="test_config",
            architecture="x86_64",
            origin="test_origin",
            compiler="gcc",
        )

        result = create_details_build_summary([build])

        assert result.status.PASS == 1
        assert result.status.FAIL == 0
        assert "test_config" in result.configs
        assert result.configs["test_config"].PASS == 1
        assert "x86_64" in result.architectures
        assert result.architectures["x86_64"].PASS == 1
        assert "gcc" in result.architectures["x86_64"].compilers
        assert "test_origin" in result.origins
        assert result.origins["test_origin"].PASS == 1

    def test_create_details_build_summary_multiple_builds(self):
        """Test creating build summary with multiple builds."""
        builds = [
            create_test_build_history_item(
                id="build1",
                status="PASS",
                config_name="config1",
                architecture="x86_64",
                origin="origin1",
                compiler="gcc",
            ),
            create_test_build_history_item(
                id="build2",
                status="FAIL",
                config_name="config1",
                architecture="x86_64",
                origin="origin1",
                compiler="gcc",
            ),
            create_test_build_history_item(
                id="build3",
                status="PASS",
                config_name="config2",
                architecture="arm64",
                origin="origin2",
                compiler="clang",
            ),
        ]

        result = create_details_build_summary(builds)

        assert result.status.PASS == 2
        assert result.status.FAIL == 1
        assert "config1" in result.configs
        assert result.configs["config1"].PASS == 1
        assert result.configs["config1"].FAIL == 1
        assert "config2" in result.configs
        assert result.configs["config2"].PASS == 1
        assert "x86_64" in result.architectures
        assert result.architectures["x86_64"].PASS == 1
        assert result.architectures["x86_64"].FAIL == 1
        assert "gcc" in result.architectures["x86_64"].compilers
        assert "arm64" in result.architectures
        assert result.architectures["arm64"].PASS == 1
        assert "clang" in result.architectures["arm64"].compilers
        assert "origin1" in result.origins
        assert result.origins["origin1"].PASS == 1
        assert result.origins["origin1"].FAIL == 1
        assert "origin2" in result.origins
        assert result.origins["origin2"].PASS == 1

    def test_create_details_build_summary_with_none_values(self):
        """Test creating build summary with None values in builds."""
        builds = [
            create_test_build_history_item(
                id="build_none_fields",
                status="PASS",
                config_name=None,
                architecture=None,
                origin="test_origin",
                compiler=None,
            ),
            create_test_build_history_item(
                id="build_with_fields",
                status="FAIL",
                config_name="config1",
                architecture="x86_64",
                origin="origin1",
                compiler="gcc",
            ),
        ]

        result = create_details_build_summary(builds)
        assert result.status.PASS == 1
        assert result.status.FAIL == 1
        assert "config1" in result.configs
        assert result.configs["config1"].FAIL == 1
        assert "x86_64" in result.architectures
        assert result.architectures["x86_64"].FAIL == 1
        assert "origin1" in result.origins
        assert result.origins["origin1"].FAIL == 1

    def test_create_details_build_summary_compiler_sorting(self):
        """Test that compilers are sorted in architecture summary."""
        builds = [
            create_test_build_history_item(
                id="build_clang",
                status="PASS",
                config_name="config1",
                architecture="x86_64",
                origin="origin1",
                compiler="clang",
            ),
            create_test_build_history_item(
                id="build_gcc",
                status="PASS",
                config_name="config1",
                architecture="x86_64",
                origin="origin1",
                compiler="gcc",
            ),
            create_test_build_history_item(
                id="build_icc",
                status="PASS",
                config_name="config1",
                architecture="x86_64",
                origin="origin1",
                compiler="icc",
            ),
        ]

        result = create_details_build_summary(builds)

        assert "x86_64" in result.architectures
        compilers = result.architectures["x86_64"].compilers
        assert compilers == ["clang", "gcc", "icc"]  # Should be sorted

    def test_create_details_build_summary_duplicate_compilers(self):
        """Test that duplicate compilers are not added multiple times."""
        builds = [
            create_test_build_history_item(
                id="build_gcc_pass",
                status="PASS",
                config_name="config1",
                architecture="x86_64",
                origin="origin1",
                compiler="gcc",
            ),
            create_test_build_history_item(
                id="build_gcc_fail",
                status="FAIL",
                config_name="config1",
                architecture="x86_64",
                origin="origin1",
                compiler="gcc",
            ),
        ]

        result = create_details_build_summary(builds)

        assert "x86_64" in result.architectures
        compilers = result.architectures["x86_64"].compilers
        assert compilers == ["gcc"]  # Should only appear once

    def test_create_details_build_summary_all_status_types(self):
        """Test creating build summary with all status types."""
        builds = [
            create_test_build_history_item(
                id="build_pass",
                status="PASS",
                config_name=None,
                architecture=None,
                origin="test_origin",
                compiler=None,
            ),
            create_test_build_history_item(
                id="build_fail",
                status="FAIL",
                config_name=None,
                architecture=None,
                origin="test_origin",
                compiler=None,
            ),
            create_test_build_history_item(
                id="build_error",
                status="ERROR",
                config_name=None,
                architecture=None,
                origin="test_origin",
                compiler=None,
            ),
            create_test_build_history_item(
                id="build_skip",
                status="SKIP",
                config_name=None,
                architecture=None,
                origin="test_origin",
                compiler=None,
            ),
            create_test_build_history_item(
                id="build_miss",
                status="MISS",
                config_name=None,
                architecture=None,
                origin="test_origin",
                compiler=None,
            ),
            create_test_build_history_item(
                id="build_done",
                status="DONE",
                config_name=None,
                architecture=None,
                origin="test_origin",
                compiler=None,
            ),
            create_test_build_history_item(
                id="build_null",
                status="NULL",
                config_name=None,
                architecture=None,
                origin="test_origin",
                compiler=None,
            ),
        ]

        result = create_details_build_summary(builds)

        assert result.status.PASS == 1
        assert result.status.FAIL == 1
        assert result.status.ERROR == 1
        assert result.status.SKIP == 1
        assert result.status.MISS == 1
        assert result.status.DONE == 1
        assert result.status.NULL == 1
