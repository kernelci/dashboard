import os
from typing import Optional

from django.conf import settings

from kernelCI_app.helpers.logger import log_message
from kernelCI_app.management.commands.helpers.summary import SIGNUP_FOLDER
from kernelCI_app.utils import read_yaml_file


def get_default_tree_recipients(
    *,
    base_dir: Optional[str] = None,
    signup_folder: Optional[str] = None,
    search_url: str,
) -> list[str]:
    """
    Searches in every subscription file to find the matching git_url from a tree,
    and returns the default recipients of that tree

    Params:
        base_dir: the base path for the signup folder;
        signup_folder: the relative path of the folder where all the subscription files are;
        search_url: the url of the tree that is being searched;

    Returns:
        A list of str with recipient emails.
        The list will be empty if there was an error or the tree was not found.
    """

    if not base_dir:
        base_dir = settings.BACKEND_DATA_DIR
    if not signup_folder:
        signup_folder = SIGNUP_FOLDER

    full_path = os.path.join(base_dir, signup_folder)
    for filename in os.listdir(full_path):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            file_path = os.path.join(signup_folder, filename)
            file_data = read_yaml_file(base_dir=base_dir, file=file_path)

            # Although there is a for loop here, there should only be a single tree per file
            for tree_values in file_data.values():
                tree_url = tree_values.get("url")
                default_recipients = tree_values.get("default_recipients", [])
                if search_url is not None and search_url == tree_url:
                    return default_recipients
        else:
            log_message(
                f"Skipping file {filename} on loading summary files. Not a yaml file."
            )
