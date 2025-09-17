"""
Factory for generating Checkout test data.
"""

import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
from kernelCI_app.models import Checkouts
from .mocks import Checkout


class CheckoutFactory(DjangoModelFactory):
    """Factory for creating Checkout instances with realistic test data."""

    class Meta:
        model = Checkouts

    id = factory.Sequence(
        lambda n: (
            Checkout.get_all_checkout_ids()[n]
            if n < len(Checkout.get_all_checkout_ids())
            else f"checkout_{n:08x}"
        )
    )

    origin = factory.LazyAttribute(
        lambda obj: (
            Checkout.get_origin(obj.id)
            if Checkout.is_known_checkout(obj.id)
            else "fake-origin"
        )
    )

    tree_name = factory.LazyAttribute(
        lambda obj: (
            Checkout.get_tree_name(obj.id)
            if Checkout.is_known_checkout(obj.id)
            else f"{obj.origin}-tree"
        )
    )

    git_repository_url = factory.LazyAttribute(
        lambda obj: (
            Checkout.get_git_url(obj.id)
            if Checkout.is_known_checkout(obj.id)
            else {
                "maestro": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
                "redhat": "https://git.kernel.org/pub/scm/linux/kernel/git/redhat/linux.git",
                "microsoft": "https://github.com/microsoft/WSL2-Linux-Kernel.git",
                "broonie": "https://git.kernel.org/pub/scm/linux/kernel/git/broonie/linux.git",
                "linaro": "https://git.linaro.org/landing-teams/working/arm/kernel-release.git",
                "0dayci": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
                "syzbot": "https://github.com/google/syzkaller.git",
                "android-mainline": "https://android.googlesource.com/kernel/common.git",
                "next-pending-fixes": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
            }.get(
                obj.origin,
                "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
            )
        )
    )

    git_commit_hash = factory.LazyAttribute(
        lambda obj: (
            obj.id if Checkout.is_known_checkout(obj.id) else f"commit_{obj.id[:8]}"
        )
    )

    git_commit_name = factory.LazyAttribute(
        lambda obj: f"commit-{obj.git_commit_hash[:8]}"
    )

    git_repository_branch = factory.LazyAttribute(
        lambda obj: (
            Checkout.get_git_branch(obj.id)
            if Checkout.is_known_checkout(obj.id)
            else "fake-branch"
        )
    )

    patchset_files = factory.LazyFunction(
        lambda: [
            {
                "name": "0001-fix-example.patch",
                "url": "https://example.com/patch1.patch",
            },
            {
                "name": "0002-update-config.patch",
                "url": "https://example.com/patch2.patch",
            },
        ]
    )

    patchset_hash = factory.Sequence(lambda n: f"patchset_{n:08x}")

    message_id = factory.Sequence(lambda n: f"<message-{n}@kernelci.org>")

    comment = factory.Faker("text", max_nb_chars=200)

    start_time = factory.LazyAttribute(
        lambda obj: (
            Checkout.get_timestamp(obj.id)
            if Checkout.get_timestamp(obj.id)
            else timezone.now() - timezone.timedelta(days=30)
        )
    )

    log_url = factory.LazyAttribute(
        lambda obj: f"https://logs.kernelci.org/{obj.origin}/{obj.git_commit_hash[:8]}.log"
    )

    log_excerpt = factory.Faker("text", max_nb_chars=1000)

    valid = factory.Iterator([True, True, True, False])

    misc = factory.LazyFunction(
        lambda: {
            "build_environment": "docker",
            "kernel_version": "6.1.0",
            "compiler": "gcc-11.2.0",
        }
    )

    git_commit_message = factory.Faker("text", max_nb_chars=500)
    git_repository_branch_tip = factory.Iterator([True, False])
    git_commit_tags = factory.LazyFunction(lambda: ["v6.1", "stable"])

    origin_builds_finish_time = factory.LazyFunction(
        lambda: timezone.now() - timezone.timedelta(minutes=30)
    )

    origin_tests_finish_time = factory.LazyFunction(
        lambda: timezone.now() - timezone.timedelta(minutes=15)
    )

    field_timestamp = factory.LazyFunction(lambda: timezone.now())
