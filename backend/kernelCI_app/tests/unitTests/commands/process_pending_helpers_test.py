from unittest.mock import MagicMock
from django.test import SimpleTestCase

from kernelCI_app.management.commands.helpers.process_pending_helpers import (
    EMPTY_PATH_GROUP,
    RollupKey,
    accumulate_rollup_entry,
    aggregate_tests_rollup,
    extract_path_group,
)
from kernelCI_app.constants.general import UNKNOWN_STRING
from kernelCI_app.models import StatusChoices


def _make_checkout(
    origin="test-origin",
    tree_name="mainline",
    git_repository_branch="main",
    git_repository_url="https://example.com/repo.git",
    git_commit_hash="abc123",
):
    checkout = MagicMock()
    checkout.origin = origin
    checkout.tree_name = tree_name
    checkout.git_repository_branch = git_repository_branch
    checkout.git_repository_url = git_repository_url
    checkout.git_commit_hash = git_commit_hash
    return checkout


def _make_build(
    checkout=None,
    architecture="x86_64",
    compiler="gcc",
    config_name="defconfig",
):
    build = MagicMock()
    build.checkout = checkout or _make_checkout()
    build.architecture = architecture
    build.compiler = compiler
    build.config_name = config_name
    return build


def _make_pending_test(
    test_id="test-1",
    build_id="build-1",
    path="boot.test",
    platform="qemu-x86",
    compatible=None,
    lab="lab-1",
    origin="test-origin",
    is_boot=False,
    full_status=StatusChoices.PASS,
):
    test = MagicMock()
    test.test_id = test_id
    test.build_id = build_id
    test.path = path
    test.platform = platform
    test.compatible = compatible
    test.lab = lab
    test.origin = origin
    test.is_boot = is_boot
    test.full_status = full_status
    return test


def _make_rollup_entry(checkout=None, status=StatusChoices.PASS, **overrides):
    defaults = {
        "checkout": checkout or _make_checkout(),
        "path_group": "boot",
        "config": "defconfig",
        "arch": "x86_64",
        "compiler": "gcc",
        "hardware_key": "qemu-x86",
        "platform": "qemu-x86",
        "lab": "lab-1",
        "origin": "test-origin",
        "issue_id": None,
        "issue_version": None,
        "issue_uncategorized": False,
        "is_boot": False,
        "status": status,
    }
    defaults.update(overrides)
    return defaults


class TestExtractPathGroup(SimpleTestCase):
    def test_path_with_dot_returns_first_segment(self):
        self.assertEqual(extract_path_group("boot.test"), "boot")

    def test_path_with_multiple_dots_returns_first_segment_only(self):
        self.assertEqual(extract_path_group("a.b.c.d"), "a")

    def test_path_without_dot_returns_path_itself(self):
        self.assertEqual(extract_path_group("boot"), "boot")

    def test_empty_string_returns_empty_path_group(self):
        self.assertEqual(extract_path_group(""), EMPTY_PATH_GROUP)

    def test_none_returns_empty_path_group(self):
        self.assertEqual(extract_path_group(None), EMPTY_PATH_GROUP)

    def test_path_starting_with_dot_returns_empty_string_segment(self):
        self.assertEqual(extract_path_group(".boot"), "")


