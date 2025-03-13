import json
from http import HTTPStatus
from kernelCI_app.helpers.logger import create_endpoint_notification
from kernelCI_app.helpers.discordWebhook import send_discord_notification

REASON_MAX_LEN = 500


class LogServerErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if HTTPStatus(response.status_code).is_server_error:
            reason = (
                response.data
                if hasattr(response, "data")
                else response.content.decode()
            )
            reason = self.process_validation_error(reason)
            message = f"Request failed with error {response.status_code}: {response.reason_phrase}"
            if reason is not None and reason != "":
                reason = str(reason)[:REASON_MAX_LEN]
                message += f"\nReason (limited to {REASON_MAX_LEN} characters):\n```json\n{reason}```"

            notification = create_endpoint_notification(
                message=message,
                request=request,
            )
            send_discord_notification(content=notification)

        return response

    def process_validation_error(self, data: dict | list | str) -> dict | list:
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return data

        if isinstance(data, dict):
            return data

        new_data = []
        for error in data:
            if isinstance(error, dict):
                error.pop("input")
                error.pop("url")
            new_data.append(error)
        return new_data
