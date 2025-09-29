from kernelCI_app.helpers.issueListing import (
    should_discard_issue_by_culprit,
    should_discard_issue_by_origin,
    should_discard_issue_by_options,
    should_discard_issue_by_category,
    should_discard_issue_record,
)
from kernelCI_app.helpers.filters import FilterParams
from kernelCI_app.typeModels.issues import (
    CULPRIT_CODE,
    CULPRIT_HARNESS,
    CULPRIT_TOOL,
    HAS_INCIDENT_OPTION,
)


class TestShouldDiscardIssueByCulprit:
    def test_should_discard_issue_by_culprit_no_filters(self):
        """Test should_discard_issue_by_culprit with no filters."""
        record = {"culprit_code": True, "culprit_harness": False, "culprit_tool": False}

        result = should_discard_issue_by_culprit(culprit_filters=set(), record=record)

        assert result is False

    def test_should_discard_issue_by_culprit_with_code_culprit(self):
        """Test should_discard_issue_by_culprit with code culprit."""
        record = {"culprit_code": True, "culprit_harness": False, "culprit_tool": False}

        result = should_discard_issue_by_culprit(
            culprit_filters={CULPRIT_CODE}, record=record
        )

        assert result is False

    def test_should_discard_issue_by_culprit_with_harness_culprit(self):
        """Test should_discard_issue_by_culprit with harness culprit."""
        record = {"culprit_code": False, "culprit_harness": True, "culprit_tool": False}

        result = should_discard_issue_by_culprit(
            culprit_filters={CULPRIT_HARNESS}, record=record
        )

        assert result is False

    def test_should_discard_issue_by_culprit_with_tool_culprit(self):
        """Test should_discard_issue_by_culprit with tool culprit."""
        record = {"culprit_code": False, "culprit_harness": False, "culprit_tool": True}

        result = should_discard_issue_by_culprit(
            culprit_filters={CULPRIT_TOOL}, record=record
        )

        assert result is False

    def test_should_discard_issue_by_culprit_with_no_matching_culprits(self):
        """Test should_discard_issue_by_culprit with no matching culprits."""
        record = {
            "culprit_code": False,
            "culprit_harness": False,
            "culprit_tool": False,
        }

        result = should_discard_issue_by_culprit(
            culprit_filters={CULPRIT_CODE}, record=record
        )

        assert result is True


class TestShouldDiscardIssueByOrigin:
    def test_should_discard_issue_by_origin_no_filters(self):
        """Test should_discard_issue_by_origin with no filters."""
        result = should_discard_issue_by_origin(
            origin_filters=set(), issue_origin="origin1"
        )

        assert result is False

    def test_should_discard_issue_by_origin_matching_origin(self):
        """Test should_discard_issue_by_origin with matching origin."""
        result = should_discard_issue_by_origin(
            origin_filters={"origin1", "origin2"}, issue_origin="origin1"
        )

        assert result is False

    def test_should_discard_issue_by_origin_non_matching_origin(self):
        """Test should_discard_issue_by_origin with non-matching origin."""
        result = should_discard_issue_by_origin(
            origin_filters={"origin1", "origin2"}, issue_origin="origin3"
        )

        assert result is True


class TestShouldDiscardIssueByOptions:
    def test_should_discard_issue_by_options_no_filters(self):
        """Test should_discard_issue_by_options with no filters."""
        record = {"has_incident": True}

        result = should_discard_issue_by_options(option_filters=set(), record=record)

        assert result is False

    def test_should_discard_issue_by_options_with_incident(self):
        """Test should_discard_issue_by_options with incident option."""
        record = {"has_incident": True}

        result = should_discard_issue_by_options(
            option_filters={HAS_INCIDENT_OPTION}, record=record
        )

        assert result is False

    def test_should_discard_issue_by_options_without_incident(self):
        """Test should_discard_issue_by_options without incident."""
        record = {"has_incident": False}

        result = should_discard_issue_by_options(
            option_filters={HAS_INCIDENT_OPTION}, record=record
        )

        assert result is True

    def test_should_discard_issue_by_options_none_incident(self):
        """Test should_discard_issue_by_options with None incident."""
        record = {"has_incident": None}

        result = should_discard_issue_by_options(
            option_filters={HAS_INCIDENT_OPTION}, record=record
        )

        assert result is True


