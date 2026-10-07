from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest
from django.http import HttpResponse
from django.test import RequestFactory

from kernelCI_app.middleware.backendRequestMetricsMiddleware import (
    REQUEST_COUNT_CAP,
    BackendRequestMetricsMiddleware,
    Client,
    get_client_info,
    iter_visitor_request_keys,
    publish_visitor_requests,
    record_unique_visitor,
    request_count_band,
    resolve_publish_analytics_date,
)

MIDDLEWARE_MODULE = "kernelCI_app.middleware.backendRequestMetricsMiddleware"


def _middleware():
    return BackendRequestMetricsMiddleware(lambda request: HttpResponse())


def _patch_counters(monkeypatch) -> list[str]:
    created: list[str] = []
    monkeypatch.setattr(
        f"{MIDDLEWARE_MODULE}.Counter",
        lambda *args, **kwargs: created.append(args[0]) or MagicMock(),
    )
    monkeypatch.setattr(f"{MIDDLEWARE_MODULE}._metrics", None)
    return created


class TestMiddlewareCall:
    def test_constructing_middleware_does_not_create_counters(self, monkeypatch):
        created = _patch_counters(monkeypatch)
        _middleware()
        assert created == []

    def test_non_api_request_does_not_create_counters(self, monkeypatch):
        created = _patch_counters(monkeypatch)
        _middleware()(RequestFactory().get("/health/"))
        assert created == []

    def test_api_request_creates_counters(self, monkeypatch):
        created = _patch_counters(monkeypatch)
        monkeypatch.setattr(
            f"{MIDDLEWARE_MODULE}.cache.add", lambda *args, **kwargs: False
        )
        _middleware()(
            RequestFactory().get(
                "/api/tree/",
                HTTP_USER_AGENT="Mozilla/5.0",
                REMOTE_ADDR="192.0.2.1",
            )
        )
        assert created == [
            "dashboard_backend_requests_by_client_total",
            "dashboard_unique_visitors_total",
            "dashboard_unique_visitors_by_endpoint_total",
            "dashboard_kci_dev_requests_by_version_total",
            "dashboard_visitors_by_request_count_total",
        ]


@pytest.mark.parametrize(
    ("user_agent", "browser", "os", "device", "client", "kci_dev_version"),
    [
        ("kci-dev/0.1.11", "kci-dev", "unknown", "cli", Client.KCI_DEV, "0.1.11"),
        (
            "kci-dev/0.1.11 (Linux)",
            "kci-dev",
            "Linux",
            "cli",
            Client.KCI_DEV,
            "0.1.11",
        ),
        (
            "kci-dev/0.1.11 (LINUX)",
            "kci-dev",
            "Linux",
            "cli",
            Client.KCI_DEV,
            "0.1.11",
        ),
        (
            "kci-dev/0.1.11 (macos)",
            "kci-dev",
            "macOS",
            "cli",
            Client.KCI_DEV,
            "0.1.11",
        ),
        (
            "kci-dev/0.1.11 (Windows)",
            "kci-dev",
            "Windows",
            "cli",
            Client.KCI_DEV,
            "0.1.11",
        ),
        (
            "kci-dev/0.1.11 (unknown)",
            "kci-dev",
            "unknown",
            "cli",
            Client.KCI_DEV,
            "0.1.11",
        ),
        (
            "kci-dev/0.1.11.dev0 (Linux)",
            "kci-dev",
            "Linux",
            "cli",
            Client.KCI_DEV,
            "0.1.11.dev0",
        ),
        (
            "kci-dev/unknown (Linux)",
            "kci-dev",
            "Linux",
            "cli",
            Client.KCI_DEV,
            "unknown",
        ),
        (
            "kci-dev/not-a-release",
            "kci-dev",
            "unknown",
            "cli",
            Client.KCI_DEV,
            "unknown",
        ),
        ("kci-dev", "kci-dev", "unknown", "cli", Client.KCI_DEV, "unknown"),
        ("", "unknown", "unknown", "unknown", Client.UNKNOWN, None),
        ("kci-devtools/1.0", "unknown", "unknown", "desktop", Client.UNKNOWN, None),
        ("Go-http-client/1.1", "unknown", "unknown", "desktop", Client.UNKNOWN, None),
        ("curl/8.5.0", "curl", "unknown", "script", Client.SCRIPT, None),
        (
            "python-requests/2.32.3",
            "python-requests",
            "unknown",
            "script",
            Client.SCRIPT,
            None,
        ),
        (
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "bot",
            "bot",
            "bot",
            Client.BOT,
            None,
        ),
        (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Chrome",
            "Linux",
            "desktop",
            Client.DASHBOARD,
            None,
        ),
    ],
)
def test_get_client_info(user_agent, browser, os, device, client, kci_dev_version):
    info = get_client_info(user_agent)
    assert info.browser == browser
    assert info.os == os
    assert info.device == device
    assert info.client == client
    assert info.kci_dev_version == kci_dev_version


