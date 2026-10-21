from unittest.mock import patch

from django.core.cache import cache

from kernelCI_app.cache import (
    DISCORD_NOTIFICATION_COOLDOWN,
    DISCORD_NOTIFICATION_KEY,
    _add_to_lookup,
    _create_cache_params_hash,
    clear_cache,
    get_notification_cache,
    get_query_cache,
    set_notification_cache,
    set_query_cache,
)


class TestCreateCacheParamsHash:
    def test_create_cache_params_hash_with_params(self):
        """Test hash creation with parameters."""
        params = {"key1": "value1", "key2": "value2"}
        hash1 = _create_cache_params_hash(params)
        hash2 = _create_cache_params_hash(params)
        assert hash1 == hash2

    def test_create_cache_params_hash_different_order(self):
        """Test that hash is consistent regardless of parameter order."""
        params1 = {"key1": "value1", "key2": "value2"}
        params2 = {"key2": "value2", "key1": "value1"}
        hash1 = _create_cache_params_hash(params1)
        hash2 = _create_cache_params_hash(params2)
        assert hash1 == hash2

    def test_create_cache_params_hash_different_values(self):
        """Test that different parameter values produce different hashes."""
        params1 = {"key1": "value1"}
        params2 = {"key1": "value2"}
        hash1 = _create_cache_params_hash(params1)
        hash2 = _create_cache_params_hash(params2)
        assert hash1 != hash2


class TestSetQueryCache:
    @patch("kernelCI_app.cache.cache")
    def test_set_query_cache_with_params(self, mock_cache):
        """Test setting cache with parameters."""
        key = "test_key"
        params = {"param1": "value1"}
        rows = ["row1", "row2"]

        set_query_cache(key=key, params=params, rows=rows)

        mock_cache.set.assert_called_once()
        call_args = mock_cache.set.call_args
        assert call_args[0][0].startswith("test_key-")
        assert call_args[0][1] == rows

    @patch("kernelCI_app.cache.cache")
    def test_set_query_cache_without_params(self, mock_cache):
        """Test setting cache without parameters."""
        key = "test_key"
        rows = ["row1", "row2"]

        set_query_cache(key=key, rows=rows)

        mock_cache.set.assert_called_once_with(
            key, rows, mock_cache.set.call_args[0][2]
        )

    @patch("kernelCI_app.cache.cache")
    def test_set_query_cache_with_lookup_keys(self, mock_cache):
        """Test setting cache with lookup keys."""
        key = "test_key"
        rows = ["row1", "row2"]
        commit_hash = "commit123"
        build_id = "build456"
        test_id = "test789"

        set_query_cache(
            key=key,
            rows=rows,
            commit_hash=commit_hash,
            build_id=build_id,
            test_id=test_id,
        )

        mock_cache.set.assert_called_once()


class TestGetQueryCache:
    @patch("kernelCI_app.cache.cache")
    def test_get_query_cache_with_params(self, mock_cache):
        """Test getting cache with parameters."""
        key = "test_key"
        params = {"param1": "value1"}
        expected_data = ["row1", "row2"]
        mock_cache.get.return_value = expected_data

        result = get_query_cache(key, params)

        assert result == expected_data
        mock_cache.get.assert_called_once()
        call_args = mock_cache.get.call_args[0][0]
        assert call_args.startswith("test_key-")

    @patch("kernelCI_app.cache.cache")
    def test_get_query_cache_without_params(self, mock_cache):
        """Test getting cache without parameters."""
        key = "test_key"
        expected_data = ["row1", "row2"]
        mock_cache.get.return_value = expected_data

        result = get_query_cache(key)

        assert result == expected_data
        mock_cache.get.assert_called_once_with(key)

    @patch("kernelCI_app.cache.cache")
    def test_get_query_cache_returns_none(self, mock_cache):
        """Test getting cache when no data exists."""
        key = "test_key"
        mock_cache.get.return_value = None

        result = get_query_cache(key)

        assert result is None


class TestSetNotificationCache:
    @patch("kernelCI_app.cache.cache")
    def test_set_notification_cache(self, mock_cache):
        """Test setting notification cache."""
        notification = "test notification"

        set_notification_cache(notification=notification)

        mock_cache.set.assert_called_once()
        call_args = mock_cache.set.call_args
        assert call_args[0][0].startswith(f"{DISCORD_NOTIFICATION_KEY}-")
        assert call_args[0][1] == notification
        assert call_args[0][2] == DISCORD_NOTIFICATION_COOLDOWN

    @patch("kernelCI_app.cache.cache")
    def test_set_notification_cache_different_notifications(self, mock_cache):
        """Test that different notifications get different cache keys."""
        notification1 = "notification 1"
        notification2 = "notification 2"

        set_notification_cache(notification=notification1)
        set_notification_cache(notification=notification2)

        assert mock_cache.set.call_count == 2
        call1_key = mock_cache.set.call_args_list[0][0][0]
        call2_key = mock_cache.set.call_args_list[1][0][0]
        assert call1_key != call2_key


