from unittest.mock import patch, MagicMock
from datetime import datetime
from kernelCI_app.tasks import (
    _is_checkout_done,
    _is_checkout_unstable,
    get_checkout_ids_for_update,
    update_checkout_cache,
    UPDATE_INTERVAL_IN_DAYS,
)
from kernelCI_app.models import Checkouts


class TestIsCheckoutDone:
    def test_is_checkout_done_with_checkout_model(self):
        """Test _is_checkout_done with Checkouts model instance."""
        mock_checkout = MagicMock(spec=Checkouts)
        mock_checkout.origin_builds_finish_time = datetime.now()
        mock_checkout.origin_tests_finish_time = datetime.now()
        result = _is_checkout_done(checkout=mock_checkout)

        assert result is True

    def test_is_checkout_done_with_dict(self):
        """Test _is_checkout_done with dictionary."""
        checkout_dict = {
            "origin_builds_finish_time": datetime.now(),
            "origin_tests_finish_time": datetime.now(),
        }

        result = _is_checkout_done(checkout=checkout_dict)

        assert result is True

    def test_is_checkout_done_missing_builds_time(self):
        """Test _is_checkout_done when builds finish time is None."""
        mock_checkout = MagicMock(spec=Checkouts)
        mock_checkout.origin_builds_finish_time = None
        mock_checkout.origin_tests_finish_time = datetime.now()

        result = _is_checkout_done(checkout=mock_checkout)

        assert result is False

    def test_is_checkout_done_missing_tests_time(self):
        """Test _is_checkout_done when tests finish time is None."""
        mock_checkout = MagicMock(spec=Checkouts)
        mock_checkout.origin_builds_finish_time = datetime.now()
        mock_checkout.origin_tests_finish_time = None

        result = _is_checkout_done(checkout=mock_checkout)

        assert result is False

    def test_is_checkout_done_both_times_none(self):
        """Test _is_checkout_done when both times are None."""
        checkout_dict = {
            "origin_builds_finish_time": None,
            "origin_tests_finish_time": None,
        }

        result = _is_checkout_done(checkout=checkout_dict)

        assert result is False


class TestIsCheckoutUnstable:
    @patch("kernelCI_app.tasks.now")
    def test_is_checkout_unstable_with_checkout_model_done(self, mock_now):
        """Test _is_checkout_unstable with done checkout."""
        mock_now.return_value = datetime(2024, 1, 15, 12, 0, 0)
        mock_checkout = MagicMock(spec=Checkouts)
        mock_checkout.start_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_checkout.origin_builds_finish_time = datetime.now()
        mock_checkout.origin_tests_finish_time = datetime.now()

        with patch("kernelCI_app.tasks._is_checkout_done", return_value=True):
            result = _is_checkout_unstable(checkout=mock_checkout)

        assert result is False

    @patch("kernelCI_app.tasks.now")
    def test_is_checkout_unstable_with_dict_done(self, mock_now):
        """Test _is_checkout_unstable with done checkout dict."""
        mock_now.return_value = datetime(2024, 1, 15, 12, 0, 0)
        checkout_dict = {
            "start_time": datetime(2024, 1, 1, 12, 0, 0),
            "origin_builds_finish_time": datetime.now(),
            "origin_tests_finish_time": datetime.now(),
        }

        with patch("kernelCI_app.tasks._is_checkout_done", return_value=True):
            result = _is_checkout_unstable(checkout=checkout_dict)

        assert result is False

    @patch("kernelCI_app.tasks.now")
    def test_is_checkout_unstable_old_checkout(self, mock_now):
        """Test _is_checkout_unstable with old checkout."""
        mock_now.return_value = datetime(2024, 1, 15, 12, 0, 0)
        mock_checkout = MagicMock(spec=Checkouts)
        mock_checkout.start_time = datetime(2023, 1, 1, 12, 0, 0)  # Very old
        mock_checkout.origin_builds_finish_time = None
        mock_checkout.origin_tests_finish_time = None

        with patch("kernelCI_app.tasks._is_checkout_done", return_value=False):
            result = _is_checkout_unstable(checkout=mock_checkout)

        assert result is False

    @patch("kernelCI_app.tasks.now")
    def test_is_checkout_unstable_recent_unfinished(self, mock_now):
        """Test _is_checkout_unstable with recent unfinished checkout."""
        mock_now.return_value = datetime(2024, 1, 15, 12, 0, 0)
        mock_checkout = MagicMock(spec=Checkouts)
        mock_checkout.start_time = datetime(2024, 1, 14, 12, 0, 0)  # Recent
        mock_checkout.origin_builds_finish_time = None
        mock_checkout.origin_tests_finish_time = None

        with patch("kernelCI_app.tasks._is_checkout_done", return_value=False):
            result = _is_checkout_unstable(checkout=mock_checkout)

        assert result is True

    @patch("kernelCI_app.tasks.now")
    def test_is_checkout_unstable_none_start_time(self, mock_now):
        """Test _is_checkout_unstable with None start_time."""
        mock_now.return_value = datetime(2024, 1, 15, 12, 0, 0)
        mock_checkout = MagicMock(spec=Checkouts)
        mock_checkout.start_time = None
        mock_checkout.origin_builds_finish_time = None
        mock_checkout.origin_tests_finish_time = None

        with patch("kernelCI_app.tasks._is_checkout_done", return_value=False):
            result = _is_checkout_unstable(checkout=mock_checkout)

        assert result is True


