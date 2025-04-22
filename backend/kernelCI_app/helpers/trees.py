import os

from django.conf import settings
import yaml
from kernelCI_app.helpers.logger import log_message


def make_tree_identifier_key(
    *, tree_name: str, git_repository_url: str, git_repository_branch: str
) -> str:
    return f"{tree_name}-{git_repository_url}-{git_repository_branch}"


def get_tree_file_data() -> dict[str, dict[str, str]]:
    """Returns the data from the tree names file"""
    filepath = os.path.join(settings.BACKEND_DATA_DIR, "trees-name.yaml")

    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            trees_from_file = yaml.safe_load(file)

    if trees_from_file is not None:
        return trees_from_file
    return {}


def get_tree_url_to_name_map() -> dict[str, str]:
    """Returns a dictionary mapping tree URLs to their tree names
    from the tree names file."""
    url_to_name = {}
    try:
        file_data = get_tree_file_data()

        # From: {"trees": {"tree1": {"url": "url1"}, "tree2": {"url": "url2"}}}
        # To: {"url1": "tree1", "url2": "tree2"}
        if file_data and "trees" in file_data:
            for tree_name, tree_data in file_data["trees"].items():
                if "url" in tree_data:
                    url_to_name[tree_data["url"]] = tree_name
    except (yaml.YAMLError, FileNotFoundError) as e:
        log_message(e)

    return url_to_name
