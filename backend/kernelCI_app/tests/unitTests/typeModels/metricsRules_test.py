import tempfile
import unittest
from pathlib import Path

from kernelCI_app.typeModels.metricsRules import (
    MetricsRuleError,
    load_metrics_rules,
    metrics_rules_dir,
)


def _write(directory: Path, name: str, text: str) -> None:
    (directory / name).write_text(text)


class TestLoadMetricsRules(unittest.TestCase):
    def test_valid_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            _write(
                directory,
                "collabora.yaml",
                """
collabora-labs:
  origins: [maestro]
  labs: [lava-collabora]
  period_days: 7
  to: ["Collabora team <team@example.com>"]
second:
  period_days: 14
  to: [other@example.com]
""",
            )
            loaded = load_metrics_rules(directory)

        self.assertEqual(loaded[0].origins, ["maestro"])
        self.assertEqual(loaded[0].labs, ["lava-collabora"])
        self.assertEqual(loaded[0].period_days, 7)
        self.assertEqual(loaded[0].to, ["Collabora team <team@example.com>"])
        self.assertIsNone(loaded[1].origins)
        self.assertIsNone(loaded[1].labs)
        self.assertEqual(loaded[1].period_days, 14)

    def test_invalid_rule_files(self):
        cases = [
            (
                {
                    "a.yaml": "shared:\n  period_days: 7\n  to: [a@example.com]\n",
                    "b.yaml": "shared:\n  period_days: 7\n  to: [b@example.com]\n",
                },
                "b.yaml",
                "shared",
                "shared",
            ),
            (
                {
                    "a.yaml": (
                        "shared:\n  period_days: 7\n  to: [a@example.com]\n"
                        "shared:\n  period_days: 8\n  to: [b@example.com]\n"
                    )
                },
                "a.yaml",
                "shared",
                "shared",
            ),
            (
                {
                    "a.yaml": "rule:\n  period_days: 7\n  to: [a@example.com]\n  window: 7\n"
                },
                "a.yaml",
                "rule",
                "window",
            ),
            (
                {"a.yaml": "rule:\n  period_days: 7\n  to: []\n"},
                "a.yaml",
                "rule",
                "to",
            ),
            (
                {"a.yaml": 'rule:\n  period_days: 7\n  to: [""]\n'},
                "a.yaml",
                "rule",
                "to",
            ),
            (
                {"a.yaml": "rule:\n  period_days: 0\n  to: [a@example.com]\n"},
                "a.yaml",
                "rule",
                "period_days",
            ),
            (
                {"a.yaml": "rule:\n  period_days: 7\n  to: [not-an-address]\n"},
                "a.yaml",
                "rule",
                "to",
            ),
            (
                {"a.yaml": 'rule:\n  period_days: 7\n  to: ["a@b.com, c@d.com"]\n'},
                "a.yaml",
                "rule",
                "to",
            ),
        ]
        for files, file, rule, key in cases:
            with self.subTest(file=file, key=key):
                with tempfile.TemporaryDirectory() as tmp:
                    directory = Path(tmp)
                    for name, text in files.items():
                        _write(directory, name, text)
                    with self.assertRaises(MetricsRuleError) as caught:
                        load_metrics_rules(directory)
                self.assertEqual(caught.exception.file, file)
                self.assertEqual(caught.exception.rule, rule)
                self.assertEqual(caught.exception.key, key)

    def test_committed_metrics_directory_is_valid(self):
        directory = metrics_rules_dir()
        self.assertTrue(directory.is_dir())
        load_metrics_rules(directory)
        self.assertEqual(load_metrics_rules(directory / "missing"), [])
