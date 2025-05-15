import json
import os
import typing_extensions

from django.conf import settings
import yaml
from kernelCI_app.helpers.logger import log_message
from kernelCI_app.typeModels.common import StatusCount
from kernelCI_app.typeModels.treeListing import Checkout


def make_tree_identifier_key(
    *, tree_name: str, git_repository_url: str, git_repository_branch: str
) -> str:
    return f"{tree_name}-{git_repository_url}-{git_repository_branch}"


def get_tree_file_data() -> dict[str, dict[str, str]]:
    """Returns the data from the tree names file"""
    filepath = os.path.join(settings.BACKEND_VOLUME_DIR, "trees-name.yaml")

    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            trees_from_file = yaml.safe_load(file)

    if trees_from_file is not None:
        return trees_from_file
    return {}


@typing_extensions.deprecated(
    "Only use this function when the trees-name.yaml file is solidified and ready to be used.",
    category=None,
)
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


def sanitize_tree(
    checkout: dict,
) -> Checkout:
    """Sanitizes a checkout that was returned by a 'treelisting-like' query

    Returns a Checkout object"""
    build_status = StatusCount(
        PASS=checkout["pass_builds"],
        FAIL=checkout["fail_builds"],
        NULL=checkout["null_builds"],
        ERROR=checkout["error_builds"],
        MISS=checkout["miss_builds"],
        DONE=checkout["done_builds"],
        SKIP=checkout["skip_builds"],
    )

    test_status = {
        "pass": checkout["pass_tests"],
        "fail": checkout["fail_tests"],
        "null": checkout["null_tests"],
        "error": checkout["error_tests"],
        "miss": checkout["miss_tests"],
        "done": checkout["done_tests"],
        "skip": checkout["skip_tests"],
    }

    boot_status = {
        "pass": checkout["pass_boots"],
        "fail": checkout["fail_boots"],
        "null": checkout["null_boots"],
        "error": checkout["error_boots"],
        "miss": checkout["miss_boots"],
        "done": checkout["done_boots"],
        "skip": checkout["skip_boots"],
    }

    if isinstance(checkout.get("git_commit_tags"), str):
        try:
            checkout["git_commit_tags"] = json.loads(checkout["git_commit_tags"])
            if not isinstance(checkout["git_commit_tags"], list):
                checkout["git_commit_tags"] = []
        except json.JSONDecodeError:
            checkout["git_commit_tags"] = []

    return Checkout(
        **checkout,
        build_status=build_status,
        boot_status=boot_status,
        test_status=test_status,
    )
