from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from kernelCI_app.queries.tree import (
    get_tree_compare_builds,
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
        self.assertNotIn("known_issues", executed_query)
        self.assertNotIn("SELECT\n            b.id AS build_id", executed_query)
