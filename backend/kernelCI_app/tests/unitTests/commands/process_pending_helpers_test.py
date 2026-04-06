from unittest.mock import MagicMock
from django.test import SimpleTestCase

from kernelCI_app.management.commands.helpers.process_pending_helpers import (
    EMPTY_PATH_GROUP,
    RollupEntryData,
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
    defaults: RollupEntryData = {
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


class TestAccumulateRollupEntryCorrection(SimpleTestCase):
    """Test is_correction=True behavior: null -> non-null transitions."""

    def _make_rollup_data_with_null_entry(self, initial_null_count=1):
        """Pre-seed rollup_data with a record having some null_tests."""
        checkout = _make_checkout()
        entry = _make_rollup_entry(checkout=checkout, status=None)
        rollup_key = RollupKey(
            origin=checkout.origin,
            tree_name=checkout.tree_name,
            git_repository_branch=checkout.git_repository_branch,
            git_repository_url=checkout.git_repository_url,
            git_commit_hash=checkout.git_commit_hash,
            path_group=entry["path_group"],
            config=entry["config"],
            arch=entry["arch"],
            compiler=entry["compiler"],
            hardware_key=entry["hardware_key"],
            platform=entry["platform"],
            lab=entry["lab"],
            test_origin=entry["origin"],
            issue_id=entry["issue_id"],
            issue_version=entry["issue_version"],
            issue_uncategorized=entry["issue_uncategorized"],
            is_boot=entry["is_boot"],
        )
        rollup_data = {
            rollup_key: {
                "pass_tests": 0,
                "fail_tests": 0,
                "skip_tests": 0,
                "error_tests": 0,
                "miss_tests": 0,
                "done_tests": 0,
                "null_tests": initial_null_count,
                "total_tests": initial_null_count,
            }
        }
        return rollup_data, entry, rollup_key

    def test_correction_decrements_null_tests(self):
        """Correction moves count from null_tests to the new status bucket."""
        rollup_data, entry, rollup_key = self._make_rollup_data_with_null_entry()
        entry["status"] = StatusChoices.PASS

        accumulate_rollup_entry(rollup_data, entry, is_correction=True)

        record = rollup_data[rollup_key]
        self.assertEqual(record["null_tests"], 0)

    def test_correction_increments_new_status_bucket(self):
        """The new status bucket gets the count moved from null_tests."""
        rollup_data, entry, rollup_key = self._make_rollup_data_with_null_entry()
        entry["status"] = StatusChoices.PASS

        accumulate_rollup_entry(rollup_data, entry, is_correction=True)

        record = rollup_data[rollup_key]
        self.assertEqual(record["pass_tests"], 1)

    def test_correction_does_not_change_total_tests(self):
        """Total should remain unchanged - just moving from null to bucket."""
        rollup_data, entry, rollup_key = self._make_rollup_data_with_null_entry()
        entry["status"] = StatusChoices.PASS

        accumulate_rollup_entry(rollup_data, entry, is_correction=True)

        record = rollup_data[rollup_key]
        self.assertEqual(record["total_tests"], 1)

    def test_correction_with_fail_status(self):
        """Correction works with fail status too."""
        rollup_data, entry, rollup_key = self._make_rollup_data_with_null_entry()
        entry["status"] = StatusChoices.FAIL

        accumulate_rollup_entry(rollup_data, entry, is_correction=True)

        record = rollup_data[rollup_key]
        self.assertEqual(record["null_tests"], 0)
        self.assertEqual(record["fail_tests"], 1)
        self.assertEqual(record["total_tests"], 1)

    def test_correction_with_skip_status(self):
        """Correction works with skip status."""
        rollup_data, entry, rollup_key = self._make_rollup_data_with_null_entry()
        entry["status"] = StatusChoices.SKIP

        accumulate_rollup_entry(rollup_data, entry, is_correction=True)

        record = rollup_data[rollup_key]
        self.assertEqual(record["null_tests"], 0)
        self.assertEqual(record["skip_tests"], 1)
        self.assertEqual(record["total_tests"], 1)

    def test_correction_with_null_as_new_status(self):
        """If new status is also null, both operations hit null_tests (net zero)."""
        rollup_data, entry, rollup_key = self._make_rollup_data_with_null_entry()
        entry["status"] = None

        accumulate_rollup_entry(rollup_data, entry, is_correction=True)

        record = rollup_data[rollup_key]
        # Decrement then increment null_tests: net change is 0
        self.assertEqual(record["null_tests"], 1)
        self.assertEqual(record["total_tests"], 1)

    def test_multiple_corrections_on_same_rollup_key(self):
        """Multiple corrections on the same key accumulate correctly."""
        checkout = _make_checkout()
        base_entry = _make_rollup_entry(checkout=checkout, status=None)
        rollup_key = RollupKey(
            origin=checkout.origin,
            tree_name=checkout.tree_name,
            git_repository_branch=checkout.git_repository_branch,
            git_repository_url=checkout.git_repository_url,
            git_commit_hash=checkout.git_commit_hash,
            path_group=base_entry["path_group"],
            config=base_entry["config"],
            arch=base_entry["arch"],
            compiler=base_entry["compiler"],
            hardware_key=base_entry["hardware_key"],
            platform=base_entry["platform"],
            lab=base_entry["lab"],
            test_origin=base_entry["origin"],
            issue_id=base_entry["issue_id"],
            issue_version=base_entry["issue_version"],
            issue_uncategorized=base_entry["issue_uncategorized"],
            is_boot=base_entry["is_boot"],
        )
        rollup_data = {
            rollup_key: {
                "pass_tests": 0,
                "fail_tests": 0,
                "skip_tests": 0,
                "error_tests": 0,
                "miss_tests": 0,
                "done_tests": 0,
                "null_tests": 3,
                "total_tests": 3,
            }
        }

        # Three corrections: PASS, FAIL, SKIP
        entry1 = _make_rollup_entry(checkout=checkout, status=StatusChoices.PASS)
        entry2 = _make_rollup_entry(checkout=checkout, status=StatusChoices.FAIL)
        entry3 = _make_rollup_entry(checkout=checkout, status=StatusChoices.SKIP)

        accumulate_rollup_entry(rollup_data, entry1, is_correction=True)
        accumulate_rollup_entry(rollup_data, entry2, is_correction=True)
        accumulate_rollup_entry(rollup_data, entry3, is_correction=True)

        record = rollup_data[rollup_key]
        self.assertEqual(record["null_tests"], 0)
        self.assertEqual(record["pass_tests"], 1)
        self.assertEqual(record["fail_tests"], 1)
        self.assertEqual(record["skip_tests"], 1)
        self.assertEqual(record["total_tests"], 3)


class TestAggregateTestsRollupWithReprocess(SimpleTestCase):
    """Test aggregate_tests_rollup with reprocess_test_ids parameter."""

    def test_reprocess_test_id_applies_correction(self):
        """Test in reprocess_test_ids gets correction: null_tests decremented."""
        checkout = _make_checkout()
        build = _make_build(checkout=checkout)
        # This test will be marked as reprocess
        test = _make_pending_test(
            test_id="test-1",
            build_id="build-1",
            full_status=StatusChoices.PASS,
        )

        result = aggregate_tests_rollup(
            [test],
            {"build-1": build},
            {},
            reprocess_test_ids={"test-1"},  # Mark as correction
        )

        record = next(iter(result.values()))
        # Correction: total should not increment, pass_tests should be 1
        # But since there's no prior null_tests to decrement, it goes negative
        self.assertEqual(record["pass_tests"], 1)
        self.assertEqual(record["null_tests"], -1)
        self.assertEqual(record["total_tests"], 0)

    def test_normal_test_not_in_reprocess(self):
        """Test not in reprocess_test_ids behaves like normal."""
        checkout = _make_checkout()
        build = _make_build(checkout=checkout)
        test = _make_pending_test(
            test_id="test-1",
            build_id="build-1",
            full_status=StatusChoices.PASS,
        )

        result = aggregate_tests_rollup(
            [test],
            {"build-1": build},
            {},
            reprocess_test_ids=set(),  # Empty set
        )

        record = next(iter(result.values()))
        self.assertEqual(record["pass_tests"], 1)
        self.assertEqual(record["total_tests"], 1)
        self.assertEqual(record["null_tests"], 0)

    def test_mixed_batch_corrections_and_new(self):
        """Two tests same rollup key: one correction + one normal."""
        checkout = _make_checkout()
        build = _make_build(checkout=checkout)
        # Correction: was counted as null, now becoming PASS
        test_correction = _make_pending_test(
            test_id="t1",
            build_id="build-1",
            full_status=StatusChoices.PASS,
        )
        # New test, fresh PASS
        test_new = _make_pending_test(
            test_id="t2",
            build_id="build-1",
            full_status=StatusChoices.PASS,
        )

        result = aggregate_tests_rollup(
            [test_correction, test_new],
            {"build-1": build},
            {},
            reprocess_test_ids={"t1"},  # Only first is correction
        )

        self.assertEqual(len(result), 1)
        record = next(iter(result.values()))
        # Correction: null_tests -1, pass_tests +1, total_tests 0
        # New: pass_tests +1, total_tests +1
        # Result: null_tests -1, pass_tests 2, total_tests 1
        self.assertEqual(record["null_tests"], -1)
        self.assertEqual(record["pass_tests"], 2)
        self.assertEqual(record["total_tests"], 1)

    def test_default_reprocess_test_ids_is_empty(self):
        """Not passing reprocess_test_ids defaults to empty set."""
        checkout = _make_checkout()
        build = _make_build(checkout=checkout)
        test = _make_pending_test(
            test_id="test-1",
            build_id="build-1",
            full_status=StatusChoices.FAIL,
        )

        # Call without the reprocess_test_ids parameter
        result = aggregate_tests_rollup([test], {"build-1": build}, {})

        record = next(iter(result.values()))
        self.assertEqual(record["fail_tests"], 1)
        self.assertEqual(record["total_tests"], 1)
        self.assertEqual(record["null_tests"], 0)
