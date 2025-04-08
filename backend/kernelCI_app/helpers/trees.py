from datetime import datetime
import os

from django.conf import settings
import yaml
from kernelCI_app.helpers.logger import log_message
from kernelCI_app.models import Checkouts


def make_tree_identifier_key(
    *, tree_name: str, git_repository_url: str, git_repository_branch: str
) -> str:
    return f"{tree_name}-{git_repository_url}-{git_repository_branch}"


def get_tree_heads(origin: str, start_date: datetime, end_date: datetime):
    tree_id_fields = [
        "tree_name",
        "git_repository_branch",
        "git_repository_url",
    ]

    checkouts_subquery = (
        Checkouts.objects.filter(
            origin=origin,
            start_time__gte=start_date,
            start_time__lte=end_date,
        )
        .order_by(
            *tree_id_fields,
            "-start_time",
        )
        .distinct(*tree_id_fields)
        .values_list("git_commit_hash", flat=True)
    )

    return checkouts_subquery


def get_tree_url_to_name_map() -> dict[str, str]:
    filepath = os.path.join(settings.BACKEND_DATA_DIR, "trees-name.yaml")
    url_to_name = {}
    try:
        with open(filepath, "r") as file:
            file_data = yaml.safe_load(file)

        # From: {"trees": {"tree1": {"url": "url1"}, "tree2": {"url": "url2"}}}
        # To: {"url1": "tree1", "url2": "tree2"}
        if file_data and "trees" in file_data:
            for tree_name, tree_data in file_data["trees"].items():
                if "url" in tree_data:
                    url_to_name[tree_data["url"]] = tree_name
    except (yaml.YAMLError, FileNotFoundError) as e:
        log_message(e)

    return url_to_name
