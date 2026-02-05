import logging
from typing import Optional
from django.core.management.base import BaseCommand
from kernelCI_app.constants.tree_names import TREE_NAMES_FILENAME
from kernelCI_app.models import Checkouts
import re
import yaml
import os
from django.conf import settings

logger = logging.getLogger(__name__)


def process_dict(d):
    for key, value in d.items():
        if isinstance(value, dict) and "url" in value:
            d[key] = value["url"]
        elif isinstance(value, dict):
            process_dict(value)


class Command(BaseCommand):
    def __init__(self):
        self.maestro_trees = dict()
        self.non_maestro_trees = dict()
        self.trees: dict[str, dict] = {"trees": {}}

    def _define_tree_name(self, git_url: str):
        regex = r"([^/]+)/([^/]+)?$"
        match = re.search(regex, git_url)

        first_part = match.group(1)
        second_part = match.group(2).split(".")[0]

        new_tree_name = first_part

        if second_part.lower() not in first_part.lower():
            new_tree_name += f"-{second_part}"

        return new_tree_name

    def _get_trees_proofs(self, *, is_maestro=False):
        query = (
            Checkouts.objects.values("tree_name", "git_repository_url")
            .distinct("tree_name", "git_repository_url")
            .filter(git_repository_url__isnull=False)
        )

        origin_trees = self.maestro_trees if is_maestro else self.non_maestro_trees

        if is_maestro:
            records = query.filter(origin="maestro")
        else:
            records = query.exclude(origin="maestro")

        for record in records:
            tree_name = record["tree_name"]
            git_url = record["git_repository_url"]

            if git_url in origin_trees.values():
                continue

            if not tree_name or tree_name in origin_trees:
                tree_name = self._define_tree_name(git_url)

            if tree_name in origin_trees:
                suffix_match = re.search(r"-(\d+)$", tree_name)
                if suffix_match:
                    suffix_num = int(suffix_match.group(1))
                    base_name = tree_name[: suffix_match.start()]
                    tree_name = f"{base_name}-{suffix_num + 1}"
                else:
                    tree_name = f"{tree_name}-1"

            origin_trees[tree_name] = git_url

    def _merge_trees(self, default_trees: dict = {}):
        merged_trees = default_trees

        for tree, git_url in self.maestro_trees.items():
            tree_in_dict = tree in merged_trees
            git_url_in_dict = git_url in merged_trees.values()

            if not tree_in_dict and not git_url_in_dict:
                merged_trees[tree] = git_url

        for tree, git_url in self.non_maestro_trees.items():
            tree_in_dict = tree in merged_trees
            git_url_in_dict = git_url in merged_trees.values()

            if not tree_in_dict and not git_url_in_dict:
                merged_trees[tree] = git_url

        return merged_trees

    def _format_trees_to_yml_format(self, trees: dict):
        trees_yml = {"trees": {}}

        for tree, git_url in trees.items():
            trees_yml["trees"][tree] = {"url": git_url}

        return trees_yml

    def generate_tree_names(self, filepath: Optional[str] = None) -> dict:
        """
        Reads the Checkouts table to find all unique git_repository_url and tree_name combinations,
        then generates a tree-names.yaml file with the format:

        trees:
            tree_name:
                url: git_repository_url

        If a tree_name is missing or duplicated, it will be generated based on the git_repository_url.
        If the tree_name already exists in the list but there's a new git_repository_url,
        the existing one will be kept and the new name will be suffixed with a number.

        Maestro and non-maestro trees are processed separately to avoid naming conflicts
        (maestro has priority).

        Writes the resulting file into BACKEND_VOLUME_DIR/TREE_NAMES_FILENAME.
        Returns the data that will be written to the tree-names.yaml file.
        """
        if filepath is None:
            filepath = os.path.join(settings.BACKEND_VOLUME_DIR, TREE_NAMES_FILENAME)

        if os.path.exists(filepath):
            with open(filepath, "r") as file:
                trees_from_file = yaml.safe_load(file)

                if trees_from_file is None:
                    trees_from_file = {}
                else:
                    process_dict(trees_from_file)
                    trees_from_file = trees_from_file["trees"]
        else:
            trees_from_file = {}

        self._get_trees_proofs()
        self._get_trees_proofs(is_maestro=True)

        merged_dict = self._merge_trees(default_trees=trees_from_file)
        formatted_dict = self._format_trees_to_yml_format(merged_dict)

        try:
            with open(filepath, "w") as file:
                yaml.dump(
                    formatted_dict, file, default_flow_style=False, allow_unicode=True
                )
        except Exception as e:
            # There's an exception but shouldn't stop the run because this can be used
            # in the code and is not a critical failure, so it shouldn't stop the execution.
            logger.error("Error writing %s: %s", TREE_NAMES_FILENAME, e)
        else:
            logger.info("Tree names file generated/updated at: %s", filepath)

        return formatted_dict

    def handle(self, *args, **options):
        """
        Generates the tree-names.yaml with a relation from tree_name to git_repository_url.
        """

        # Calls a separate function so that we can use the generation in the code while
        # also avoiding returning from handle(), which is expected to return None.
        self.generate_tree_names()
