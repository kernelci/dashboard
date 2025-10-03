from kernelCI_app.helpers.commonDetails import add_unfiltered_issue


class TestAddUnfilteredIssue:
    def test_add_unfiltered_issue_with_valid_issue_and_increment(self):
        """Test adding issue when all conditions are met."""
        issue_set = set()
        unknown_issue_flag_dict = {"build": False, "boot": False, "test": False}

        add_unfiltered_issue(
            issue_id="issue123",
            issue_version=1,
            should_increment=True,
            issue_set=issue_set,
            is_failed_task=False,
            unknown_issue_flag_dict=unknown_issue_flag_dict,
            unknown_issue_flag_tab="build",
        )

        assert (("issue123", 1)) in issue_set
        assert unknown_issue_flag_dict["build"] is False

    def test_add_unfiltered_issue_with_failed_task(self):
        """Test setting unknown issue flag when task failed."""
        issue_set = set()
        unknown_issue_flag_dict = {"build": False, "boot": False, "test": False}

        add_unfiltered_issue(
            issue_id="issue123",
            issue_version=1,
            should_increment=False,
            issue_set=issue_set,
            is_failed_task=True,
            unknown_issue_flag_dict=unknown_issue_flag_dict,
            unknown_issue_flag_tab="test",
        )

        assert len(issue_set) == 0
        assert unknown_issue_flag_dict["test"] is True

    def test_add_unfiltered_issue_with_none_issue_id(self):
        """Test behavior when issue_id is None."""
        issue_set = set()
        unknown_issue_flag_dict = {"build": False, "boot": False, "test": False}

        add_unfiltered_issue(
            issue_id=None,
            issue_version=1,
            should_increment=True,
            issue_set=issue_set,
            is_failed_task=False,
            unknown_issue_flag_dict=unknown_issue_flag_dict,
            unknown_issue_flag_tab="build",
        )

        assert len(issue_set) == 0
        assert unknown_issue_flag_dict["build"] is False

    def test_add_unfiltered_issue_with_none_issue_version(self):
        """Test behavior when issue_version is None."""
        issue_set = set()
        unknown_issue_flag_dict = {"build": False, "boot": False, "test": False}

        add_unfiltered_issue(
            issue_id="issue123",
            issue_version=None,
            should_increment=True,
            issue_set=issue_set,
            is_failed_task=False,
            unknown_issue_flag_dict=unknown_issue_flag_dict,
            unknown_issue_flag_tab="build",
        )

        assert len(issue_set) == 0
        assert unknown_issue_flag_dict["build"] is False

    def test_add_unfiltered_issue_with_should_increment_false(self):
        """Test behavior when should_increment is False."""
        issue_set = set()
        unknown_issue_flag_dict = {"build": False, "boot": False, "test": False}

        add_unfiltered_issue(
            issue_id="issue123",
            issue_version=1,
            should_increment=False,
            issue_set=issue_set,
            is_failed_task=False,
            unknown_issue_flag_dict=unknown_issue_flag_dict,
            unknown_issue_flag_tab="build",
        )

        assert len(issue_set) == 0
        assert unknown_issue_flag_dict["build"] is False

    def test_add_unfiltered_issue_with_both_conditions_false(self):
        """Test behavior when both should_increment and is_failed_task are False."""
        issue_set = set()
        unknown_issue_flag_dict = {"build": False, "boot": False, "test": False}

        add_unfiltered_issue(
            issue_id="issue123",
            issue_version=1,
            should_increment=False,
            issue_set=issue_set,
            is_failed_task=False,
            unknown_issue_flag_dict=unknown_issue_flag_dict,
            unknown_issue_flag_tab="boot",
        )

        assert len(issue_set) == 0
        assert unknown_issue_flag_dict["boot"] is False
