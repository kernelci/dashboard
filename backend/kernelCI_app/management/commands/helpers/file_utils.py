import os
from typing import Optional
import logging
from kernelCI_app.constants.ingester import INGESTER_TREES_FILEPATH
from kernelCI_app.management.commands.treeproof import Command as TreeproofCommand


logger = logging.getLogger("ingester")


def load_tree_names(
    trees_file: Optional[str] = INGESTER_TREES_FILEPATH,
) -> dict[str, str]:
    """
    Updates data from the tree_names, which correlates git_repository_url to tree_name,
    and returns a dict with the updated data.
    """
    if trees_file is None:
        trees_file = INGESTER_TREES_FILEPATH

    try:
        data = TreeproofCommand().generate_tree_names(filepath=trees_file)
    except Exception as e:
        logger.error("Error reading trees file %s: %s", trees_file, e)
        raise e

    tree_names = {v["url"]: tree_name for tree_name, v in data.get("trees", {}).items()}

    return tree_names


def move_file_to_failed_dir(filename: str, failed_dir: str) -> None:
    try:
        os.rename(filename, os.path.join(failed_dir, os.path.basename(filename)))
    except Exception as e:
        logger.error("Error moving file %s to failed directory: %s", filename, e)
        raise e


def verify_dir(dir: str) -> None:
    if not os.path.exists(dir):
        logger.error("Directory %s does not exist", dir)
        # try to create it
        try:
            os.makedirs(dir)
            logger.info("Directory %s created", dir)
        except Exception as e:
            logger.error("Error creating directory %s: %s", dir, e)
            raise e
    if not os.path.isdir(dir):
        raise Exception(f"Directory {dir} is not a directory")
    if not os.access(dir, os.W_OK):
        raise Exception(f"Directory {dir} is not writable")
    logger.info("Directory %s is valid and writable", dir)


def verify_spool_dirs(spool_dir: str) -> None:
    failed_dir = os.path.join(spool_dir, "failed")
    archive_dir = os.path.join(spool_dir, "archive")
    pending_retry_dir = os.path.join(spool_dir, "pending_retry")
    verify_dir(spool_dir)
    verify_dir(failed_dir)
    verify_dir(archive_dir)
    verify_dir(pending_retry_dir)
