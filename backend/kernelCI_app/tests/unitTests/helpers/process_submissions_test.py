from unittest.mock import patch, MagicMock
from django.db import IntegrityError
from django.test import SimpleTestCase
from django.utils import timezone
from pydantic import ValidationError

from kernelCI_app.management.commands.helpers.process_submissions import (
    get_model_fields,
    flatten_dict_specific,
    make_issue_instance,
    make_checkout_instance,
    make_build_instance,
    make_test_instance,
    make_incident_instance,
    build_instances_from_submission,
    insert_items,
    insert_submission_data,
)
from kernelCI_app.models import Issues, Checkouts, Builds, Tests, Incidents


MOCK_TIME = timezone.datetime(2025, 10, 11, 12, 0, 0)


class TestGetModelFields(SimpleTestCase):
    def test_get_model_fields_regular_field(self):
        mock_field = MagicMock()
        mock_field.__class__.__name__ = "TextField"
        mock_field.name = "description"

        result = get_model_fields([mock_field])

        self.assertIn("description", result)
        self.assertEqual(len(result), 1)

    def test_get_model_fields_foreign_key_field(self):
        mock_field = MagicMock()
        mock_field.__class__.__name__ = "ForeignKey"
        mock_field.name = "description"

        result = get_model_fields([mock_field])

        self.assertIn("description_id", result)
        self.assertNotIn("description", result)


class TestFlattenDictSpecific(SimpleTestCase):
    def test_flatten_dict_specific_with_dict_value(self):
        target = {
            "environment": {"comment": "foo", "misc": {"platform": "bar"}},
            "other_field": "value",
        }

        result = flatten_dict_specific(target, ["environment"])

        expected = {
            "environment_comment": "foo",
            "environment_misc": {"platform": "bar"},
            "other_field": "value",
        }
        self.assertEqual(result, expected)

    def test_flatten_dict_specific_with_multiple_target_fields(self):
        target = {
            "environment": {"comment": "env_comment"},
            "number": {"value": 42, "unit": "seconds"},
            "other": "value",
        }

        result = flatten_dict_specific(target, ["environment", "number"])

        expected = {
            "environment_comment": "env_comment",
            "number_value": 42,
            "number_unit": "seconds",
            "other": "value",
        }
        self.assertEqual(result, expected)

    def test_flatten_dict_specific_with_empty_dict(self):
        result = flatten_dict_specific({}, ["environment"])
        self.assertEqual(result, {})

    def test_flatten_dict_specific_with_no_target_fields(self):
        target = {"field1": {"nested": "value"}, "field2": "value"}
        result = flatten_dict_specific(target, ["nonexistent"])
        self.assertEqual(result, target)

    def test_flatten_dict_specific_with_non_dict_value(self):
        target = {
            "environment": "not_a_dict",
            "other_field": "value",
        }

        result = flatten_dict_specific(target, ["environment"])

        self.assertEqual(result, target)

    def test_flatten_dict_specific_with_empty_dict_value(self):
        target = {
            "environment": {},
            "other_field": "value",
        }

        result = flatten_dict_specific(target, ["environment"])

        expected = {"other_field": "value"}
        self.assertEqual(result, expected)


@patch("kernelCI_app.management.commands.helpers.process_submissions.timezone.now")
class TestMakeIssueInstance(SimpleTestCase):
    def test_make_issue_instance_with_all_fields(self, mock_now):
        mock_now.return_value = MOCK_TIME
        issue_data = {
            "id": "issue",
            "version": 1,
            "origin": "test_origin",
            "report_url": "http://my_url.com",
            "comment": "Test issue",
            "culprit": {"code": True, "tool": False, "harness": True},
            "misc": {"key": "value"},
            "extra_field": "should_be_filtered",
        }

        result = make_issue_instance(issue_data)

        self.assertIsInstance(result, Issues)
        self.assertFalse(hasattr(result, "extra_field"))

        expected_fields = {
            "id": "issue",
            "version": 1,
            "origin": "test_origin",
            "report_url": "http://my_url.com",
            "comment": "Test issue",
            "culprit_code": True,
            "culprit_tool": False,
            "culprit_harness": True,
            "misc": {"key": "value"},
            "field_timestamp": MOCK_TIME,
        }
        actual_fields = {field: getattr(result, field) for field in expected_fields}
        self.assertEqual(actual_fields, expected_fields)


