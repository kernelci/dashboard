"""
Factory for generating TreeTestsRollup test data.
"""

import factory
from factory.django import DjangoModelFactory
from kernelCI_app.models import TreeTestsRollup


class TreeTestsRollupFactory(DjangoModelFactory):
    """Factory for creating TreeTestsRollup instances with realistic test data."""

    class Meta:
        model = TreeTestsRollup

    origin = factory.Faker("word")
    tree_name = factory.Faker("word")
    git_repository_branch = factory.Faker("word")
    git_repository_url = factory.Faker("url")
    git_commit_hash = factory.Faker("sha1")

    path_group = factory.Faker("word")
    build_config_name = "defconfig"
    build_architecture = "x86_64"
    build_compiler = "gcc-12"
    hardware_key = factory.Faker("word")

    test_platform = None
    test_lab = None
    test_origin = None

    issue_id = None
    issue_version = None
    issue_uncategorized = False

    is_boot = False

    pass_tests = 0
    fail_tests = 0
    skip_tests = 0
    error_tests = 0
    miss_tests = 0
    done_tests = 0
    null_tests = 0
    total_tests = factory.LazyAttribute(
        lambda obj: (
            obj.pass_tests
            + obj.fail_tests
            + obj.skip_tests
            + obj.error_tests
            + obj.miss_tests
            + obj.done_tests
            + obj.null_tests
        )
    )
