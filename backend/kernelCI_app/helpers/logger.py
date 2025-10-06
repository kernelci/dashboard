from django.http import HttpRequest

from kernelCI_app.constants.general import PRODUCTION_HOST, STAGING_HOST
from kernelCI_app.helpers.system import get_running_instance
import logging

logger = logging.getLogger(__name__)


# For logging that we care about, we create a function so we can easily use
# a more sophisticated logging library later.
def log_message(message: str) -> None:
    try:
        logger.info(message)
    except Exception:
        print("LOGGER FAILED, using print as fallback")
        print(message)


def create_endpoint_notification(*, message: str, request: HttpRequest) -> str:
    running_instance = get_running_instance()
    request_path = request.get_full_path()

    if running_instance is None:
        request_path = request.build_absolute_uri()
    elif running_instance == "production":
        request_path = PRODUCTION_HOST + request_path
    else:
        request_path = STAGING_HOST + request_path

    endpoint_clause = "\n\nEndpoint:\n" + request_path

    body_clause = (
        ("\nBody:\n```json\n" + request.body.decode("utf-8") + "```")
        if request.body
        else ""
    )

    return message + endpoint_clause + body_clause