class TestGetCheckoutIdsForUpdate:
    def test_get_checkout_ids_for_update_no_cache_origins(self):
        """Test that NO_CACHE_ORIGINS are skipped."""
        mock_checkout = MagicMock(spec=Checkouts)
        mock_checkout.origin = "broonie"
        mock_checkout.id = "checkout1"

        result = get_checkout_ids_for_update(
            kcidb_checkouts=[mock_checkout],
            sqlite_tree_keys=set(),
            sqlite_trees_map={},
        )

        assert result == set()

    def test_get_checkout_ids_for_update_new_tree(self):
        """Test that new trees are added to update list."""
        mock_checkout = MagicMock(spec=Checkouts)
        mock_checkout.origin = "valid_origin"
        mock_checkout.id = "checkout1"
        mock_checkout.tree_name = "tree1"
        mock_checkout.git_repository_branch = "branch1"
        mock_checkout.git_repository_url = "url1"

        result = get_checkout_ids_for_update(
            kcidb_checkouts=[mock_checkout],
            sqlite_tree_keys=set(),
            sqlite_trees_map={},
        )

        assert result == {"checkout1"}

    def test_get_checkout_ids_for_update_unstable_sqlite_tree(self):
        """Test that unstable sqlite trees are updated."""
        mock_checkout = MagicMock(spec=Checkouts)
        mock_checkout.origin = "valid_origin"
        mock_checkout.id = "checkout1"
        mock_checkout.tree_name = "tree1"
        mock_checkout.git_repository_branch = "branch1"
        mock_checkout.git_repository_url = "url1"
        mock_checkout.start_time = None

        tree_key = ("tree1", "branch1", "url1")
        sqlite_trees_map = {
            tree_key: {"unstable": True, "checkout_id": "sqlite_checkout1"}
        }

        result = get_checkout_ids_for_update(
            kcidb_checkouts=[mock_checkout],
            sqlite_tree_keys={tree_key},
            sqlite_trees_map=sqlite_trees_map,
        )

        assert "sqlite_checkout1" in result

    def test_get_checkout_ids_for_update_unstable_checkout(self):
        """Test that unstable checkouts are updated."""
        mock_checkout = MagicMock(spec=Checkouts)
        mock_checkout.origin = "valid_origin"
        mock_checkout.id = "checkout1"
        mock_checkout.tree_name = "tree1"
        mock_checkout.git_repository_branch = "branch1"
        mock_checkout.git_repository_url = "url1"

        tree_key = ("tree1", "branch1", "url1")
        sqlite_trees_map = {
            tree_key: {"unstable": False, "checkout_id": "sqlite_checkout1"}
        }

        with patch("kernelCI_app.tasks._is_checkout_unstable", return_value=True):
            result = get_checkout_ids_for_update(
                kcidb_checkouts=[mock_checkout],
                sqlite_tree_keys={tree_key},
                sqlite_trees_map=sqlite_trees_map,
            )

        assert "checkout1" in result

    def test_get_checkout_ids_for_update_newer_checkout(self):
        """Test that newer checkouts are updated."""
        mock_checkout = MagicMock(spec=Checkouts)
        mock_checkout.origin = "valid_origin"
        mock_checkout.id = "checkout1"
        mock_checkout.tree_name = "tree1"
        mock_checkout.git_repository_branch = "branch1"
        mock_checkout.git_repository_url = "url1"
        mock_checkout.start_time = datetime(2024, 1, 15, 12, 0, 0)

        tree_key = ("tree1", "branch1", "url1")
        sqlite_trees_map = {
            tree_key: {
                "unstable": False,
                "checkout_id": "sqlite_checkout1",
                "start_time": datetime(2024, 1, 14, 12, 0, 0),
            }
        }

        with patch("kernelCI_app.tasks._is_checkout_unstable", return_value=False):
            result = get_checkout_ids_for_update(
                kcidb_checkouts=[mock_checkout],
                sqlite_tree_keys={tree_key},
                sqlite_trees_map=sqlite_trees_map,
            )

        assert "checkout1" in result