@pytest.mark.parametrize(
    ("count", "band"),
    [
        (1, "1-5"),
        (5, "1-5"),
        (6, "6-10"),
        (10, "6-10"),
        (11, "11-20"),
        (20, "11-20"),
        (21, "21-50"),
        (50, "21-50"),
        (51, "51-100"),
        (100, "51-100"),
        (101, "101-500"),
        (500, "101-500"),
        (501, "501-999"),
        (999, "501-999"),
        (1000, "1000+"),
    ],
)
def test_request_count_band(count, band):
    assert request_count_band(count) == band


def test_resolve_publish_analytics_date_refuses_unfinished_day():
    today = datetime.now(UTC).date()
    yesterday = (today - timedelta(days=1)).isoformat()
    assert resolve_publish_analytics_date(None) == yesterday
    assert resolve_publish_analytics_date(yesterday) == yesterday
    with pytest.raises(ValueError, match="not finished"):
        resolve_publish_analytics_date(today.isoformat())


class _MemoryCache:
    def __init__(self):
        self.data = {}

    def add(self, key, value, timeout=None):
        if key in self.data:
            return False
        self.data[key] = value
        return True

    def get(self, key, default=None):
        return self.data.get(key, default)

    def incr(self, key, delta=1):
        self.data[key] += delta
        return self.data[key]

    def touch(self, key, timeout=None):
        return key in self.data

    def delete(self, key):
        self.data.pop(key, None)


def _visitor_metrics(monkeypatch):
    from prometheus_client import CollectorRegistry, Counter

    from kernelCI_app.middleware.backendRequestMetricsMiddleware import Metrics

    registry = CollectorRegistry()
    bands = Counter(
        "dashboard_visitors_by_request_count_total",
        "Visitors by request-count band",
        ["client", "band"],
        registry=registry,
    )
    unique = MagicMock()
    seen = []

    def labels(*, client):
        counter = MagicMock()
        counter.inc.side_effect = lambda: seen.append(client)
        return counter

    unique.labels.side_effect = labels
    metrics = Metrics(
        requests_by_client=MagicMock(),
        unique_visitors=unique,
        unique_visitors_by_endpoint=MagicMock(),
        kci_dev_requests_by_version=MagicMock(),
        visitors_by_request_count=bands,
    )
    monkeypatch.setattr(f"{MIDDLEWARE_MODULE}.get_metrics", lambda: metrics)
    monkeypatch.setattr(f"{MIDDLEWARE_MODULE}.get_analytics_date", lambda: "2026-09-30")
    monkeypatch.setattr(
        f"{MIDDLEWARE_MODULE}.get_daily_salt", lambda analytics_date: "salt"
    )
    memory = _MemoryCache()
    monkeypatch.setattr(f"{MIDDLEWARE_MODULE}.cache", memory)
    return memory, bands, seen


def _request(ip, user_agent="Mozilla/5.0 Chrome/131.0.0.0"):
    return RequestFactory().get(
        "/api/tree/", HTTP_USER_AGENT=user_agent, REMOTE_ADDR=ip
    )


def _band_count(counter, client, band):
    return next(
        sample.value
        for metric in counter.collect()
        for sample in metric.samples
        if sample.labels.get("client") == client and sample.labels.get("band") == band
    )


def test_publish_counts_visitors_once_per_client(monkeypatch):
    memory, bands, seen = _visitor_metrics(monkeypatch)
    record_unique_visitor(
        request=_request("192.0.2.1"),
        endpoint="tree",
        client=Client.DASHBOARD,
    )
    record_unique_visitor(
        request=_request("192.0.2.1"),
        endpoint="tree",
        client=Client.DASHBOARD,
    )
    record_unique_visitor(
        request=_request("192.0.2.2", "kci-dev/0.1.11"),
        endpoint="tree",
        client=Client.KCI_DEV,
    )

    counts = {
        key: value
        for key, value in memory.data.items()
        if key.startswith("analytics:visitor-requests:")
    }
    assert sorted(counts.values()) == [1, 2]
    assert seen == [Client.DASHBOARD, Client.KCI_DEV]
    hashes = {key.rsplit(":", 1)[-1] for key in counts}
    monkeypatch.setattr(
        f"{MIDDLEWARE_MODULE}.iter_visitor_request_keys",
        lambda analytics_date: list(counts),
    )

    publish_visitor_requests("2026-09-30")
    publish_visitor_requests("2026-09-30")

    for metric in bands.collect():
        for sample in metric.samples:
            assert hashes.isdisjoint(sample.labels.values())
    assert _band_count(bands, "dashboard", "1-5") == 1
    assert _band_count(bands, "kci-dev", "1-5") == 1


