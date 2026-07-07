"""Integration tests for the prune_db management command."""

from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone

from kernelCI_app.models import Builds, Checkouts, Tests
from kernelCI_app.tests.factories import (
    BuildFactory,
    CheckoutFactory,
    IncidentFactory,
    TestFactory,
)


def _days_ago(days: int):
    return timezone.now() - timezone.timedelta(days=days)


def _prune(**kwargs) -> str:
    out = StringIO()
    call_command("prune_db", older_than="10 days", stdout=out, **kwargs)
    return out.getvalue()


@pytest.mark.django_db
def test_old_checkout_cascades():
    """An old checkout drags its builds and tests even when they are newer."""
    checkout = CheckoutFactory(field_timestamp=_days_ago(30))
    build = BuildFactory(checkout=checkout, field_timestamp=_days_ago(1))
    test = TestFactory(build=build, field_timestamp=_days_ago(1))

    _prune(yes=True)

    assert not Checkouts.objects.filter(id=checkout.id).exists()
    assert not Builds.objects.filter(id=build.id).exists()
    assert not Tests.objects.filter(id=test.id).exists()


@pytest.mark.django_db
def test_old_build_cascades():
    """An old build drags its newer tests; its recent checkout survives."""
    checkout = CheckoutFactory(field_timestamp=_days_ago(1))
    build = BuildFactory(checkout=checkout, field_timestamp=_days_ago(30))
    test = TestFactory(build=build, field_timestamp=_days_ago(1))

    _prune(yes=True)

    assert Checkouts.objects.filter(id=checkout.id).exists()
    assert not Builds.objects.filter(id=build.id).exists()
    assert not Tests.objects.filter(id=test.id).exists()


@pytest.mark.django_db
def test_remove_old_only():
    """Recent rows survive; an old test is removed while its recent build/checkout stay."""
    checkout = CheckoutFactory(field_timestamp=_days_ago(1))
    build = BuildFactory(checkout=checkout, field_timestamp=_days_ago(1))
    recent_test = TestFactory(build=build, field_timestamp=_days_ago(1))
    old_test = TestFactory(build=build, field_timestamp=_days_ago(30))

    _prune(yes=True)

    assert Checkouts.objects.filter(id=checkout.id).exists()
    assert Builds.objects.filter(id=build.id).exists()
    assert Tests.objects.filter(id=recent_test.id).exists()
    assert not Tests.objects.filter(id=old_test.id).exists()


@pytest.mark.django_db
def test_dry_run_no_deletion():
    checkout = CheckoutFactory(field_timestamp=_days_ago(30))
    build = BuildFactory(checkout=checkout, field_timestamp=_days_ago(30))
    test = TestFactory(build=build, field_timestamp=_days_ago(30))

    output = _prune(dry_run=True)

    assert "DRY RUN" in output
    for label in ("checkouts", "builds", "tests", "total"):
        assert label in output
    assert Checkouts.objects.filter(id=checkout.id).exists()
    assert Builds.objects.filter(id=build.id).exists()
    assert Tests.objects.filter(id=test.id).exists()


@pytest.mark.django_db
def test_origins_limit_age_prune():
    """--origins limits age-based pruning; rows from other origins are kept."""
    kept_checkout = CheckoutFactory(field_timestamp=_days_ago(30), origin="keep-me")
    kept_build = BuildFactory(
        checkout=kept_checkout, field_timestamp=_days_ago(30), origin="keep-me"
    )
    pruned_checkout = CheckoutFactory(field_timestamp=_days_ago(30), origin="prune-me")
    pruned_build = BuildFactory(
        checkout=pruned_checkout, field_timestamp=_days_ago(30), origin="prune-me"
    )

    _prune(yes=True, origins=["prune-me"])

    assert Checkouts.objects.filter(id=kept_checkout.id).exists()
    assert Builds.objects.filter(id=kept_build.id).exists()
    assert not Checkouts.objects.filter(id=pruned_checkout.id).exists()
    assert not Builds.objects.filter(id=pruned_build.id).exists()


@pytest.mark.django_db
def test_origins_cascade_ignores_child_origin():
    """Children of a pruned parent are removed even when their origin differs."""
    checkout = CheckoutFactory(field_timestamp=_days_ago(30), origin="parent-origin")
    build = BuildFactory(
        checkout=checkout,
        field_timestamp=_days_ago(1),
        origin="child-origin",
    )
    test = TestFactory(
        build=build,
        field_timestamp=_days_ago(1),
        origin="child-origin",
    )

    _prune(yes=True, origins=["parent-origin"])

    assert not Checkouts.objects.filter(id=checkout.id).exists()
    assert not Builds.objects.filter(id=build.id).exists()
    assert not Tests.objects.filter(id=test.id).exists()