class TestUpdateCheckoutCache:
    @patch("kernelCI_app.tasks._is_checkout_unstable")
    @patch("kernelCI_app.tasks.populate_checkouts_cache_db")
    @patch("kernelCI_app.tasks.get_tree_listing_data_by_checkout_id")
    @patch("kernelCI_app.tasks.get_cached_tree_listing_fast")
    @patch("kernelCI_app.tasks.get_tree_listing_fast")
    @patch("kernelCI_app.tasks.get_checkout_ids_for_update")
    def test_update_checkout_cache_with_sqlite_data(
        self,
        mock_get_checkout_ids,
        mock_get_tree_listing_fast,
        mock_get_cached_tree_listing_fast,
        mock_get_tree_listing_data_by_checkout_id,
        mock_populate_checkouts_cache_db,
        mock_is_checkout_unstable,
    ):
        """Test the main update_checkout_cache function with sqlite_checkouts."""
        mock_get_tree_listing_fast.return_value = []
        mock_get_cached_tree_listing_fast.return_value = [
            {
                "tree_name": "test_tree",
                "git_repository_branch": "main",
                "git_repository_url": "https://git.example.com/test.git",
                "checkout_id": "sqlite_checkout1",
                "unstable": False,
            },
            {
                "tree_name": "another_tree",
                "git_repository_branch": "develop",
                "git_repository_url": "https://git.example.com/another.git",
                "checkout_id": "sqlite_checkout2",
                "unstable": True,
            },
        ]
        mock_get_checkout_ids.return_value = {"checkout1", "checkout2"}
        mock_get_tree_listing_data_by_checkout_id.return_value = [
            {"id": "checkout1"},
            {"id": "checkout2"},
        ]

        def mock_unstable_side_effect(checkout):
            if checkout["id"] == "checkout1":
                return False
            elif checkout["id"] == "checkout2":
                return True
            return False

        mock_is_checkout_unstable.side_effect = mock_unstable_side_effect

        update_checkout_cache()

        mock_get_tree_listing_fast.assert_called_once_with(
            interval={"days": UPDATE_INTERVAL_IN_DAYS}
        )
        mock_get_cached_tree_listing_fast.assert_called_once()
        mock_get_checkout_ids.assert_called_once()

        call_args = mock_get_checkout_ids.call_args[1]
        assert "kcidb_checkouts" in call_args
        assert "sqlite_tree_keys" in call_args
        assert "sqlite_trees_map" in call_args

        sqlite_tree_keys = call_args["sqlite_tree_keys"]
        expected_keys = {
            ("test_tree", "main", "https://git.example.com/test.git"),
            ("another_tree", "develop", "https://git.example.com/another.git"),
        }
        assert sqlite_tree_keys == expected_keys

        sqlite_trees_map = call_args["sqlite_trees_map"]
        assert len(sqlite_trees_map) == 2
        assert (
            "test_tree",
            "main",
            "https://git.example.com/test.git",
        ) in sqlite_trees_map
        assert (
            "another_tree",
            "develop",
            "https://git.example.com/another.git",
        ) in sqlite_trees_map

        mock_get_tree_listing_data_by_checkout_id.assert_called_once()
        mock_populate_checkouts_cache_db.assert_called_once()