def test_visitor_request_count_stops_at_cap(monkeypatch):
    memory, _bands, _seen = _visitor_metrics(monkeypatch)
    record_unique_visitor(
        request=_request("192.0.2.1"),
        endpoint="tree",
        client=Client.DASHBOARD,
    )
    key = next(
        key for key in memory.data if key.startswith("analytics:visitor-requests:")
    )
    memory.data[key] = REQUEST_COUNT_CAP
    record_unique_visitor(
        request=_request("192.0.2.1"),
        endpoint="tree",
        client=Client.DASHBOARD,
    )
    assert memory.data[key] == REQUEST_COUNT_CAP


def test_unique_visitors_use_legacy_dedupe_key(monkeypatch):
    memory, _bands, seen = _visitor_metrics(monkeypatch)
    memory.data["analytics:unique-visitors:2026-09-30:existinghash"] = "true"
    monkeypatch.setattr(
        f"{MIDDLEWARE_MODULE}.get_daily_visitor_hash",
        lambda request, analytics_date: "existinghash",
    )
    record_unique_visitor(
        request=_request("192.0.2.1"),
        endpoint="tree",
        client=Client.DASHBOARD,
    )
    assert seen == []
    assert any(key.startswith("analytics:visitor-requests:") for key in memory.data)


def test_iter_visitor_request_keys_scans_django_key(monkeypatch):
    analytics_date = "2026-09-30"
    prefix = f"analytics:visitor-requests:{analytics_date}:"
    logical = f"{prefix}dashboard:abc"
    stored = f":1:{logical}"
    seen = {}

    class Redis:
        def scan_iter(self, *, match, count=None):
            seen["match"] = match
            yield stored.encode()
            yield b"not-a-visitor-key"

    redis_cache = MagicMock()
    redis_cache.version = 1
    redis_cache._cache.get_client.return_value = Redis()
    monkeypatch.setattr(f"{MIDDLEWARE_MODULE}.cache", redis_cache)

    assert list(iter_visitor_request_keys(analytics_date)) == [logical]
    assert seen["match"] == f"*:1:{prefix}*"


def test_publish_skips_when_count_missing(monkeypatch):
    memory, bands, _seen = _visitor_metrics(monkeypatch)
    key = "analytics:visitor-requests:2026-09-30:dashboard:deadbeef"
    monkeypatch.setattr(
        f"{MIDDLEWARE_MODULE}.iter_visitor_request_keys",
        lambda analytics_date: [key],
    )
    publish_visitor_requests("2026-09-30")
    assert (
        sum(sample.value for metric in bands.collect() for sample in metric.samples)
        == 0.0
    )
    assert not any(
        k.startswith("analytics:visitor-requests-published:") for k in memory.data
    )
    memory.data[key] = 3
    publish_visitor_requests("2026-09-30")
    assert _band_count(bands, "dashboard", "1-5") == 1


def test_request_count_at_cap_refreshes_ttl(monkeypatch):
    memory, _bands, _seen = _visitor_metrics(monkeypatch)
    record_unique_visitor(
        request=_request("192.0.2.1"),
        endpoint="tree",
        client=Client.DASHBOARD,
    )
    key = next(
        key for key in memory.data if key.startswith("analytics:visitor-requests:")
    )
    memory.data[key] = REQUEST_COUNT_CAP
    touched = []

    def touch(key, timeout=None):
        touched.append(key)
        return key in memory.data

    monkeypatch.setattr(f"{MIDDLEWARE_MODULE}.cache.touch", touch)
    record_unique_visitor(
        request=_request("192.0.2.1"),
        endpoint="tree",
        client=Client.DASHBOARD,
    )
    assert key in touched


def test_publish_retries_after_increment_failure(monkeypatch):
    memory, bands, _seen = _visitor_metrics(monkeypatch)
    key = "analytics:visitor-requests:2026-09-30:dashboard:deadbeef"
    memory.data[key] = 2
    monkeypatch.setattr(
        f"{MIDDLEWARE_MODULE}.iter_visitor_request_keys",
        lambda analytics_date: [key],
    )
    calls = {"n": 0}
    original_labels = bands.labels

    def flaky_labels(**kwargs):
        counter = original_labels(**kwargs)
        original_inc = counter.inc

        def inc():
            calls["n"] += 1
            if calls["n"] == 1:
                raise OSError("prometheus unavailable")
            return original_inc()

        counter.inc = inc
        return counter

    bands.labels = flaky_labels

    with pytest.raises(RuntimeError, match="Failed to publish"):
        publish_visitor_requests("2026-09-30")
    assert not any(
        k.startswith("analytics:visitor-requests-published:") for k in memory.data
    )

    publish_visitor_requests("2026-09-30")
    assert _band_count(bands, "dashboard", "1-5") == 1
