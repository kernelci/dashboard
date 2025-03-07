from typing import Any, Optional, TypedDict

import requests
import os

from kernelCI_app.helpers.logger import log_message

# For more information on discord webhook structure, visit
# https://discord.com/developers/docs/resources/webhook#execute-webhook

AVATAR_URL = "https://avatars.githubusercontent.com/u/11725450?s=200&v=4"
WEBHOOK_NAME = "KernelCI Dashboard Notifications"


class DiscordImage(TypedDict):
    url: str
    width: Optional[int]
    height: Optional[int]


class DiscordEmbed(TypedDict):
    title: str
    description: Optional[str]
    url: Optional[str]
    image: Optional[DiscordImage]


def send_discord_notification(
    *,
    content: Optional[str] = None,
    embeds: Optional[list[DiscordEmbed]] = None,
    avatar_url: Optional[str] = AVATAR_URL,
    webhook_name: Optional[str] = WEBHOOK_NAME,
) -> None:
    url = os.getenv("DISCORD_WEBHOOK_URL")
    if not url:
        log_message("DISCORD_WEBHOOK_URL environment variable is not set.")
        return

    if not content and not embeds:
        log_message(
            "Either content or embeds must be set in order to send notifications."
        )
        return

    if embeds is not None and len(embeds) > 10:
        log_message("The embed list can contain at most 10 elements.")
        return

    data: dict[str, Any] = {
        "avatar_url": avatar_url,
        "username": webhook_name,
    }
    if content is not None:
        data["content"] = content
    if embeds is not None:
        data["embeds"] = embeds

    try:
        result = requests.post(url=url, json=data)
        result.raise_for_status()
    except requests.HTTPError as e:
        log_message(e)

    return
