"""
Factory for generating Test test data.
"""

import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
from kernelCI_app.models import Tests, StatusChoices
from .build_factory import BuildFactory
from .mocks import Test, Checkout


class TestFactory(DjangoModelFactory):
    """Factory for creating Test instances with realistic test data."""

    class Meta:
        model = Tests

    id = factory.Sequence(lambda n: (f"test_{n:08x}"))

    build = factory.LazyAttribute(lambda obj: (BuildFactory()))

    # TODO: origin could be the origin of the test, not the build
    origin = factory.LazyAttribute(lambda obj: obj.build.origin)

    comment = factory.Faker("text", max_nb_chars=200)

    start_time = factory.LazyAttribute(lambda obj: obj.build.start_time)

    duration = factory.Faker("pyfloat", min_value=60.0, max_value=1800.0)

    path = factory.LazyAttribute(
        lambda obj: (
            "fluster.debian.v4l2.gstreamer_av1.validate-fluster-results"
            if obj.build.id == "fluster_build_valid"
            else "fake-path"
        )
    )

    environment_misc = factory.LazyAttribute(
        lambda obj: {
            "platform": (
                "meson-g12b-a311d-khadas-vim3"
                if obj.build.checkout.id == "amlogic_checkout_001"
                and obj.path == "boot.boot_test"
                else (
                    "meson-g12b-a311d-libretech-cc"
                    if obj.build.checkout.id == "amlogic_checkout_001"
                    and obj.path == "test.test_test"
                    else (
                        Checkout.get_hardware_platform(obj.build.checkout.id)
                        if Checkout.get_hardware_platform(obj.build.checkout.id)
                        else "hardware_test"
                    )
                )
            )
        }
    )

    environment_compatible = factory.LazyAttribute(
        lambda obj: (
            [obj.environment_misc["platform"], "amlogic,g12b"]
            if obj.environment_misc["platform"]
            in ["meson-g12b-a311d-khadas-vim3", "meson-g12b-a311d-libretech-cc"]
            else None
        )
    )

    log_url = factory.LazyAttribute(
        lambda obj: "https://logs.kernelci.org/"
        + f"{obj.origin}/{obj.build.checkout.git_commit_hash[:8]}/{obj.id}.log"
    )
    log_excerpt = factory.Faker("text", max_nb_chars=1500)

    misc = factory.LazyFunction(
        lambda: {
            "test_environment": "qemu",
            "kernel_version": "6.1.0",
            "test_suite": "ltp",
            "test_version": "20240115",
        }
    )

    status = factory.LazyAttribute(
        lambda obj: (
            Test.get_test_status_from_rules(obj.id, obj.build.id, obj.build.checkout.id)
            or StatusChoices.SKIP
        )
    )

    field_timestamp = factory.LazyFunction(lambda: timezone.now())
