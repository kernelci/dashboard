"""
Factory for generating Issue test data.
"""

import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
from kernelCI_app.models import Issues
from .mocks import Issue


class IssueFactory(DjangoModelFactory):
    """Factory for creating Issue instances with realistic test data."""

    class Meta:
        model = Issues

    id = factory.Sequence(
        lambda n: (
            Issue.get_all_issue_ids()[n]
            if n < len(Issue.get_all_issue_ids())
            else f"issue_{n:08x}"
        )
    )

    version = factory.LazyAttribute(
        lambda obj: (
            Issue.get_issue_data(obj.id)["version"]
            if Issue.get_issue_data(obj.id)
            else 0
        )
    )

    origin = factory.Sequence(lambda n: (f"origin-fake-{n:08x}"))

    report_url = factory.LazyAttribute(
        lambda obj: f"https://reports.kernelci.org/{obj.origin}/{obj.id}.html"
    )
    report_subject = factory.Faker("sentence", nb_words=6)

    culprit_code = factory.Iterator([True, False, False])
    culprit_tool = factory.Iterator([False, True, False])
    culprit_harness = factory.Iterator([False, False, True])

    comment = factory.Faker("text", max_nb_chars=500)

    categories = factory.LazyFunction(
        lambda: ["build", "boot", "test", "regression", "performance"]
    )

    misc = factory.LazyFunction(
        lambda: {
            "severity": "medium",
            "priority": "normal",
            "assigned_to": "kernel-team@example.com",
            "created_by": "bot@kernelci.org",
        }
    )

    field_timestamp = factory.LazyFunction(lambda: timezone.now())