class TestAccumulateRollupEntry(SimpleTestCase):
    def test_new_entry_creates_record_with_total_one(self):
        rollup_data = {}
        entry = _make_rollup_entry(status=StatusChoices.PASS)

        accumulate_rollup_entry(rollup_data, entry)

        self.assertEqual(len(rollup_data), 1)
        record = next(iter(rollup_data.values()))
        self.assertEqual(record["total_tests"], 1)
        self.assertEqual(record["pass_tests"], 1)

    def test_same_entry_twice_increments_counters(self):
        rollup_data = {}
        entry = _make_rollup_entry(status=StatusChoices.PASS)

        accumulate_rollup_entry(rollup_data, entry)
        accumulate_rollup_entry(rollup_data, entry)

        self.assertEqual(len(rollup_data), 1)
        record = next(iter(rollup_data.values()))
        self.assertEqual(record["total_tests"], 2)
        self.assertEqual(record["pass_tests"], 2)

    def test_fail_status_increments_fail_tests(self):
        rollup_data = {}
        entry = _make_rollup_entry(status=StatusChoices.FAIL)

        accumulate_rollup_entry(rollup_data, entry)

        record = next(iter(rollup_data.values()))
        self.assertEqual(record["fail_tests"], 1)
        self.assertEqual(record["pass_tests"], 0)

    def test_skip_status_increments_skip_tests(self):
        rollup_data = {}
        entry = _make_rollup_entry(status=StatusChoices.SKIP)

        accumulate_rollup_entry(rollup_data, entry)

        record = next(iter(rollup_data.values()))
        self.assertEqual(record["skip_tests"], 1)

    def test_error_status_increments_error_tests(self):
        rollup_data = {}
        entry = _make_rollup_entry(status=StatusChoices.ERROR)

        accumulate_rollup_entry(rollup_data, entry)

        record = next(iter(rollup_data.values()))
        self.assertEqual(record["error_tests"], 1)

    def test_miss_status_increments_miss_tests(self):
        rollup_data = {}
        entry = _make_rollup_entry(status=StatusChoices.MISS)

        accumulate_rollup_entry(rollup_data, entry)

        record = next(iter(rollup_data.values()))
        self.assertEqual(record["miss_tests"], 1)

    def test_done_status_increments_done_tests(self):
        rollup_data = {}
        entry = _make_rollup_entry(status=StatusChoices.DONE)

        accumulate_rollup_entry(rollup_data, entry)

        record = next(iter(rollup_data.values()))
        self.assertEqual(record["done_tests"], 1)

    def test_unknown_status_increments_null_tests(self):
        rollup_data = {}
        entry = _make_rollup_entry(status="UNKNOWN_STATUS")

        accumulate_rollup_entry(rollup_data, entry)

        record = next(iter(rollup_data.values()))
        self.assertEqual(record["null_tests"], 1)
        self.assertEqual(record["total_tests"], 1)

    def test_none_status_increments_null_tests(self):
        rollup_data = {}
        entry = _make_rollup_entry(status=None)

        accumulate_rollup_entry(rollup_data, entry)

        record = next(iter(rollup_data.values()))
        self.assertEqual(record["null_tests"], 1)

    def test_different_keys_create_separate_records(self):
        rollup_data = {}
        checkout = _make_checkout()

        entry_a = _make_rollup_entry(checkout=checkout, path_group="boot")
        entry_b = _make_rollup_entry(checkout=checkout, path_group="kselftest")

        accumulate_rollup_entry(rollup_data, entry_a)
        accumulate_rollup_entry(rollup_data, entry_b)

        self.assertEqual(len(rollup_data), 2)

    def test_mixed_statuses_accumulate_independently(self):
        rollup_data = {}
        entry_pass = _make_rollup_entry(status=StatusChoices.PASS)
        entry_fail = _make_rollup_entry(status=StatusChoices.FAIL)

        accumulate_rollup_entry(rollup_data, entry_pass)
        accumulate_rollup_entry(rollup_data, entry_fail)

        record = next(iter(rollup_data.values()))
        self.assertEqual(record["total_tests"], 2)
        self.assertEqual(record["pass_tests"], 1)
        self.assertEqual(record["fail_tests"], 1)

    def test_initial_record_has_all_zero_counters(self):
        rollup_data = {}
        entry = _make_rollup_entry(status=StatusChoices.PASS)

        accumulate_rollup_entry(rollup_data, entry)

        record = next(iter(rollup_data.values()))
        for field in (
            "fail_tests",
            "skip_tests",
            "error_tests",
            "miss_tests",
            "done_tests",
            "null_tests",
        ):
            self.assertEqual(record[field], 0, msg=f"{field} should be 0")


