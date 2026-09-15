"""
Add deterministic local rows for exercising tree A/B compare in the UI.

Does not clear the rest of the database. Re-running replaces only the
compare-sample checkouts (and their builds/tests/rollup rows).
"""

from __future__ import annotations

from datetime import timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from kernelCI_app.constants.general import UNKNOWN_STRING
from kernelCI_app.management.commands.helpers.aggregation_helpers import (
    aggregate_checkouts_and_pendings,
)
from kernelCI_app.management.commands.helpers.process_pending_helpers import (
    accumulate_rollup_entry,
    extract_path_group,
)
from kernelCI_app.models import (
    Builds,
    Checkouts,
    Labs,
    StatusChoices,
    Tests,
    TreeListing,
    TreeTestsRollup,
)

COMPARE_TREE = "linux"
COMPARE_BRANCH = "master"
COMPARE_ORIGIN = "maestro"
COMPARE_GIT_URL = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"
HASH_A = "cccccccccccccccccccccccccccccccccccccccc"
HASH_B = "dddddddddddddddddddddddddddddddddddddddd"
CHECKOUT_A_ID = "local_compare_sample_a"
CHECKOUT_B_ID = "local_compare_sample_b"

PLATFORMS = ("kubernetes", "qemu-arm64", "qemu-x86_64", "rpi4", "imx8mq-evk")

STATUS_PAIRS: tuple[tuple[StatusChoices, StatusChoices], ...] = (
    (StatusChoices.PASS, StatusChoices.FAIL),
    (StatusChoices.FAIL, StatusChoices.FAIL),
    (StatusChoices.FAIL, StatusChoices.PASS),
    (StatusChoices.PASS, StatusChoices.PASS),
    (StatusChoices.SKIP, StatusChoices.FAIL),
    (StatusChoices.ERROR, StatusChoices.PASS),
)

BUILD_SPECS: tuple[dict, ...] = (
    {
        "suffix": "defconfig_x86",
        "config": "defconfig",
        "arch": "x86_64",
        "compiler": ["gcc-12"],
        "status_a": StatusChoices.PASS,
        "status_b": StatusChoices.FAIL,
    },
    {
        "suffix": "allmodconfig_x86",
        "config": "allmodconfig",
        "arch": "x86_64",
        "compiler": ["clang-17"],
        "status_a": StatusChoices.FAIL,
        "status_b": StatusChoices.FAIL,
    },
    {
        "suffix": "tinyconfig_x86",
        "config": "tinyconfig",
        "arch": "x86_64",
        "compiler": ["gcc-13"],
        "status_a": StatusChoices.PASS,
        "status_b": StatusChoices.PASS,
    },
    {
        "suffix": "randconfig_x86",
        "config": "randconfig",
        "arch": "x86_64",
        "compiler": ["clang-18"],
        "status_a": StatusChoices.FAIL,
        "status_b": StatusChoices.PASS,
    },
    {
        "suffix": "defconfig_arm64",
        "config": "defconfig",
        "arch": "arm64",
        "compiler": ["gcc-12"],
        "status_a": StatusChoices.PASS,
        "status_b": StatusChoices.PASS,
    },
    {
        "suffix": "allmodconfig_arm64",
        "config": "allmodconfig",
        "arch": "arm64",
        "compiler": ["clang-17"],
        "status_a": StatusChoices.FAIL,
        "status_b": StatusChoices.FAIL,
    },
    {
        "suffix": "defconfig_arm",
        "config": "defconfig",
        "arch": "arm",
        "compiler": ["gcc-11"],
        "status_a": StatusChoices.PASS,
        "status_b": StatusChoices.FAIL,
    },
    {
        "suffix": "defconfig_riscv",
        "config": "defconfig",
        "arch": "riscv",
        "compiler": ["gcc-12"],
        "status_a": StatusChoices.FAIL,
        "status_b": StatusChoices.FAIL,
    },
)

KSELFTEST_LEAVES = (
    "sgx",
    "powerpc",
    "sparc64",
    "bpf",
    "x86",
    "arm",
    "arm64",
    "riscv",
    "smp",
    "namespace",
    "cgroup",
    "futex",
    "mount",
    "net",
    "kvm",
)

DEEP_TEST_PATHS = (
    "kselftest.bpf.test_attach_probe.multi_entry_probe_attach",
    "kselftest.net.psock.test_sock_pair.socketpair_unix_stream",
    "kselftest.vm.userfaultfd.userfaultfd_hugetlb",
    "kselftest.timers.clocksource.tsc_reliable",
    "kselftest.breakpoints.breakpoint_test_breakpoint",
)