@patch("kernelCI_app.management.commands.helpers.process_submissions.timezone.now")
class TestMakeCheckoutInstance(SimpleTestCase):
    def test_make_checkout_instance_with_all_fields(self, mock_now):
        mock_now.return_value = MOCK_TIME
        checkout_data = {
            "id": "checkout",
            "origin": "test_origin",
            "tree_name": "mainline",
            "git_repository_url": "https://my_git_url.com",
            "git_commit_hash": "abc123",
            "git_repository_branch": "master",
            "extra_field": "should_be_filtered",
        }

        result = make_checkout_instance(checkout_data)

        self.assertIsInstance(result, Checkouts)
        self.assertFalse(hasattr(result, "extra_field"))

        expected_fields = {
            "id": "checkout",
            "origin": "test_origin",
            "tree_name": "mainline",
            "git_repository_url": "https://my_git_url.com",
            "git_commit_hash": "abc123",
            "git_repository_branch": "master",
            "field_timestamp": MOCK_TIME,
        }
        actual_fields = {field: getattr(result, field) for field in expected_fields}
        self.assertEqual(actual_fields, expected_fields)


@patch("kernelCI_app.management.commands.helpers.process_submissions.timezone.now")
class TestMakeBuildInstance(SimpleTestCase):
    def test_make_build_instance_with_all_fields(self, mock_now):
        mock_now.return_value = MOCK_TIME
        build_data = {
            "id": "build",
            "origin": "test_origin",
            "checkout_id": "checkout",
            "architecture": "x86_64",
            "status": "PASS",
            "config_name": "defconfig",
            "extra_field": "should_be_filtered",
        }

        result = make_build_instance(build_data)

        self.assertIsInstance(result, Builds)
        self.assertFalse(hasattr(result, "extra_field"))

        expected_fields = {
            "id": "build",
            "origin": "test_origin",
            "checkout_id": "checkout",
            "architecture": "x86_64",
            "status": "PASS",
            "config_name": "defconfig",
            "field_timestamp": MOCK_TIME,
        }
        actual_fields = {field: getattr(result, field) for field in expected_fields}
        self.assertEqual(actual_fields, expected_fields)


@patch("kernelCI_app.management.commands.helpers.process_submissions.timezone.now")
class TestMakeTestInstance(SimpleTestCase):
    def test_make_test_instance_with_all_fields(self, mock_now):
        mock_now.return_value = MOCK_TIME
        test_data = {
            "id": "test",
            "origin": "test_origin",
            "build_id": "build",
            "path": "boot.boot_test",
            "status": "PASS",
            "environment": {
                "comment": "Test environment",
                "misc": {"platform": "x86_64"},
            },
            "number": {"value": 42.5, "unit": "seconds", "prefix": "metric"},
            "extra_field": "should_be_filtered",
        }

        result = make_test_instance(test_data)

        self.assertIsInstance(result, Tests)
        self.assertFalse(hasattr(result, "extra_field"))

        expected_fields = {
            "id": "test",
            "origin": "test_origin",
            "build_id": "build",
            "path": "boot.boot_test",
            "status": "PASS",
            "environment_comment": "Test environment",
            "environment_misc": {"platform": "x86_64"},
            "number_value": 42.5,
            "number_unit": "seconds",
            "number_prefix": "metric",
            "field_timestamp": MOCK_TIME,
        }
        actual_fields = {field: getattr(result, field) for field in expected_fields}
        self.assertEqual(actual_fields, expected_fields)


