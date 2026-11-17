import pytest
from django.db import connection

from kernelCI_app.cache import clear_cache
from kernelCI_app.models import LabDaily, Labs
from kernelCI_app.queries.labs import get_lab_listing_data

pytestmark = pytest.mark.django_db


def test_one_lab_in_two_origins_is_one_row():
    with connection.cursor() as cursor:
        cursor.execute("SELECT CURRENT_DATE")
        today = cursor.fetchone()[0]

    lab = Labs.objects.create(name="shared-lab")
    LabDaily.objects.create(day=today, origin="maestro", lab=lab, build_pass=2)
    LabDaily.objects.create(day=today, origin="redhat", lab=lab, build_pass=5)

    clear_cache("labListing", {"interval_in_days": 7})
    shared = [
        row
        for row in get_lab_listing_data(interval_in_days=7)
        if row[0] == "shared-lab"
    ]

    assert shared == [("shared-lab", 7, 0, 0, 0, 0, 0, 0, 0, 0)]
