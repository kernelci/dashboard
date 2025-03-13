from kernelCI_app.helpers.logger import create_endpoint_notification
from kernelCI_app.helpers.discordWebhook import send_discord_notification


class LogServerErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if 500 <= response.status_code < 600:
            message = f"Request failed with error {response.status_code}: {response.reason_phrase}"
            notification = create_endpoint_notification(
                message=message,
                request=request,
            )
            send_discord_notification(content=notification)

        return response