@patch("kernelCI_app.management.commands.helpers.process_submissions.timezone.now")
class TestMakeIncidentInstance(SimpleTestCase):
    def test_make_incident_instance_with_all_fields(self, mock_now):
        mock_now.return_value = MOCK_TIME
        incident_data = {
            "id": "incident",
            "origin": "test_origin",
            "issue_id": "issue",
            "issue_version": 1,
            "build_id": "build",
            "test_id": "test",
            "present": True,
            "comment": "Test incident",
            "extra_field": "should_be_filtered",
        }

        result = make_incident_instance(incident_data)

        self.assertIsInstance(result, Incidents)
        self.assertFalse(hasattr(result, "extra_field"))

        expected_fields = {
            "id": "incident",
            "origin": "test_origin",
            "issue_id": "issue",
            "issue_version": 1,
            "build_id": "build",
            "test_id": "test",
            "present": True,
            "comment": "Test incident",
            "field_timestamp": MOCK_TIME,
        }
        actual_fields = {field: getattr(result, field) for field in expected_fields}
        self.assertEqual(actual_fields, expected_fields)


class TestBuildInstancesFromSubmission(SimpleTestCase):
    @patch(
        "kernelCI_app.management.commands.helpers.process_submissions.make_issue_instance"
    )
    @patch(
        "kernelCI_app.management.commands.helpers.process_submissions.make_checkout_instance"
    )
    @patch(
        "kernelCI_app.management.commands.helpers.process_submissions.make_build_instance"
    )
    @patch(
        "kernelCI_app.management.commands.helpers.process_submissions.make_test_instance"
    )
    @patch(
        "kernelCI_app.management.commands.helpers.process_submissions.make_incident_instance"
    )
    def test_build_instances_from_submission_with_all_types(
        self,
        mock_make_incident,
        mock_make_test,
        mock_make_build,
        mock_make_checkout,
        mock_make_issue,
    ):
        mock_make_issue.return_value = MagicMock()
        mock_make_checkout.return_value = MagicMock()
        mock_make_build.return_value = MagicMock()
        mock_make_test.return_value = MagicMock()
        mock_make_incident.return_value = MagicMock()

        submission_data = {
            "issues": [{"id": "issue", "version": 1, "origin": "test"}],
            "checkouts": [{"id": "checkout", "origin": "test"}],
            "builds": [{"id": "build", "origin": "test", "checkout_id": "checkout"}],
            "tests": [{"id": "test", "origin": "test", "build_id": "build"}],
            "incidents": [
                {
                    "id": "incident",
                    "origin": "test",
                    "issue_id": "issue",
                    "issue_version": 1,
                }
            ],
        }

        result = build_instances_from_submission(submission_data)

        expected = {
            "issues": [mock_make_issue.return_value],
            "checkouts": [mock_make_checkout.return_value],
            "builds": [mock_make_build.return_value],
            "tests": [mock_make_test.return_value],
            "incidents": [mock_make_incident.return_value],
        }
        self.assertEqual(result, expected)

        mock_make_issue.assert_called_once()
        mock_make_checkout.assert_called_once()
        mock_make_build.assert_called_once()
        mock_make_test.assert_called_once()
        mock_make_incident.assert_called_once()

    def test_build_instances_from_submission_with_empty_data(self):
        result = build_instances_from_submission({})

        expected = {
            "issues": [],
            "checkouts": [],
            "builds": [],
            "tests": [],
            "incidents": [],
        }
        self.assertEqual(result, expected)

    @patch("kernelCI_app.management.commands.helpers.process_submissions.logger")
    @patch(
        "kernelCI_app.management.commands.helpers.process_submissions.make_issue_instance"
    )
    def test_build_instances_from_submission_with_validation_error(
        self, mock_make_issue, mock_logger
    ):
        submission_data = {"issues": [{"id": "issue", "version": 1, "origin": "test"}]}
        mock_make_issue.side_effect = ValidationError.from_exception_data(
            "TestModel", []
        )

        result = build_instances_from_submission(submission_data)

        self.assertEqual(len(result["issues"]), 0)
        mock_logger.error.assert_called_once()

    @patch("kernelCI_app.management.commands.helpers.process_submissions.logger")
    @patch(
        "kernelCI_app.management.commands.helpers.process_submissions.make_issue_instance"
    )
    def test_build_instances_from_submission_with_non_dict_items(
        self, mock_make_issue, mock_logger
    ):
        submission_data = {
            "issues": [
                {"id": "issue_1", "version": 1, "origin": "test"},
                "not_a_dict",
                {"id": "issue_2", "version": 1, "origin": "test"},
            ]
        }

        result = build_instances_from_submission(submission_data)

        self.assertEqual(len(result["issues"]), 2)
        self.assertEqual(mock_make_issue.call_count, 2)
        mock_logger.warning.assert_called_once()

    @patch(
        "kernelCI_app.management.commands.helpers.process_submissions.make_issue_instance"
    )
    def test_build_instances_from_submission_continues_on_error(self, mock_make_issue):
        submission_data = {
            "issues": [
                {"id": "issue_1", "version": 1, "origin": "test"},
                {"id": "issue_2", "version": 1, "origin": "test"},
                {"id": "issue_3", "version": 1, "origin": "test"},
            ]
        }
        mock_issue_1 = MagicMock()
        mock_issue_3 = MagicMock()
        mock_make_issue.side_effect = [
            mock_issue_1,
            ValidationError.from_exception_data("TestModel", []),
            mock_issue_3,
        ]

        result = build_instances_from_submission(submission_data)

        self.assertEqual(len(result["issues"]), 2)
        self.assertEqual(result["issues"][0], mock_issue_1)
        self.assertEqual(result["issues"][1], mock_issue_3)
        self.assertEqual(mock_make_issue.call_count, 3)


