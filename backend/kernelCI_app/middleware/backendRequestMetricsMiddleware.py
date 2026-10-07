"""Privacy-preserving client analytics for ``/api/`` requests.

Long-lived Prometheus metrics are aggregate counts only. Raw IP, raw
User-Agent, and full referrer URL are never exposed as metric labels.

Collected as aggregate Prometheus counters:
  * Request attributes: endpoint, method, status_class, and coarse client
    buckets (browser, os, device) derived from the User-Agent. Referrer is
    reduced to its external domain (or ``direct_or_internal``).
  * ``kci-dev`` release version, on its own counter. The browser label stays
    ``kci-dev``.
  * Daily unique-visitor estimates (total and per-endpoint), labeled by coarse
    client kind (``dashboard``, ``kci-dev``, ``script``, ``bot``, ``unknown``).

Unique-visitor de-duplication uses pseudonymisation, not irreversible
anonymisation: fingerprint = ``HMAC-SHA256(daily_salt, "<ip>|<user_agent>")``.
The ``daily_salt`` is a random 32-byte secret generated per UTC day, kept only
in the cache with a ~25h TTL, and rotated daily so hashes cannot be linked
across days. Only the hash is used as a de-duplication cache key; raw
IP/User-Agent are discarded immediately after hashing and never written to
metrics or durable storage by this feature. While the salt exists, the cache
key is pseudonymised personal data under GDPR.

See ``docs/monitoring.md`` ("Client Analytics") and ``PRIVACY.md``.
"""

import hashlib
import hmac
import logging
import re
import secrets
import threading
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from urllib.parse import urlparse

from django.core.cache import cache
from django.core.exceptions import DisallowedHost
from prometheus_client import Counter

UNKNOWN = "unknown"
DIRECT_OR_INTERNAL = "direct_or_internal"


class Client(StrEnum):
    DASHBOARD = "dashboard"
    KCI_DEV = "kci-dev"
    SCRIPT = "script"
    BOT = "bot"
    UNKNOWN = "unknown"


