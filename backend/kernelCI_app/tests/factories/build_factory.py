"""
Factory for generating Build test data.
"""

import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
from kernelCI_app.models import Builds, StatusChoices
from .checkout_factory import CheckoutFactory
from .mocks import Build, Checkout


class BuildFactory(DjangoModelFactory):
    """Factory for creating Build instances with realistic test data."""

    class Meta:
        model = Builds

    id = factory.Sequence(lambda n: f"build_{n:08x}")

    checkout = factory.SubFactory(CheckoutFactory)

    origin = factory.LazyAttribute(lambda obj: obj.checkout.origin)

    comment = factory.Faker("text", max_nb_chars=200)

    start_time = factory.LazyAttribute(lambda obj: obj.checkout.start_time)

    duration = factory.Faker("pyfloat", min_value=300.0, max_value=3600.0)

    architecture = factory.LazyAttribute(lambda obj: ("x86_64"))

    command = factory.LazyAttribute(
        lambda obj: f"make ARCH={obj.architecture} defconfig all"
    )

    compiler = factory.LazyAttribute(
        lambda obj: (
            ["gcc-12"]
            if obj.checkout.id != "aaeon_checkout_001"
            else ["gcc-11.2.0", "gcc-12.1.0", "clang-14.0.0", "clang-15.0.0"]
        )
    )

    input_files = factory.LazyFunction(
        lambda: [
            {"name": "defconfig", "url": "https://example.com/defconfig"},
            {"name": "kernel.config", "url": "https://example.com/kernel.config"},
        ]
    )

    output_files = factory.LazyFunction(
        lambda: [
            {"name": "vmlinux", "url": "https://example.com/vmlinux"},
            {"name": "bzImage", "url": "https://example.com/bzImage"},
            {"name": "modules.tar.gz", "url": "https://example.com/modules.tar.gz"},
        ]
    )

    config_name = factory.LazyAttribute(lambda obj: ("defconfig"))

    config_url = factory.LazyAttribute(
        lambda obj: f"https://configs.kernelci.org/{obj.origin}/{obj.config_name}"
    )
    log_url = factory.LazyAttribute(
        lambda obj: f"https://logs.kernelci.org/{obj.origin}/{obj.checkout.git_commit_hash[:8]}/{obj.id}.log"
    )
    log_excerpt = factory.Faker("text", max_nb_chars=2000)

    misc = factory.LazyAttribute(
        lambda obj: {
            "build_environment": "docker",
            "kernel_version": "6.1.0",
            "build_time": "2024-01-15T10:30:00Z",
            "memory_usage": "2.5GB",
            "disk_usage": "1.2GB",
            "hardware": (
                Checkout.get_hardware_platform(obj.checkout.id)
                if Checkout.get_hardware_platform(obj.checkout.id)
                else "fake-hardware"
            ),
        }
    )

    status = factory.LazyAttribute(
        lambda obj: (
            Build.get_build_status_from_rules(obj.id, obj.checkout.id)
            or StatusChoices.SKIP
        )
    )

    field_timestamp = factory.LazyFunction(lambda: timezone.now())