class TestInsertItems(SimpleTestCase):
    @patch("kernelCI_app.management.commands.helpers.process_submissions.logger")
    @patch(
        "kernelCI_app.management.commands.helpers.process_submissions.make_issue_instance"
    )
    def test_insert_items_success(self, mock_make_issue, mock_logger):
        mock_issue = MagicMock()
        mock_issue.save = MagicMock()
        mock_make_issue.return_value = mock_issue

        items = [
            {"id": "issue_1", "version": 1, "origin": "test"},
            {"id": "issue_2", "version": 1, "origin": "test"},
        ]

        result = insert_items("issues", items)

        self.assertEqual(result, 2)
        self.assertEqual(mock_make_issue.call_count, 2)
        self.assertEqual(mock_issue.save.call_count, 2)
        mock_logger.info.assert_called_once()

    @patch("kernelCI_app.management.commands.helpers.process_submissions.logger")
    @patch(
        "kernelCI_app.management.commands.helpers.process_submissions.make_issue_instance"
    )
    def test_insert_items_with_validation_error(self, mock_make_issue, mock_logger):
        items = [{"id": "issue", "version": 1, "origin": "test"}]

        mock_make_issue.side_effect = ValidationError.from_exception_data(
            "TestModel", []
        )
        result = insert_items("issues", items)
        self.assertEqual(result, 0)
        self.assertEqual(mock_logger.error.call_count, 1)

    @patch("kernelCI_app.management.commands.helpers.process_submissions.logger")
    @patch(
        "kernelCI_app.management.commands.helpers.process_submissions.make_issue_instance"
    )
    def test_insert_items_with_integrity_error(self, mock_make_issue, mock_logger):
        items = [{"id": "issue", "version": 1, "origin": "test"}]

        mock_issue = MagicMock()
        mock_issue.save = MagicMock(side_effect=IntegrityError("Duplicate key"))
        mock_make_issue.return_value = mock_issue
        result = insert_items("issues", items)
        self.assertEqual(result, 0)
        self.assertEqual(mock_logger.error.call_count, 1)

    @patch("kernelCI_app.management.commands.helpers.process_submissions.logger")
    @patch(
        "kernelCI_app.management.commands.helpers.process_submissions.make_issue_instance"
    )
    def test_insert_items_with_empty_list(self, mock_make_issue, mock_logger):
        items = []

        result = insert_items("issues", items)

        self.assertEqual(result, 0)
        mock_make_issue.assert_not_called()
        mock_logger.info.assert_called_once_with("Processing 0 issues")

    @patch("kernelCI_app.management.commands.helpers.process_submissions.logger")
    @patch(
        "kernelCI_app.management.commands.helpers.process_submissions.make_issue_instance"
    )
    def test_insert_items_continues_on_error(self, mock_make_issue, mock_logger):
        items = [
            {"id": "issue_1", "version": 1, "origin": "test"},
            {"id": "issue_2", "version": 1, "origin": "test"},
            {"id": "issue_3", "version": 1, "origin": "test"},
        ]

        mock_issue_1 = MagicMock()
        mock_issue_1.save = MagicMock()
        mock_issue_3 = MagicMock()
        mock_issue_3.save = MagicMock()
        mock_make_issue.side_effect = [
            mock_issue_1,
            ValidationError.from_exception_data("TestModel", []),
            mock_issue_3,
        ]

        result = insert_items("issues", items)

        self.assertEqual(result, 2)
        self.assertEqual(mock_issue_1.save.call_count, 1)
        self.assertEqual(mock_issue_3.save.call_count, 1)
        self.assertEqual(mock_make_issue.call_count, 3)
        self.assertEqual(mock_logger.error.call_count, 1)


