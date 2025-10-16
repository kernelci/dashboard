import os
import yaml
import logging
from kernelCI_app.helpers.logger import out
from kernelCI_app.constants.ingester import TREES_FILE


logger = logging.getLogger("ingester")


def get_spool_files(spool_dir: str) -> tuple[list[str], int]:
    json_files = [
        f
        for f in os.listdir(spool_dir)
        if os.path.isfile(os.path.join(spool_dir, f)) and f.endswith(".json")
    ]
    if not json_files:
        return

    total_bytes = 0
    for f in json_files:
        try:
            total_bytes += os.path.getsize(os.path.join(spool_dir, f))
        except Exception:
            pass

    out(
        "Spool status: %d .json files queued (%.2f MB)"
        % (
            len(json_files),
            total_bytes / (1024 * 1024) if total_bytes else 0.0,
        )
    )

    return json_files, total_bytes


def load_trees_name(trees_file: str = TREES_FILE) -> dict[str, str]:
    """Reads data from the trees_file, which correlates git_repository_url to tree_name"""
    with open(trees_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    trees_name = {v["url"]: tree_name for tree_name, v in data.get("trees", {}).items()}

    return trees_name


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