class TestAggregateTestsRollup(SimpleTestCase):
    def test_empty_tests_returns_empty_dict(self):
        result = aggregate_tests_rollup([], {}, {})
        self.assertEqual(result, {})

    def test_test_with_missing_build_is_skipped(self):
        test = _make_pending_test(build_id="missing-build")

        result = aggregate_tests_rollup([test], {}, {})

        self.assertEqual(result, {})

    def test_compatible_used_as_hardware_key(self):
        checkout = _make_checkout()
        build = _make_build(checkout=checkout)
        test = _make_pending_test(
            build_id="build-1",
            compatible=["board-model-a", "board-model-b"],
            platform=None,
        )

        result = aggregate_tests_rollup([test], {"build-1": build}, {})

        rollup_key = next(iter(result.keys()))
        self.assertIsInstance(rollup_key, RollupKey)
        self.assertEqual(rollup_key.hardware_key, "board-model-a")

    def test_platform_used_as_hardware_key_when_no_compatible(self):
        checkout = _make_checkout()
        build = _make_build(checkout=checkout)
        test = _make_pending_test(
            build_id="build-1",
            compatible=None,
            platform="qemu-x86",
        )

        result = aggregate_tests_rollup([test], {"build-1": build}, {})

        rollup_key = next(iter(result.keys()))
        self.assertEqual(rollup_key.hardware_key, "qemu-x86")

    def test_unknown_string_used_as_hardware_key_when_no_compatible_and_no_platform(
        self,
    ):
        checkout = _make_checkout()
        build = _make_build(checkout=checkout)
        test = _make_pending_test(
            build_id="build-1",
            compatible=None,
            platform=None,
        )

        result = aggregate_tests_rollup([test], {"build-1": build}, {})

        rollup_key = next(iter(result.keys()))
        self.assertEqual(rollup_key.hardware_key, UNKNOWN_STRING)

    def test_empty_compatible_list_falls_back_to_platform(self):
        checkout = _make_checkout()
        build = _make_build(checkout=checkout)
        test = _make_pending_test(
            build_id="build-1",
            compatible=[],
            platform="fallback-platform",
        )

        result = aggregate_tests_rollup([test], {"build-1": build}, {})

        rollup_key = next(iter(result.keys()))
        self.assertEqual(rollup_key.hardware_key, "fallback-platform")

    def test_issue_info_is_set_from_issues_map(self):
        checkout = _make_checkout()
        build = _make_build(checkout=checkout)
        test = _make_pending_test(
            test_id="test-1",
            build_id="build-1",
            full_status=StatusChoices.FAIL,
        )
        issues_map = {"test-1": {"issue_id": "issue-42", "issue_version": 3}}

        result = aggregate_tests_rollup([test], {"build-1": build}, issues_map)

        rollup_key = next(iter(result.keys()))
        self.assertEqual(rollup_key.issue_id, "issue-42")
        self.assertEqual(rollup_key.issue_version, 3)

    def test_fail_without_issue_sets_uncategorized_true(self):
        checkout = _make_checkout()
        build = _make_build(checkout=checkout)
        test = _make_pending_test(
            test_id="test-1",
            build_id="build-1",
            full_status=StatusChoices.FAIL,
        )

        result = aggregate_tests_rollup([test], {"build-1": build}, {})

        rollup_key = next(iter(result.keys()))
        self.assertTrue(rollup_key.issue_uncategorized)

    def test_fail_with_issue_sets_uncategorized_false(self):
        checkout = _make_checkout()
        build = _make_build(checkout=checkout)
        test = _make_pending_test(
            test_id="test-1",
            build_id="build-1",
            full_status=StatusChoices.FAIL,
        )
        issues_map = {"test-1": {"issue_id": "issue-1", "issue_version": 1}}

        result = aggregate_tests_rollup([test], {"build-1": build}, issues_map)

        rollup_key = next(iter(result.keys()))
        self.assertFalse(rollup_key.issue_uncategorized)

    def test_pass_without_issue_sets_uncategorized_false(self):
        checkout = _make_checkout()
        build = _make_build(checkout=checkout)
        test = _make_pending_test(
            test_id="test-1",
            build_id="build-1",
            full_status=StatusChoices.PASS,
        )

        result = aggregate_tests_rollup([test], {"build-1": build}, {})

        rollup_key = next(iter(result.keys()))
        self.assertFalse(rollup_key.issue_uncategorized)

    def test_build_none_fields_fall_back_to_unknown_string(self):
        checkout = _make_checkout()
        build = _make_build(
            checkout=checkout,
            architecture=None,
            compiler=None,
            config_name=None,
        )
        test = _make_pending_test(build_id="build-1")

        result = aggregate_tests_rollup([test], {"build-1": build}, {})

        rollup_key = next(iter(result.keys()))
        self.assertEqual(rollup_key.arch, UNKNOWN_STRING)
        self.assertEqual(rollup_key.compiler, UNKNOWN_STRING)
        self.assertEqual(rollup_key.config, UNKNOWN_STRING)

    def test_none_path_uses_empty_path_group(self):
        checkout = _make_checkout()
        build = _make_build(checkout=checkout)
        test = _make_pending_test(build_id="build-1", path=None)

        result = aggregate_tests_rollup([test], {"build-1": build}, {})

        rollup_key = next(iter(result.keys()))
        self.assertEqual(rollup_key.path_group, EMPTY_PATH_GROUP)

    def test_path_is_grouped_by_first_segment(self):
        checkout = _make_checkout()
        build = _make_build(checkout=checkout)
        test = _make_pending_test(build_id="build-1", path="kselftest.net.tcp")

        result = aggregate_tests_rollup([test], {"build-1": build}, {})

        rollup_key = next(iter(result.keys()))
        self.assertEqual(rollup_key.path_group, "kselftest")

    def test_multiple_tests_same_key_accumulate_counts(self):
        checkout = _make_checkout()
        build = _make_build(checkout=checkout)
        test1 = _make_pending_test(
            test_id="t1", build_id="build-1", full_status=StatusChoices.PASS
        )
        test2 = _make_pending_test(
            test_id="t2", build_id="build-1", full_status=StatusChoices.PASS
        )

        result = aggregate_tests_rollup([test1, test2], {"build-1": build}, {})

        self.assertEqual(len(result), 1)
        record = next(iter(result.values()))
        self.assertEqual(record["total_tests"], 2)
        self.assertEqual(record["pass_tests"], 2)

    def test_multiple_tests_different_path_groups_create_separate_keys(self):
        checkout = _make_checkout()
        build = _make_build(checkout=checkout)
        test1 = _make_pending_test(test_id="t1", build_id="build-1", path="boot.test")
        test2 = _make_pending_test(
            test_id="t2", build_id="build-1", path="kselftest.net"
        )

        result = aggregate_tests_rollup([test1, test2], {"build-1": build}, {})

        self.assertEqual(len(result), 2)

    def test_skips_test_with_missing_build_but_processes_others(self):
        checkout = _make_checkout()
        build = _make_build(checkout=checkout)
        test_ok = _make_pending_test(test_id="t1", build_id="build-1")
        test_missing = _make_pending_test(test_id="t2", build_id="missing-build")

        result = aggregate_tests_rollup([test_ok, test_missing], {"build-1": build}, {})

        self.assertEqual(len(result), 1)
        record = next(iter(result.values()))
        self.assertEqual(record["total_tests"], 1)