class TestInsertSubmissionData(SimpleTestCase):
    @patch("kernelCI_app.management.commands.helpers.process_submissions.logger")
    @patch("kernelCI_app.management.commands.helpers.process_submissions.insert_items")
    def test_insert_submission_data_with_all_types(
        self, mock_insert_items, mock_logger
    ):
        mock_insert_items.return_value = 1

        submission_data = {
            "issues": [{"id": "issue", "version": 1, "origin": "test"}],
            "checkouts": [{"id": "checkout", "origin": "test"}],
            "builds": [{"id": "build", "origin": "test", "checkout_id": "checkout"}],
            "tests": [{"id": "test", "origin": "test", "build_id": "build"}],
            "incidents": [
                {
                    "id": "incident",
                    "origin": "test",
                    "issue_id": "issue",
                    "issue_version": 1,
                }
            ],
        }
        metadata = {"filename": "test_submission.json"}

        insert_submission_data(submission_data, metadata)

        self.assertEqual(mock_insert_items.call_count, 5)
        mock_logger.info.assert_called()

    @patch("kernelCI_app.management.commands.helpers.process_submissions.logger")
    @patch("kernelCI_app.management.commands.helpers.process_submissions.insert_items")
    def test_insert_submission_data_with_empty_data(
        self, mock_insert_items, mock_logger
    ):
        submission_data = {}
        metadata = {"filename": "empty_submission.json"}

        insert_submission_data(submission_data, metadata)

        self.assertEqual(mock_insert_items.call_count, 0)
        mock_logger.info.assert_called()

    @patch("kernelCI_app.management.commands.helpers.process_submissions.logger")
    @patch("kernelCI_app.management.commands.helpers.process_submissions.insert_items")
    def test_insert_submission_data_error_propagation(
        self, mock_insert_items, mock_logger
    ):
        mock_insert_items.side_effect = ValueError("Processing error")

        submission_data = {
            "issues": [{"id": "issue", "version": 1, "origin": "test"}],
        }
        metadata = {"filename": "error_submission.json"}

        with self.assertRaises(ValueError):
            insert_submission_data(submission_data, metadata)

        mock_logger.error.assert_called_once()