BOOT_PATHS = (
    "boot",
    "boot.grafana",
    "boot.dra7xx-evm",
    "boot.qemu",
)


class Command(BaseCommand):
    help = "Seed paired compare revisions (linux/master) for local UI testing"

    def handle(self, *args, **options):
        now = timezone.now()
        with transaction.atomic():
            self._delete_prior_samples()
            checkout_a = self._create_checkout(
                checkout_id=CHECKOUT_A_ID,
                commit_hash=HASH_A,
                start_time=now - timedelta(days=2),
                label="compare-sample-a",
            )
            checkout_b = self._create_checkout(
                checkout_id=CHECKOUT_B_ID,
                commit_hash=HASH_B,
                start_time=now - timedelta(days=1),
                label="compare-sample-b",
            )
            lab = Labs.objects.get_or_create(name="lab-maestro")[0]
            builds, tests = self._seed_builds_and_tests(checkout_a, checkout_b, lab)
            rollup_count = self._create_tests_rollup(tests)
            for test in tests:
                test._lab_name = lab.name
            aggregate_checkouts_and_pendings(
                [checkout_a, checkout_b],
                tests,
                builds,
            )
            call_command("process_pending_aggregations", batch_size=5000)

        self.stdout.write(
            self.style.SUCCESS(
                "Compare sample data ready.\n"
                f"  tree/branch: {COMPARE_TREE}/{COMPARE_BRANCH}\n"
                f"  origin: {COMPARE_ORIGIN}\n"
                f"  hash A: {HASH_A}\n"
                f"  hash B: {HASH_B}\n"
                f"  tests/boots: {len(tests)}\n"
                f"  tree_tests_rollup rows: {rollup_count}\n"
                f"  URL: /tree/{COMPARE_TREE}/{COMPARE_BRANCH}/compare"
                f"?hashA={HASH_A}&hashB={HASH_B}&origin={COMPARE_ORIGIN}"
            )
        )

    def _delete_prior_samples(self) -> None:
        checkout_ids = [CHECKOUT_A_ID, CHECKOUT_B_ID]
        TreeTestsRollup.objects.filter(
            git_commit_hash__in=[HASH_A, HASH_B],
            origin=COMPARE_ORIGIN,
            tree_name=COMPARE_TREE,
        ).delete()
        TreeListing.objects.filter(
            git_commit_hash__in=[HASH_A, HASH_B],
            origin=COMPARE_ORIGIN,
            tree_name=COMPARE_TREE,
            git_repository_branch=COMPARE_BRANCH,
        ).delete()
        Tests.objects.filter(build__checkout_id__in=checkout_ids).delete()
        Builds.objects.filter(checkout_id__in=checkout_ids).delete()
        Checkouts.objects.filter(id__in=checkout_ids).delete()

    def _create_checkout(
        self,
        *,
        checkout_id: str,
        commit_hash: str,
        start_time,
        label: str,
    ) -> Checkouts:
        return Checkouts.objects.create(
            id=checkout_id,
            origin=COMPARE_ORIGIN,
            tree_name=COMPARE_TREE,
            git_repository_url=COMPARE_GIT_URL,
            git_repository_branch=COMPARE_BRANCH,
            git_commit_hash=commit_hash,
            git_commit_name=label,
            start_time=start_time,
            field_timestamp=start_time,
        )

    def _seed_builds_and_tests(
        self,
        checkout_a: Checkouts,
        checkout_b: Checkouts,
        lab: Labs,
    ) -> tuple[list[Builds], list[Tests]]:
        builds: list[Builds] = []
        for spec in BUILD_SPECS:
            for checkout, status_key in (
                (checkout_a, "status_a"),
                (checkout_b, "status_b"),
            ):
                builds.append(
                    Builds.objects.create(
                        id=f"compare_build_{spec['suffix']}_{checkout.id[-1]}",
                        checkout=checkout,
                        origin=COMPARE_ORIGIN,
                        lab=lab,
                        architecture=spec["arch"],
                        config_name=spec["config"],
                        compiler=spec["compiler"],
                        status=spec[status_key],
                        start_time=checkout.start_time,
                        field_timestamp=checkout.start_time,
                    )
                )

        created: list[Tests] = []
        test_index = 0

        def add_test(
            *,
            checkout: Checkouts,
            side: str,
            path: str,
            config: str,
            arch: str,
            status: StatusChoices,
            platform: str,
        ) -> None:
            nonlocal test_index
            build = Builds.objects.get(
                checkout=checkout,
                config_name=config,
                architecture=arch,
            )
            test = Tests.objects.create(
                id=f"compare_test_{side}_{test_index:04d}",
                build=build,
                origin=COMPARE_ORIGIN,
                lab=lab,
                path=path,
                status=status,
                start_time=checkout.start_time,
                field_timestamp=checkout.start_time,
                environment_misc={"platform": platform},
            )
            created.append(test)
            test_index += 1

        config_arch_pairs = {(s["config"], s["arch"]) for s in BUILD_SPECS}

        for checkout, side in ((checkout_a, "a"), (checkout_b, "b")):
            pair_index = 0
            for leaf in KSELFTEST_LEAVES:
                for config, arch in config_arch_pairs:
                    status_a, status_b = STATUS_PAIRS[pair_index % len(STATUS_PAIRS)]
                    status = status_a if side == "a" else status_b
                    platform = PLATFORMS[pair_index % len(PLATFORMS)]
                    add_test(
                        checkout=checkout,
                        side=side,
                        path=f"build.kselftest.{leaf}",
                        config=config,
                        arch=arch,
                        status=status,
                        platform=platform,
                    )
                    pair_index += 1

            for path_index, path in enumerate(DEEP_TEST_PATHS):
                config, arch = ("defconfig", "x86_64")
                status_a, status_b = STATUS_PAIRS[path_index % len(STATUS_PAIRS)]
                status = status_a if side == "a" else status_b
                add_test(
                    checkout=checkout,
                    side=side,
                    path=path,
                    config=config,
                    arch=arch,
                    status=status,
                    platform=PLATFORMS[path_index % len(PLATFORMS)],
                )

            for boot_index, boot_path in enumerate(BOOT_PATHS):
                config, arch = ("defconfig", "arm64")
                status_a, status_b = STATUS_PAIRS[boot_index % len(STATUS_PAIRS)]
                status = status_a if side == "a" else status_b
                add_test(
                    checkout=checkout,
                    side=side,
                    path=boot_path,
                    config=config,
                    arch=arch,
                    status=status,
                    platform=PLATFORMS[boot_index % len(PLATFORMS)],
                )

        return builds, created

    def _create_tests_rollup(self, tests: list[Tests]) -> int:
        rollup_data: dict = {}

        for test in tests:
            checkout = test.build.checkout
            path = test.path or ""
            platform = (
                test.environment_misc.get("platform") if test.environment_misc else None
            )
            hardware_key = platform or UNKNOWN_STRING
            compiler = (
                test.build.compiler[0]
                if isinstance(test.build.compiler, list) and test.build.compiler
                else test.build.compiler or UNKNOWN_STRING
            )
            accumulate_rollup_entry(
                rollup_data,
                {
                    "checkout": checkout,
                    "path_group": extract_path_group(path),
                    "config": test.build.config_name or UNKNOWN_STRING,
                    "arch": test.build.architecture or UNKNOWN_STRING,
                    "compiler": compiler,
                    "hardware_key": hardware_key,
                    "platform": platform,
                    "lab": None,
                    "origin": test.origin,
                    "issue_id": None,
                    "issue_version": None,
                    "issue_uncategorized": test.status == StatusChoices.FAIL,
                    "is_boot": bool(path) and path.startswith("boot"),
                    "status": test.status,
                },
            )

        rollup_objects = [
            TreeTestsRollup(
                origin=key.origin,
                tree_name=key.tree_name,
                git_repository_branch=key.git_repository_branch,
                git_repository_url=key.git_repository_url,
                git_commit_hash=key.git_commit_hash,
                path_group=key.path_group,
                build_config_name=key.config,
                build_architecture=key.arch,
                build_compiler=key.compiler,
                hardware_key=key.hardware_key,
                test_platform=key.platform,
                test_lab=key.lab,
                test_origin=key.test_origin,
                issue_id=key.issue_id,
                issue_version=key.issue_version,
                issue_uncategorized=key.issue_uncategorized,
                is_boot=key.is_boot,
                **counts,
            )
            for key, counts in rollup_data.items()
        ]

        TreeTestsRollup.objects.bulk_create(rollup_objects)
        return len(rollup_objects)