SCRIPT_HTTP_USER_AGENT_MARKERS = (
    ("curl/", "curl"),
    ("wget/", "wget"),
    ("python-requests/", "python-requests"),
)
KCI_DEV_USER_AGENT = re.compile(
    r"^kci-dev(?:/([^\s/()]+))?(?:\s+\(([^)]+)\))?\s*$",
    re.IGNORECASE,
)
KCI_DEV_VERSION = re.compile(r"^\d+\.\d+\.\d+(?:[a-z0-9.]{0,16})?$", re.IGNORECASE)
KCI_DEV_OS = {
    "linux": "Linux",
    "macos": "macOS",
    "windows": "Windows",
}
UNIQUE_VISITOR_TTL_SECONDS = 25 * 60 * 60  # 25h
UNIQUE_VISITOR_SALT_BYTES = 32
REQUEST_COUNT_CAP = 1000
_BANDS = (
    (5, "1-5"),
    (10, "6-10"),
    (20, "11-20"),
    (50, "21-50"),
    (100, "51-100"),
    (500, "101-500"),
    (999, "501-999"),
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Metrics:
    requests_by_client: Counter
    unique_visitors: Counter
    unique_visitors_by_endpoint: Counter
    kci_dev_requests_by_version: Counter
    visitors_by_request_count: Counter


_metrics: Metrics | None = None
_metrics_lock = threading.Lock()


def get_metrics() -> Metrics:
    """Do not construct at import; Django admin checks import MIDDLEWARE."""
    global _metrics
    if _metrics is None:
        with _metrics_lock:
            if _metrics is None:
                _metrics = Metrics(
                    requests_by_client=Counter(
                        "dashboard_backend_requests_by_client_total",
                        "Backend requests grouped by endpoint and client attributes",
                        [
                            "endpoint",
                            "method",
                            "status_class",
                            "client",
                            "browser",
                            "os",
                            "device",
                            "referrer_domain",
                        ],
                    ),
                    unique_visitors=Counter(
                        "dashboard_unique_visitors_total",
                        "Daily unique backend visitors",
                        ["client"],
                    ),
                    unique_visitors_by_endpoint=Counter(
                        "dashboard_unique_visitors_by_endpoint_total",
                        "Daily unique backend visitors deduplicated per endpoint"
                        " by rotated Redis salt",
                        ["endpoint", "client"],
                    ),
                    kci_dev_requests_by_version=Counter(
                        "dashboard_kci_dev_requests_by_version_total",
                        "kci-dev requests by release version",
                        ["version", "client"],
                    ),
                    visitors_by_request_count=Counter(
                        "dashboard_visitors_by_request_count_total",
                        "Visitors published once per UTC day by request-count band",
                        ["client", "band"],
                    ),
                )
    return _metrics


@dataclass(frozen=True)
class ClientInfo:
    browser: str
    os: str
    device: str
    client: Client
    kci_dev_version: str | None = None


class BackendRequestMetricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith("/api/"):
            labels = get_backend_request_labels(request, response)
            record_client(
                **{
                    key: labels[key]
                    for key in (
                        "endpoint",
                        "method",
                        "status_class",
                        "client",
                        "browser",
                        "os",
                        "device",
                        "referrer_domain",
                    )
                }
            )
            if labels["client"] is Client.KCI_DEV:
                record_kci_dev_version(labels["kci_dev_version"])
            record_unique_visitor(
                request=request,
                endpoint=labels["endpoint"],
                client=labels["client"],
            )
        return response


def record_client(
    *,
    endpoint: str,
    method: str,
    status_class: str,
    client: Client,
    browser: str,
    os: str,
    device: str,
    referrer_domain: str,
) -> None:
    get_metrics().requests_by_client.labels(
        endpoint=endpoint,
        method=method,
        status_class=status_class,
        client=client,
        browser=browser,
        os=os,
        device=device,
        referrer_domain=referrer_domain,
    ).inc()


def record_kci_dev_version(version: str) -> None:
    get_metrics().kci_dev_requests_by_version.labels(
        version=version,
        client=Client.KCI_DEV,
    ).inc()


def record_unique_visitor(*, request, endpoint: str, client: Client) -> None:
    try:
        analytics_date = get_analytics_date()
        visitor_hash = get_daily_visitor_hash(request, analytics_date=analytics_date)
        if visitor_hash is None:
            return

        visitor_key = f"analytics:unique-visitors:{analytics_date}:{visitor_hash}"
        request_count_key = (
            f"analytics:visitor-requests:{analytics_date}:{client.value}:{visitor_hash}"
        )
        endpoint_visitor_key = (
            f"analytics:unique-visitors:{analytics_date}:"
            f"endpoint:{endpoint}:{visitor_hash}"
        )

        if cache.add(visitor_key, "true", timeout=UNIQUE_VISITOR_TTL_SECONDS):
            get_metrics().unique_visitors.labels(client=client).inc()

        _bump_request_count(request_count_key)

        if cache.add(endpoint_visitor_key, "true", timeout=UNIQUE_VISITOR_TTL_SECONDS):
            get_metrics().unique_visitors_by_endpoint.labels(
                endpoint=endpoint,
                client=client,
            ).inc()
    except Exception as exc:
        logger.debug("Failed to record unique visitor metric: %s", exc)


def _bump_request_count(key: str) -> None:
    if cache.add(key, 1, timeout=UNIQUE_VISITOR_TTL_SECONDS):
        return
    count = cache.get(key)
    if isinstance(count, int) and count < REQUEST_COUNT_CAP:
        cache.incr(key)
    cache.touch(key, UNIQUE_VISITOR_TTL_SECONDS)


def request_count_band(count: int) -> str:
    if count >= REQUEST_COUNT_CAP:
        return "1000+"
    for upper, band in _BANDS:
        if count <= upper:
            return band
    return "1000+"


def resolve_publish_analytics_date(analytics_date: str | None) -> str:
    yesterday = (datetime.now(UTC).date() - timedelta(days=1)).isoformat()
    if analytics_date is None:
        return yesterday
    if analytics_date >= datetime.now(UTC).date().isoformat():
        raise ValueError(
            f"Refusing to publish {analytics_date}: the UTC day is not finished"
        )
    return analytics_date


def publish_visitor_requests(analytics_date: str | None = None) -> None:
    """Observe one sample per visitor after the UTC day ends."""
    analytics_date = resolve_publish_analytics_date(analytics_date)

    bands = get_metrics().visitors_by_request_count
    failures = 0
    for key in iter_visitor_request_keys(analytics_date):
        rest = key.split(f"analytics:visitor-requests:{analytics_date}:", 1)[1]
        client_value, _, visitor_hash = rest.partition(":")
        published_key = (
            f"analytics:visitor-requests-published:{analytics_date}:"
            f"{client_value}:{visitor_hash}"
        )
        count = cache.get(key)
        if not isinstance(count, int):
            continue
        if not cache.add(published_key, 1, timeout=UNIQUE_VISITOR_TTL_SECONDS):
            continue
        try:
            bands.labels(
                client=client_value,
                band=request_count_band(count),
            ).inc()
        except Exception:
            cache.delete(published_key)
            logger.exception(
                "Failed to publish visitor request count band for client=%s",
                client_value,
            )
            failures += 1
            continue

    if failures:
        raise RuntimeError(
            f"Failed to publish visitor request counts for {failures} visitor(s)"
        )


def iter_visitor_request_keys(analytics_date: str):
    prefix = f"analytics:visitor-requests:{analytics_date}:"
    redis = cache._cache.get_client()
    version_mark = f":{cache.version}:"
    match = f"*{version_mark}{prefix}*"
    for raw_key in redis.scan_iter(match=match, count=200):
        key = raw_key.decode() if isinstance(raw_key, bytes) else raw_key
        logical = key.split(version_mark, 1)[-1]
        if logical.startswith(prefix):
            yield logical


def get_daily_visitor_hash(request, *, analytics_date: str) -> str | None:
    user_agent = request.headers.get("User-Agent", "")
    client_ip = get_client_ip(request)
    if not client_ip:
        return None

    daily_salt = get_daily_salt(analytics_date)
    if daily_salt is None:
        return None

    message = f"{client_ip}|{user_agent}".encode()
    return hmac.new(daily_salt.encode(), message, hashlib.sha256).hexdigest()


def get_daily_salt(analytics_date: str) -> str | None:
    salt_key = f"analytics:unique-visitors:salt:{analytics_date}"
    daily_salt = cache.get(salt_key)
    if daily_salt is not None:
        return daily_salt

    candidate_salt = secrets.token_hex(UNIQUE_VISITOR_SALT_BYTES)
    cache.add(salt_key, candidate_salt, timeout=UNIQUE_VISITOR_TTL_SECONDS)

    daily_salt = cache.get(salt_key)
    return daily_salt


def get_analytics_date() -> str:
    return datetime.now(UTC).date().isoformat()


def get_client_ip(request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",", maxsplit=1)[0].strip()

    forwarded = request.headers.get("Forwarded", "")
    if forwarded:
        forwarded_ip = parse_forwarded_for(forwarded)
        if forwarded_ip:
            return forwarded_ip

    return request.META.get("REMOTE_ADDR", "").strip()


def parse_forwarded_for(forwarded: str) -> str:
    first_hop = forwarded.split(",", maxsplit=1)[0]
    for part in first_hop.split(";"):
        key, _, value = part.strip().partition("=")
        if key.lower() == "for":
            return normalize_forwarded_node(value.strip().strip('"'))
    return ""


def normalize_forwarded_node(node: str) -> str:
    if node.startswith("["):  # IPV6 [2001:db8::1]:8080
        return node[1 : node.find("]")] if "]" in node else node[1:]
    if node.count(":") == 1:  # IPV4 192.0.2.60:8080
        return node.split(":", maxsplit=1)[0]
    return node


def get_backend_request_labels(request, response) -> dict[str, str]:
    client_info = get_client_info(request.headers.get("User-Agent", ""))

    return {
        "endpoint": get_endpoint(request),
        "method": request.method.upper(),
        "status_class": get_status_class(response.status_code),
        "browser": client_info.browser,
        "os": client_info.os,
        "device": client_info.device,
        "referrer_domain": get_referrer_domain(
            referrer=request.headers.get("Referer", ""),
            request_host=get_request_host(request),
        ),
        "client": client_info.client,
        "kci_dev_version": client_info.kci_dev_version or UNKNOWN,
    }


def get_request_host(request) -> str:
    try:
        return request.get_host()
    except DisallowedHost:
        return UNKNOWN


def get_endpoint(request) -> str:
    resolver_match = getattr(request, "resolver_match", None)
    url_name = getattr(resolver_match, "url_name", None)
    if url_name is not None:
        return url_name
    return UNKNOWN


def get_status_class(status_code: int) -> str:
    if 100 <= status_code <= 599:
        return f"{status_code // 100}xx"
    return UNKNOWN


def get_referrer_domain(*, referrer: str, request_host: str) -> str:
    if not referrer:
        return DIRECT_OR_INTERNAL

    parsed_referrer = urlparse(referrer)
    referrer_host = parsed_referrer.hostname
    if referrer_host is None:
        return DIRECT_OR_INTERNAL

    normalized_referrer = referrer_host.lower()
    normalized_request_host = request_host.split(":", maxsplit=1)[0].lower()
    if normalized_referrer == normalized_request_host:
        return DIRECT_OR_INTERNAL

    if normalized_referrer.endswith(f".{normalized_request_host}"):
        return DIRECT_OR_INTERNAL

    return normalized_referrer[:100]


def get_client_info(user_agent: str) -> ClientInfo:
    normalized_user_agent = user_agent.lower()
    if not normalized_user_agent:
        return ClientInfo(
            browser=UNKNOWN,
            os=UNKNOWN,
            device=UNKNOWN,
            client=Client.UNKNOWN,
        )

    kci_dev_match = KCI_DEV_USER_AGENT.match(user_agent)
    if kci_dev_match is not None:
        version = kci_dev_match.group(1)
        if version is None or KCI_DEV_VERSION.fullmatch(version) is None:
            version = UNKNOWN
        os_family = kci_dev_match.group(2)
        os = UNKNOWN
        if os_family:
            os = KCI_DEV_OS.get(os_family.strip().casefold(), UNKNOWN)
        return ClientInfo(
            browser="kci-dev",
            os=os,
            device="cli",
            client=Client.KCI_DEV,
            kci_dev_version=version,
        )

    for marker, tool in SCRIPT_HTTP_USER_AGENT_MARKERS:
        if marker in normalized_user_agent:
            return ClientInfo(
                browser=tool,
                os=UNKNOWN,
                device="script",
                client=Client.SCRIPT,
            )

    if is_bot(normalized_user_agent):
        return ClientInfo(
            browser="bot",
            os="bot",
            device="bot",
            client=Client.BOT,
        )

    browser = get_browser(normalized_user_agent)
    return ClientInfo(
        browser=browser,
        os=get_os(normalized_user_agent),
        device=get_device(normalized_user_agent),
        client=Client.DASHBOARD if browser != UNKNOWN else Client.UNKNOWN,
    )


def is_bot(normalized_user_agent: str) -> bool:
    return bool(
        re.search(
            r"bot|crawler|spider|slurp|duckduckbot|bingpreview|facebookexternalhit",
            normalized_user_agent,
        )
    )


def get_browser(normalized_user_agent: str) -> str:
    if "edg/" in normalized_user_agent:
        return "Edge"
    if "firefox/" in normalized_user_agent:
        return "Firefox"
    if any(s in normalized_user_agent for s in ["opr/", "opera"]):
        return "Opera"
    if any(s in normalized_user_agent for s in ["chrome/", "crios/"]):
        return "Chrome"
    if "safari/" in normalized_user_agent:
        return "Safari"
    if any(s in normalized_user_agent for s in ["msie", "trident/"]):
        return "Internet Explorer"
    return UNKNOWN


def get_os(normalized_user_agent: str) -> str:
    if "windows nt" in normalized_user_agent:
        return "Windows"
    if "android" in normalized_user_agent:
        return "Android"
    if "iphone" in normalized_user_agent or "ipad" in normalized_user_agent:
        return "iOS"
    if "mac os x" in normalized_user_agent:
        return "macOS"
    if "cros" in normalized_user_agent:
        return "Chrome OS"
    if "linux" in normalized_user_agent:
        return "Linux"
    return UNKNOWN


def get_device(normalized_user_agent: str) -> str:
    if any(s in normalized_user_agent for s in ["ipad", "tablet"]):
        return "tablet"
    if any(s in normalized_user_agent for s in ["mobile", "iphone", "android"]):
        return "mobile"
    return "desktop"
