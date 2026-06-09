"""Privacy-preserving client analytics for ``/api/`` requests.

This middleware records anonymous, aggregate usage metrics. No personal data
(raw IP, raw User-Agent, full referrer URL) is stored or exposed as a metric
label.

Collected as aggregate Prometheus counters only:
  * Request attributes: endpoint, method, status_class, and coarse client
    buckets (browser, os, device) derived from the User-Agent. Referrer is
    reduced to its external domain (or ``direct_or_internal``).
  * Daily unique-visitor estimates (total and per-endpoint).

Visitor anonymization: a fingerprint is computed as
``HMAC-SHA256(daily_salt, "<ip>|<user_agent>")``. The ``daily_salt`` is a
random 32-byte secret generated per UTC day, kept only in the cache with a
~25h TTL, and rotated daily so hashes cannot be linked across days. Only the
hash is used as a de-duplication cache key; raw IP/User-Agent are discarded
immediately and never persisted.

See ``docs/monitoring.md`` ("Client Analytics & Privacy") for full details and
compliance notes.
"""

import hashlib
import hmac
import logging
import re
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime
from urllib.parse import urlparse

from django.core.cache import cache
from django.core.exceptions import DisallowedHost
from prometheus_client import Counter

UNKNOWN = "unknown"
DIRECT_OR_INTERNAL = "direct_or_internal"
UNIQUE_VISITOR_TTL_SECONDS = 25 * 60 * 60  # 25h
UNIQUE_VISITOR_SALT_BYTES = 32

logger = logging.getLogger(__name__)

DASHBOARD_BACKEND_REQUESTS_BY_CLIENT = Counter(
    "dashboard_backend_requests_by_client_total",
    "Backend requests grouped by endpoint and client attributes",
    [
        "endpoint",
        "method",
        "status_class",
        "browser",
        "os",
        "device",
        "referrer_domain",
    ],
)

DASHBOARD_UNIQUE_VISITORS_TOTAL = Counter(
    "dashboard_unique_visitors_total",
    "Daily unique backend visitors",
)

DASHBOARD_UNIQUE_VISITORS_BY_ENDPOINT_TOTAL = Counter(
    "dashboard_unique_visitors_by_endpoint_total",
    "Daily unique backend visitors deduplicated per endpoint by rotated Redis salt",
    ["endpoint"],
)


@dataclass(frozen=True)
class ClientInfo:
    browser: str
    os: str
    device: str


class BackendRequestMetricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith("/api/"):
            labels = get_backend_request_labels(request, response)
            record_client(**labels)
            record_unique_visitor(request=request, endpoint=labels["endpoint"])
        return response


def record_client(
    *,
    endpoint: str,
    method: str,
    status_class: str,
    browser: str,
    os: str,
    device: str,
    referrer_domain: str,
) -> None:
    DASHBOARD_BACKEND_REQUESTS_BY_CLIENT.labels(
        endpoint=endpoint,
        method=method,
        status_class=status_class,
        browser=browser,
        os=os,
        device=device,
        referrer_domain=referrer_domain,
    ).inc()


def record_unique_visitor(*, request, endpoint: str) -> None:
    try:
        analytics_date = get_analytics_date()
        visitor_hash = get_daily_visitor_hash(request, analytics_date=analytics_date)
        if visitor_hash is None:
            return

        visitor_key = f"analytics:unique-visitors:{analytics_date}:{visitor_hash}"
        endpoint_visitor_key = (
            f"analytics:unique-visitors:{analytics_date}:"
            f"endpoint:{endpoint}:{visitor_hash}"
        )

        if cache.add(visitor_key, "true", timeout=UNIQUE_VISITOR_TTL_SECONDS):
            DASHBOARD_UNIQUE_VISITORS_TOTAL.inc()

        if cache.add(endpoint_visitor_key, "true", timeout=UNIQUE_VISITOR_TTL_SECONDS):
            DASHBOARD_UNIQUE_VISITORS_BY_ENDPOINT_TOTAL.labels(endpoint=endpoint).inc()
    except Exception as exc:
        logger.debug("Failed to record unique visitor metric: %s", exc)


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
        return ClientInfo(browser=UNKNOWN, os=UNKNOWN, device=UNKNOWN)

    if is_bot(normalized_user_agent):
        return ClientInfo(browser="bot", os="bot", device="bot")

    return ClientInfo(
        browser=get_browser(normalized_user_agent),
        os=get_os(normalized_user_agent),
        device=get_device(normalized_user_agent),
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
    if any(s in normalized_user_agent for s in ["curl/", "wget/", "python-requests/"]):
        return "HTTP Client"
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
