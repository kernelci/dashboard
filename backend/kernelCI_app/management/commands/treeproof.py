from django.core.management.base import BaseCommand
from kernelCI_app.models import Checkouts
import re
import yaml
import os
from django.conf import settings


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

            if not tree_name:
                tree_name = self._define_tree_name(git_url)

            if tree_name not in origin_trees:
                origin_trees[tree_name] = git_url

    def _merge_trees(self):
        merged_trees = {}

        for tree, git_url in self.maestro_trees.items():
            tree_in_dict = tree in merged_trees
            git_url_in_dict = git_url in merged_trees.values()

            if not (tree_in_dict or git_url_in_dict):
                merged_trees[tree] = git_url

        for tree, git_url in self.non_maestro_trees.items():
            tree_in_dict = tree in merged_trees
            git_url_in_dict = git_url in merged_trees.values()

            if not (tree_in_dict or git_url_in_dict):
                merged_trees[tree] = git_url

        return merged_trees

    def _format_trees_to_yml_format(self, trees: dict):
        trees_yml = {"trees": {}}

        for tree, git_url in trees.items():
            trees_yml["trees"][tree] = {"url": git_url}

        return trees_yml

    def handle(self, *args, **options):
        self._get_trees_proofs()
        self._get_trees_proofs(is_maestro=True)

        merged_dict = self._merge_trees()
        formatted_dict = self._format_trees_to_yml_format(merged_dict)

        filepath = os.path.join(settings.BACKEND_DATA_DIR, "trees-name.yaml")
        with open(filepath, "w") as file:
            yaml.dump(
                formatted_dict, file, default_flow_style=False, allow_unicode=True
            )
