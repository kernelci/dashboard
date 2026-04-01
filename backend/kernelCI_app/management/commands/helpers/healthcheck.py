from collections.abc import Callable
from typing import Any, Literal

from django.conf import settings

import requests

from kernelCI_app.helpers.logger import log_message

MONITORING_ID_PARAM_HELP_TEXT = (
    "Monitoring ID configured in settings for healthcheck.io pings "
    "(optional, used only for monitoring the command execution over time)"
)
type PingStatus = Literal["start", "fail", "success"]


def _resolve_monitoring_url(*, monitoring_id: str, status: PingStatus) -> str | None:
    healthcheck_base_url: str = settings.HEALTHCHECK_BASE_URL
    monitoring_path_map: dict[str, str] = settings.HEALTHCHECK_MONITORING_PATH_MAP
    monitoring_path = monitoring_path_map.get(monitoring_id)

    if not monitoring_path:
        return None

    # Success just needs to ping base healthcheck.io url + uuid, no subpath
    status_suffix = f"/{status}" if status != "success" else ""

    return f"{healthcheck_base_url.rstrip('/')}/{monitoring_path.lstrip('/')}{status_suffix}"


def _ping_healthcheck(*, monitoring_id: str, status: PingStatus) -> None:
    monitoring_url = _resolve_monitoring_url(monitoring_id=monitoring_id, status=status)
    if not monitoring_url:
        log_message(
            "No healthcheck URL configured for monitoring_id='%s', skipping %s ping."
            % (monitoring_id, status)
        )
        return

    try:
        response = requests.get(monitoring_url, timeout=10)
        response.raise_for_status()
        log_message(
            "Success at pinging healthcheck '%s' with monitoring_id '%s'"
            % (monitoring_url, monitoring_id)
        )
    except requests.RequestException as e:
        log_message(
            "ERROR: failed to ping healthcheck for monitoring_id='%s' and status='%s': %s"
            % (monitoring_id, status, e)
        )


def run_with_healthcheck_monitoring(
    *, monitoring_id: str | None, action: Callable[[], Any]
) -> Any:
    if not monitoring_id:
        return action()

    _ping_healthcheck(monitoring_id=monitoring_id, status="start")

    try:
        result = action()
    except Exception:
        _ping_healthcheck(monitoring_id=monitoring_id, status="fail")
        raise

    _ping_healthcheck(monitoring_id=monitoring_id, status="success")
    return result