class TestGetNotificationCache:
    @patch("kernelCI_app.cache.cache")
    def test_get_notification_cache(self, mock_cache):
        """Test getting notification cache."""
        notification = "test notification"
        expected_data = "cached notification"
        mock_cache.get.return_value = expected_data

        result = get_notification_cache(notification=notification)

        assert result == expected_data
        mock_cache.get.assert_called_once()
        call_args = mock_cache.get.call_args[0][0]
        assert call_args.startswith(f"{DISCORD_NOTIFICATION_KEY}-")

    @patch("kernelCI_app.cache.cache")
    def test_get_notification_cache_returns_none(self, mock_cache):
        """Test getting notification cache when no data exists."""
        notification = "test notification"
        mock_cache.get.return_value = None

        result = get_notification_cache(notification=notification)

        assert result is None


class TestAddToLookup:
    def test_add_to_lookup_with_none_property_key(self):
        """Test that None property key returns early."""
        lookup = {}
        _add_to_lookup("cache_key", None, lookup)
        assert lookup == {}

    def test_add_to_lookup_new_property_key(self):
        """Test adding to lookup with new property key."""
        lookup = {}
        cache_key = "cache_key"
        property_key = "property_key"

        _add_to_lookup(cache_key, property_key, lookup)

        assert property_key in lookup
        assert list(lookup[property_key]) == [cache_key]

    def test_add_to_lookup_existing_property_key(self):
        """Test adding to lookup with existing property key."""
        lookup = {"property_key": set(["existing_key"])}
        cache_key = "new_cache_key"
        property_key = "property_key"

        _add_to_lookup(cache_key, property_key, lookup)

        assert "new_cache_key" in lookup[property_key]
        assert "existing_key" in lookup[property_key]

    def test_add_to_lookup_multiple_calls(self):
        """Test multiple calls to add_to_lookup."""
        lookup = {}
        property_key = "property_key"

        _add_to_lookup("key1", property_key, lookup)
        _add_to_lookup("key2", property_key, lookup)
        _add_to_lookup("key3", property_key, lookup)

        assert "key1" in lookup[property_key]
        assert "key2" in lookup[property_key]
        assert "key3" in lookup[property_key]


class TestClearCache:
    def setup_method(self):
        cache.clear()

    def test_clear_one_parameter_set(self):
        five_days = {"origin": "maestro", "interval_in_days": 5}
        seven_days = {"origin": "maestro", "interval_in_days": 7}
        set_query_cache(key="labListing", params=five_days, rows=[1])
        set_query_cache(key="labListing", params=seven_days, rows=[2])

        clear_cache("labListing", five_days)

        assert get_query_cache("labListing", five_days) is None
        assert get_query_cache("labListing", seven_days) == [2]

    def test_clear_every_parameter_set(self):
        set_query_cache(key="labListing", params={"origin": "maestro"}, rows=[1])
        set_query_cache(key="labListing", params={"origin": "broonie"}, rows=[2])
        set_query_cache(key="labListingOther", params={"origin": "maestro"}, rows=[3])
        set_query_cache(key="lab_origins_query_5", rows=["maestro"])

        clear_cache("labListing")

        assert get_query_cache("labListing", {"origin": "maestro"}) is None
        assert get_query_cache("labListing", {"origin": "broonie"}) is None
        assert get_query_cache("labListingOther", {"origin": "maestro"}) == [3]
        assert get_query_cache("lab_origins_query_5") == ["maestro"]

    def test_clear_key_without_parameters(self):
        set_query_cache(key="lab_origins_query_5", rows=["maestro"])

        clear_cache("lab_origins_query_5")

        assert get_query_cache("lab_origins_query_5") is None

    def test_clear_many_lab_listing_parameter_sets(self):
        origins = [
            "maestro",
            "broonie",
            "microsoft",
            "linaro_pull_labs",
            "ti",
            "syzbot",
        ]
        intervals = [1, 5, 7, 14, 30]
        for origin in origins:
            for interval in intervals:
                params = {"origin": origin, "interval_in_days": interval}
                set_query_cache(
                    key="labListing", params=params, rows=[origin, interval]
                )

        set_query_cache(key="treeListing", params={"origin": "maestro"}, rows=["keep"])
        set_query_cache(key="lab_origins_query_5", rows=["maestro"])

        one = {"origin": "maestro", "interval_in_days": 5}
        clear_cache("labListing", one)
        assert get_query_cache("labListing", one) is None
        assert get_query_cache(
            "labListing", {"origin": "broonie", "interval_in_days": 5}
        ) == ["broonie", 5]

        clear_cache("labListing")
        for origin in origins:
            for interval in intervals:
                assert (
                    get_query_cache(
                        "labListing",
                        {"origin": origin, "interval_in_days": interval},
                    )
                    is None
                )
        assert get_query_cache("treeListing", {"origin": "maestro"}) == ["keep"]
        assert get_query_cache("lab_origins_query_5") == ["maestro"]
