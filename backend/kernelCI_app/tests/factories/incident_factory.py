"""
Factory for generating Incident test data.
"""

import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
from kernelCI_app.models import Incidents
from .issue_factory import IssueFactory
from .build_factory import BuildFactory
from .test_factory import TestFactory


class IncidentFactory(DjangoModelFactory):
    """Factory for creating Incident instances with realistic test data."""

    class Meta:
        model = Incidents

    id = factory.Sequence(lambda n: f"incident_{n:08x}")

    issue = factory.SubFactory(IssueFactory)
    build = factory.SubFactory(BuildFactory)
    test = factory.SubFactory(TestFactory)

    origin = factory.LazyAttribute(lambda obj: obj.issue.origin)

    issue_version = factory.LazyAttribute(lambda obj: obj.issue.version)

    present = factory.Iterator([True, True, True, False])

    comment = factory.Faker("text", max_nb_chars=300)

    misc = factory.LazyFunction(
        lambda: {
            "detected_at": timezone.now().isoformat(),
            "severity": "medium",
            "status": "open",
            "assigned_to": "kernel-team@example.com",
        }
    )

    field_timestamp = factory.LazyFunction(lambda: timezone.now())