@pytest.mark.django_db
def test_tables_tests_only():
    """--tables tests deletes only old tests; parents and a recent test under an old
    build/checkout are kept because those parents are not being pruned."""
    checkout = CheckoutFactory(field_timestamp=_days_ago(30))
    build = BuildFactory(checkout=checkout, field_timestamp=_days_ago(30))
    old_test = TestFactory(build=build, field_timestamp=_days_ago(30))
    recent_test = TestFactory(build=build, field_timestamp=_days_ago(1))

    _prune(yes=True, tables=["tests"])

    assert Checkouts.objects.filter(id=checkout.id).exists()
    assert Builds.objects.filter(id=build.id).exists()
    assert not Tests.objects.filter(id=old_test.id).exists()
    assert Tests.objects.filter(id=recent_test.id).exists()


@pytest.mark.django_db
def test_tables_builds_only():
    """--tables builds deletes only old builds; a recent build survives, the checkout is
    untouched, and an unlisted child test is left in place (orphaned)."""
    checkout = CheckoutFactory(field_timestamp=_days_ago(30))
    old_build = BuildFactory(checkout=checkout, field_timestamp=_days_ago(30))
    orphaned_test = TestFactory(build=old_build, field_timestamp=_days_ago(30))
    recent_build = BuildFactory(checkout=checkout, field_timestamp=_days_ago(1))

    _prune(yes=True, tables=["builds"])

    assert Checkouts.objects.filter(id=checkout.id).exists()
    assert not Builds.objects.filter(id=old_build.id).exists()
    assert Builds.objects.filter(id=recent_build.id).exists()
    assert Tests.objects.filter(id=orphaned_test.id).exists()


@pytest.mark.django_db
def test_tables_builds_tests_cascade_within_selection():
    """With builds and tests selected, an old build still drags its recent tests, but
    an old checkout does not drag its recent builds (checkouts not selected)."""
    checkout = CheckoutFactory(field_timestamp=_days_ago(30))
    old_build = BuildFactory(checkout=checkout, field_timestamp=_days_ago(30))
    old_build_recent_test = TestFactory(build=old_build, field_timestamp=_days_ago(1))
    recent_build = BuildFactory(checkout=checkout, field_timestamp=_days_ago(1))
    recent_build_recent_test = TestFactory(
        build=recent_build, field_timestamp=_days_ago(1)
    )

    _prune(yes=True, tables=["builds", "tests"])

    assert Checkouts.objects.filter(id=checkout.id).exists()
    assert not Builds.objects.filter(id=old_build.id).exists()
    assert not Tests.objects.filter(id=old_build_recent_test.id).exists()
    assert Builds.objects.filter(id=recent_build.id).exists()
    assert Tests.objects.filter(id=recent_build_recent_test.id).exists()


@pytest.mark.django_db
def test_invalid_table():
    with pytest.raises(CommandError, match="Unknown table"):
        _prune(yes=True, tables=["incidents"])


@pytest.mark.django_db
def test_incident_linked_rows_kept_by_default():
    """Builds and tests with incidents are kept unless --skip-issue-protection is set."""
    checkout = CheckoutFactory(field_timestamp=_days_ago(30))
    kept_build = BuildFactory(checkout=checkout, field_timestamp=_days_ago(30))
    kept_test = TestFactory(build=kept_build, field_timestamp=_days_ago(30))
    IncidentFactory(build=kept_build, test=kept_test)

    pruned_build = BuildFactory(checkout=checkout, field_timestamp=_days_ago(30))
    pruned_test = TestFactory(build=pruned_build, field_timestamp=_days_ago(30))

    _prune(yes=True)

    assert Checkouts.objects.filter(id=checkout.id).exists()
    assert Builds.objects.filter(id=kept_build.id).exists()
    assert Tests.objects.filter(id=kept_test.id).exists()
    assert not Builds.objects.filter(id=pruned_build.id).exists()
    assert not Tests.objects.filter(id=pruned_test.id).exists()


@pytest.mark.django_db
def test_incident_on_test_protects_parent_build():
    """A test tied to an incident keeps its parent build to avoid orphaning it."""
    checkout = CheckoutFactory(field_timestamp=_days_ago(30))
    build = BuildFactory(checkout=checkout, field_timestamp=_days_ago(30))
    test = TestFactory(build=build, field_timestamp=_days_ago(30))
    IncidentFactory(build=None, test=test)

    _prune(yes=True)

    assert Checkouts.objects.filter(id=checkout.id).exists()
    assert Builds.objects.filter(id=build.id).exists()
    assert Tests.objects.filter(id=test.id).exists()


@pytest.mark.django_db
def test_skip_issue_protection_deletes_linked_rows():
    checkout = CheckoutFactory(field_timestamp=_days_ago(30))
    build = BuildFactory(checkout=checkout, field_timestamp=_days_ago(30))
    test = TestFactory(build=build, field_timestamp=_days_ago(30))
    IncidentFactory(build=build, test=test)

    _prune(yes=True, skip_issue_protection=True)

    assert not Checkouts.objects.filter(id=checkout.id).exists()
    assert not Builds.objects.filter(id=build.id).exists()
    assert not Tests.objects.filter(id=test.id).exists()
