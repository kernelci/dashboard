from django.http import HttpRequest
from datetime import datetime


# For logging that we care about, we create a function so we can easily use
# a more sophisticated logging library later.
def log_message(message: str) -> None:
    print(message)


def create_endpoint_notification(*, message: str, request: HttpRequest) -> str:
    return (
        message
        + "\n\nEndpoint:\n"
        + request.build_absolute_uri()
        + (
            ("\nBody:\n```json\n" + request.body.decode("utf-8") + "```")
            if request.body
            else ""
        )
        + "\nAccessed in: "
        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
