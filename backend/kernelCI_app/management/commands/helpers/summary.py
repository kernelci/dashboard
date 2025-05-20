import os
from typing import Literal, Optional

from django.conf import settings
from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.helpers.logger import log_message
from kernelCI_app.utils import read_yaml_file

type PossibleReportOptions = Literal["ignore_default_recipients"]
"""The expected possible options in a report. If a new option is added, add it here too."""

type TreeKey = tuple[str, str, str]
"""A tuple (branch, giturl, origin)"""

SUMMARY_SIGNUP_FOLDER = "notifications/subscriptions/"


def process_submissions_files(
    *,
    base_dir: Optional[str] = None,
    signup_folder: Optional[str] = None,
    summary_origins: Optional[list[str]],
) -> tuple[set[TreeKey], dict[TreeKey, list[dict]]]:
    """Processes all submission files and returns the set of TreeKey and
    the dict linking each tree to its report props"""
    if not base_dir:
        base_dir = settings.BACKEND_DATA_DIR
    if not signup_folder:
        signup_folder = SUMMARY_SIGNUP_FOLDER

    tree_key_set: set[TreeKey] = set()
    tree_prop_map: dict[TreeKey, list[dict]] = {}
    """Example:
    tree_prop_map[(master, <mainline_url>, maestro)] = [
        {
            branch: master
            always: true
        },
        {
            branch: master
            origin: microsoft
            options: {}
            recipients: []
        }
    ]
    """

    full_path = os.path.join(base_dir, signup_folder)
    for filename in os.listdir(full_path):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            file_path = os.path.join(signup_folder, filename)
            file_data = read_yaml_file(base_dir=base_dir, file=file_path)
            # Although there is a for loop here, there should only be a single tree per file
            for tree_name, tree_values in file_data.items():
                giturl = tree_values.get("url")
                default_recipients = tree_values.get("default_recipients")

                if tree_values.get("reports") is None:
                    continue

                for report in tree_values["reports"]:
                    branch = report["branch"]
                    origin = report.get("origin", DEFAULT_ORIGIN)
                    if summary_origins is not None and origin not in summary_origins:
                        continue

                    report["giturl"] = giturl
                    report["tree_name"] = tree_name
                    if default_recipients:
                        report["default_recipients"] = default_recipients

                    tree_key = (branch, giturl, origin)
                    tree_key_set.add(tree_key)
                    if tree_prop_map.get(tree_key) is None:
                        tree_prop_map[tree_key] = []
                    tree_prop_map[tree_key].append(report)
        else:
            log_message(
                f"Skipping file {filename} on loading summary files. Not a yaml file."
            )

    return tree_key_set, tree_prop_map