class TestShouldDiscardIssueByCategory:
    def test_should_discard_issue_by_category_no_filters(self):
        """Test should_discard_issue_by_category with no filters."""
        result = should_discard_issue_by_category(
            categories_filters=set(), issue_categories=["category1", "category2"]
        )

        assert result is False

    def test_should_discard_issue_by_category_matching_category(self):
        """Test should_discard_issue_by_category with matching category."""
        result = should_discard_issue_by_category(
            categories_filters={"category1", "category3"},
            issue_categories=["category1", "category2"],
        )

        assert result is False

    def test_should_discard_issue_by_category_non_matching_category(self):
        """Test should_discard_issue_by_category with non-matching category."""
        result = should_discard_issue_by_category(
            categories_filters={"category1", "category3"},
            issue_categories=["category2", "category4"],
        )

        assert result is True

    def test_should_discard_issue_by_category_empty_categories(self):
        """Test should_discard_issue_by_category with empty categories."""
        result = should_discard_issue_by_category(
            categories_filters={"category1"}, issue_categories=[]
        )

        assert result is True


class TestShouldDiscardIssueRecord:
    def test_should_discard_issue_record_no_filters(self):
        """Test should_discard_issue_record with no filters."""
        issue = {
            "origin": "origin1",
            "categories": ["category1"],
            "culprit_code": True,
            "culprit_harness": False,
            "culprit_tool": False,
            "has_incident": True,
        }

        result = should_discard_issue_record(filters=None, issue=issue)

        assert result is False

    def test_should_discard_issue_record_with_filters_no_discard(self):
        """Test should_discard_issue_record with filters but no discard."""
        filters = FilterParams({}, process_body=True)
        filters.filter_origins = {"origin1"}
        filters.filter_issue_culprits = {CULPRIT_CODE}
        filters.filter_issue_options = {HAS_INCIDENT_OPTION}
        filters.filter_issue_categories = {"category1"}

        issue = {
            "origin": "origin1",
            "categories": ["category1"],
            "culprit_code": True,
            "culprit_harness": False,
            "culprit_tool": False,
            "has_incident": True,
        }

        result = should_discard_issue_record(filters=filters, issue=issue)

        assert result is False

    def test_should_discard_issue_record_with_filters_discard_by_origin(self):
        """Test should_discard_issue_record with filters that discard by origin."""
        filters = FilterParams({}, process_body=True)
        filters.filter_origins = {"origin2"}
        filters.filter_issue_culprits = set()
        filters.filter_issue_options = set()
        filters.filter_issue_categories = set()

        issue = {
            "origin": "origin1",
            "categories": ["category1"],
            "culprit_code": True,
            "culprit_harness": False,
            "culprit_tool": False,
            "has_incident": True,
        }

        result = should_discard_issue_record(filters=filters, issue=issue)

        assert result is True

    def test_should_discard_issue_record_with_filters_discard_by_culprit(self):
        """Test should_discard_issue_record with filters that discard by culprit."""
        filters = FilterParams({}, process_body=True)
        filters.filter_origins = set()
        filters.filter_issue_culprits = {CULPRIT_HARNESS}
        filters.filter_issue_options = set()
        filters.filter_issue_categories = set()

        issue = {
            "origin": "origin1",
            "categories": ["category1"],
            "culprit_code": True,
            "culprit_harness": False,
            "culprit_tool": False,
            "has_incident": True,
        }

        result = should_discard_issue_record(filters=filters, issue=issue)

        assert result is True

    def test_should_discard_issue_record_with_filters_discard_by_options(self):
        """Test should_discard_issue_record with filters that discard by options."""
        filters = FilterParams({}, process_body=True)
        filters.filter_origins = set()
        filters.filter_issue_culprits = set()
        filters.filter_issue_options = {HAS_INCIDENT_OPTION}
        filters.filter_issue_categories = set()

        issue = {
            "origin": "origin1",
            "categories": ["category1"],
            "culprit_code": True,
            "culprit_harness": False,
            "culprit_tool": False,
            "has_incident": False,
        }

        result = should_discard_issue_record(filters=filters, issue=issue)

        assert result is True

    def test_should_discard_issue_record_with_filters_discard_by_category(self):
        """Test should_discard_issue_record with filters that discard by category."""
        filters = FilterParams({}, process_body=True)
        filters.filter_origins = set()
        filters.filter_issue_culprits = set()
        filters.filter_issue_options = set()
        filters.filter_issue_categories = {"category2"}

        issue = {
            "origin": "origin1",
            "categories": ["category1"],
            "culprit_code": True,
            "culprit_harness": False,
            "culprit_tool": False,
            "has_incident": True,
        }

        result = should_discard_issue_record(filters=filters, issue=issue)

        assert result is True

    def test_should_discard_issue_record_with_missing_categories(self):
        """Test should_discard_issue_record with missing categories in issue."""
        filters = FilterParams({}, process_body=True)
        filters.filter_origins = set()
        filters.filter_issue_culprits = set()
        filters.filter_issue_options = set()
        filters.filter_issue_categories = {"category1"}

        issue = {
            "origin": "origin1",
            "culprit_code": True,
            "culprit_harness": False,
            "culprit_tool": False,
            "has_incident": True,
        }

        result = should_discard_issue_record(filters=filters, issue=issue)

        assert result is True
