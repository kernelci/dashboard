from datetime import date, datetime, timezone

from django.test import SimpleTestCase

from kernelCI_app.helpers.lab_details import (
    build_lab_attention_response,
    build_lab_details_response,
    parse_tree_filters,
    tree_key,
)


class LabDetailsHelperTest(SimpleTestCase):
    def test_parse_tree_filters(self):
        self.assertIsNone(parse_tree_filters([]))
        self.assertEqual(
            parse_tree_filters(["mainline/master", "next/master"]),
            {("mainline", "master"), ("next", "master")},
        )
        self.assertIsNone(parse_tree_filters(["invalid"]))

    def test_build_lab_details_response_aggregates_one_tree(self):
        when = datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc)
        build_rows = [
            {
                "build_id": "b1",
                "build_status": "PASS",
                "build_start_time": when,
                "build_duration": 10.0,
                "build_architecture": "arm64",
                "build_compiler": "gcc-14",
                "build_config_name": "defconfig",
                "tree_name": "mainline",
                "git_branch": "master",
                "commit_hash": "abc",
                "commit_name": "v1",
                "incident_test_id": None,
                "issue_id": None,
                "issue_version": None,
            }
        ]
        build_rows.append(dict(build_rows[0]))
        test_rows = [
            {
                "test_id": "t1",
                "test_status": "FAIL",
                "test_path": "boot",
                "test_start_time": when,
                "test_duration": None,
                "test_log_url": "http://log",
                "test_log_excerpt": None,
                "test_environment_misc": {"platform": "board-a"},
                "build_config_name": "defconfig",
                "build_architecture": "arm64",
                "build_compiler": "gcc-14",
                "tree_name": "mainline",
                "git_branch": "master",
                "commit_hash": "abc",
                "commit_name": "v1",
                "incident_test_id": None,
                "issue_id": None,
                "issue_version": None,
            }
        ]
        test_rows.append(dict(test_rows[0]))
        result = build_lab_details_response(
            lab_name="lava-demo",
            interval_in_days=7,
            build_rows=build_rows,
            test_rows=test_rows,
        )
        self.assertEqual(result.lab_name, "lava-demo")
        self.assertEqual(len(result.trees), 1)
        tree = result.trees[0]
        self.assertEqual(tree.key, tree_key("mainline", "master"))
        self.assertEqual(tree.builds.PASS, 1)
        self.assertEqual(tree.boots.FAIL, 1)
        self.assertEqual(result.fill.checkout_total, 1)
        self.assertEqual(result.fill.checkouts_built, 1)
        self.assertEqual(result.fill.checkouts_booted, 1)
        self.assertEqual(result.fill.builds_total, 1)
        self.assertEqual(result.fill.builds_with_duration, 1)
        self.assertEqual(result.fill.runs_total, 1)
        self.assertEqual(result.distribution.build_status.PASS, 1)
        self.assertEqual(result.distribution.boot_status.FAIL, 1)
        self.assertEqual(result.distribution.platforms[0].name, "board-a")
        self.assertEqual(result.distribution.platforms[0].count, 1)

    def test_attention_boot_path_and_sorted_labs(self):
        row = {
            "kind": "boot",
            "path": "boot.nfs",
            "platform": "board-a",
            "tree_name": "mainline",
            "git_branch": "master",
            "commit_name": "v1",
            "commit_hash": "abc",
            "config_name": "defconfig",
            "architecture": "arm64",
            "compiler": "gcc",
            "last_failure_date": date(2026, 10, 21),
            "passed_labs": ["lab-b", "lab-a"],
        }
        result = build_lab_attention_response(
            [
                row,
                dict(row, kind="test", path="kselftest.rtc", passed_labs=["lab-c"]),
            ]
        )
        self.assertEqual(result.items[0].path, "boot")
        self.assertEqual(result.items[0].passed_labs, ["lab-a", "lab-b"])
        self.assertEqual(result.items[1].kind, "test")
        self.assertEqual(result.items[1].path, "kselftest.rtc")
