from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from kernelCI_app.queries.tree import (
    get_tree_compare_boots_change_counts,
    get_tree_compare_boots_tests_diff,
    get_tree_compare_builds,
    get_tree_compare_builds_change_counts,
    get_tree_compare_builds_diff,
    get_tree_compare_rollup,
)


class TestTreeCompareQueries(SimpleTestCase):
    """Query-shape checks for the compare endpoint performance path."""

    @patch("kernelCI_app.queries.tree.connection")
    @patch("kernelCI_app.queries.tree.get_query_cache", return_value=None)
    @patch("kernelCI_app.queries.tree.set_query_cache")
    @patch("kernelCI_app.queries.tree.dict_fetchall", return_value=[])
    def test_compare_rollup_uses_single_any_query(
        self,
        mock_fetchall,
        mock_set_cache,
        mock_get_cache,
        mock_connection,
    ):
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        get_tree_compare_rollup(
            commit_hashes=["hash_a", "hash_b"],
            origin_param="maestro",
            git_branch_param="master",
            tree_name="linux",
        )

        executed_query = mock_cursor.execute.call_args[0][0]
        params = mock_cursor.execute.call_args[0][1]
        self.assertIn("git_commit_hash = ANY(%(commit_hashes)s)", executed_query)
        self.assertIn("DISTINCT ON (c.git_commit_hash)", executed_query)
        self.assertIn("tree_tests_rollup", executed_query)
        self.assertNotIn("git_url_param", params)

    @patch("kernelCI_app.queries.tree.connection")
    @patch("kernelCI_app.queries.tree.get_query_cache", return_value=None)
    @patch("kernelCI_app.queries.tree.set_query_cache")
    @patch("kernelCI_app.queries.tree.dict_fetchall", return_value=[])
    def test_compare_builds_aggregates_in_sql(
        self,
        mock_fetchall,
        mock_set_cache,
        mock_get_cache,
        mock_connection,
    ):
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        get_tree_compare_builds(
            commit_hashes=["hash_a", "hash_b"],
            origin_param="maestro",
            git_branch_param="master",
            tree_name="linux",
        )

        executed_query = mock_cursor.execute.call_args[0][0]
        self.assertIn("COUNT(DISTINCT b.id)", executed_query)
        self.assertIn("GROUP BY", executed_query)
        self.assertIn("b.architecture", executed_query)
        self.assertNotIn("b.architecture IS NOT NULL", executed_query)
        self.assertNotIn("b.config_name", executed_query)
        self.assertNotIn("known_issues", executed_query)
        self.assertNotIn("SELECT\n            b.id AS build_id", executed_query)

    @patch("kernelCI_app.queries.tree.connection")
    @patch("kernelCI_app.queries.tree.get_query_cache", return_value=None)
    @patch("kernelCI_app.queries.tree.set_query_cache")
    @patch("kernelCI_app.queries.tree.dict_fetchall", return_value=[])
    def test_compare_builds_diff_joins_and_diffs_in_sql(
        self,
        mock_fetchall,
        mock_set_cache,
        mock_get_cache,
        mock_connection,
    ):
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        get_tree_compare_builds_diff(
            hash_a="hash_a",
            hash_b="hash_b",
            origin_param="maestro",
            git_branch_param="master",
            tree_name="linux",
        )

        executed_query = mock_cursor.execute.call_args[0][0]
        params = mock_cursor.execute.call_args[0][1]
        self.assertIn("NULLIF(b.config_name, '')", executed_query)
        self.assertIn("NULLIF(b.architecture, '')", executed_query)
        self.assertIn("NULLIF(b.compiler, '')", executed_query)
        self.assertIn("FULL OUTER JOIN", executed_query)
        self.assertIn("IS DISTINCT FROM", executed_query)
        self.assertIn("a.grouped_status = 'FAIL'", executed_query)
        self.assertIn("WHEN UPPER(b.status) = 'PASS' THEN 'PASS'", executed_query)
        self.assertIn("WHEN UPPER(b.status) = 'FAIL' THEN 'FAIL'", executed_query)
        self.assertIn("ELSE 'INCONCLUSIVE'", executed_query)
        self.assertNotIn("incidents", executed_query)
        self.assertNotIn("FROM tests", executed_query)
        self.assertIn("AS id_a", executed_query)
        self.assertIn("AS id_b", executed_query)
        self.assertEqual(params["commit_hashes"], ["hash_a", "hash_b"])

    @patch("kernelCI_app.queries.tree.connection")
    @patch("kernelCI_app.queries.tree.get_query_cache", return_value=None)
    @patch("kernelCI_app.queries.tree.set_query_cache")
    @patch(
        "kernelCI_app.queries.tree.dict_fetchall",
        return_value=[
            {
                "regression": 1,
                "fixed": 0,
                "new_failure": 2,
                "still_failing": 3,
                "new_pass": 4,
                "appeared": 5,
                "disappeared": 6,
            }
        ],
    )
    def test_compare_builds_change_counts_aggregates_categories(
        self,
        mock_fetchall,
        mock_set_cache,
        mock_get_cache,
        mock_connection,
    ):
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        result = get_tree_compare_builds_change_counts(
            hash_a="hash_a",
            hash_b="hash_b",
            origin_param="maestro",
            git_branch_param="master",
            tree_name="linux",
        )

        executed_query = mock_cursor.execute.call_args[0][0]
        self.assertIn("COUNT(*) FILTER", executed_query)
        self.assertIn("still_failing", executed_query)
        self.assertIn("appeared", executed_query)
        self.assertIn("disappeared", executed_query)
        self.assertIn("FULL OUTER JOIN", executed_query)
        self.assertNotIn("IS DISTINCT FROM", executed_query)
        self.assertEqual(result["regression"], 1)
        self.assertEqual(result["still_failing"], 3)
        self.assertEqual(result["appeared"], 5)
        self.assertEqual(result["disappeared"], 6)
        self.assertIn("status_b IN ('FAIL', 'INCONCLUSIVE')", executed_query)
        self.assertIn("status_a = 'INCONCLUSIVE'", executed_query)

    @patch("kernelCI_app.queries.tree.connection")
    @patch("kernelCI_app.queries.tree.get_query_cache", return_value=None)
    @patch("kernelCI_app.queries.tree.set_query_cache")
    @patch("kernelCI_app.queries.tree.dict_fetchall", return_value=[])
    def test_compare_boots_change_counts_include_architecture(
        self,
        mock_fetchall,
        mock_set_cache,
        mock_get_cache,
        mock_connection,
    ):
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        get_tree_compare_boots_change_counts(
            hash_a="hash_a",
            hash_b="hash_b",
            origin_param="maestro",
            git_branch_param="master",
            tree_name="linux",
        )

        executed_query = mock_cursor.execute.call_args[0][0]
        self.assertIn("NULLIF(b.architecture, '')", executed_query)
        self.assertIn("a.architecture = b.architecture", executed_query)
        self.assertIn("t.path = 'boot' OR t.path LIKE 'boot.%%'", executed_query)
        self.assertIn("status_b IN ('FAIL', 'INCONCLUSIVE')", executed_query)

    @patch("kernelCI_app.queries.tree.connection")
    @patch("kernelCI_app.queries.tree.get_query_cache", return_value=None)
    @patch("kernelCI_app.queries.tree.set_query_cache")
    @patch("kernelCI_app.queries.tree.dict_fetchall", return_value=[])
    def test_compare_boots_tests_diff_uses_latest_wins_and_diffs_in_sql(
        self,
        mock_fetchall,
        mock_set_cache,
        mock_get_cache,
        mock_connection,
    ):
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        get_tree_compare_boots_tests_diff(
            data_type="tests",
            hash_a="hash_a",
            hash_b="hash_b",
            origin="maestro",
            git_branch="master",
            tree_name="linux",
        )

        executed_query = mock_cursor.execute.call_args[0][0]
        params = mock_cursor.execute.call_args[0][1]
        self.assertIn("git_commit_hash = ANY(%(commit_hashes)s)", executed_query)
        self.assertIn("DISTINCT ON (c.git_commit_hash)", executed_query)
        self.assertIn("DISTINCT ON (", executed_query)
        self.assertIn("t.start_time DESC NULLS LAST", executed_query)
        self.assertIn("FULL OUTER JOIN", executed_query)
        self.assertIn("IS DISTINCT FROM", executed_query)
        self.assertIn("WHEN UPPER(t.status) = 'FAIL' THEN 'FAIL'", executed_query)
        self.assertIn("maestro:dummy_%%", executed_query)
        self.assertIn("NULLIF(b.config_name, '')", executed_query)
        self.assertIn("NULLIF(b.architecture, '')", executed_query)
        self.assertNotIn("WHEN UPPER(t.status) = 'FAIL' THEN 2", executed_query)
        self.assertNotIn("ARRAY_AGG", executed_query)
        self.assertIn("AS id_a", executed_query)
        self.assertIn("AS id_b", executed_query)
        self.assertEqual(params["commit_hashes"], ["hash_a", "hash_b"])
