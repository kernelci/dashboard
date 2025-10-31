import os
import yaml
import logging
from kernelCI_app.constants.ingester import TREES_FILE


logger = logging.getLogger("ingester")


def load_tree_names(trees_file: str = TREES_FILE) -> dict[str, str]:
    """Reads data from the trees_file, which correlates git_repository_url to tree_name"""
    with open(trees_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

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
    verify_dir(spool_dir)
    verify_dir(failed_dir)
    verify_dir(archive_dir)
