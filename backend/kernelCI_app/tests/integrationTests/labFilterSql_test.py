"""Run lab predicates against Postgres, including paths and window edges."""

from datetime import datetime, timezone

import pytest
from django.db import connection

from kernelCI_app.constants.general import UNKNOWN_STRING
from kernelCI_app.helpers.labFilter import (
    full_page_lab_sql,
    hardware_details_lab_sql,
    lab_filter_sql,
)
from kernelCI_app.helpers.labFilter import test_side_lab_sql as side_lab_sql
from kernelCI_app.models import Builds, Checkouts, Labs, Tests
from kernelCI_app.queries.hardware import query_records
from kernelCI_app.typeModels.hardwareDetails import Tree

pytestmark = pytest.mark.django_db

START = datetime(2024, 1, 1, tzinfo=timezone.utc)
END = datetime(2024, 1, 2, tzinfo=timezone.utc)


def _ids(sql: str, params: dict, *, frm: str, column: str) -> set[str]:
    where = sql or "TRUE"
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT {column} FROM {frm} WHERE {where}", params)
        return {row[0] for row in cursor.fetchall()}


@pytest.fixture
def rows():
    checkout = Checkouts.objects.create(id="checkout", origin="maestro")
    lava = Labs.objects.create(name="lava")
    broonie = Labs.objects.create(name="broonie")
    capital = Labs.objects.create(name="Lava")
    named = Builds.objects.create(
        id="named",
        checkout=checkout,
        origin="maestro",
        lab=lava,
        misc={"lab": "only-misc"},
        start_time=START,
    )
    misc_only = Builds.objects.create(
        id="misc-only",
        checkout=checkout,
        origin="maestro",
        misc={"lab": "only-misc"},
        start_time=START,
    )
    empty_misc = Builds.objects.create(
        id="empty-misc",
        checkout=checkout,
        origin="maestro",
        misc={"lab": ""},
        start_time=START,
    )
    bare = Builds.objects.create(
        id="bare", checkout=checkout, origin="maestro", start_time=START
    )
    other = Builds.objects.create(
        id="other-lab",
        checkout=checkout,
        origin="maestro",
        lab=broonie,
        start_time=START,
    )
    capital_build = Builds.objects.create(
        id="capital-lab",
        checkout=checkout,
        origin="maestro",
        lab=capital,
        start_time=START,
    )
    keep = Builds.objects.create(
        id="keep", checkout=checkout, origin="maestro", lab=lava, start_time=START
    )

    def add_test(**kwargs):
        misc = kwargs.pop("misc", None)
        compatible = kwargs.pop("compatible", ["board"])
        return Tests.objects.create(
            origin="maestro",
            build=kwargs.pop("build"),
            start_time=START,
            environment_compatible=compatible,
            environment_misc={"platform": kwargs.pop("platform", "board")},
            misc=misc,
            **kwargs,
        )

    add_test(
        id="boot-lava",
        build=named,
        path="boot",
        lab=lava,
        misc={"runtime": "not-lava"},
    )
    add_test(id="boot-child", build=named, path="boot.nfs", lab=lava)
    add_test(id="bootloader", build=named, path="bootloader", lab=lava)
    add_test(
        id="boot-null",
        build=misc_only,
        path="boot",
        misc={"runtime": "lava"},
    )
    add_test(id="suite-lava", build=named, path="suite.a", lab=lava)
    add_test(id="suite-misc", build=misc_only, path="suite.a", misc={"runtime": "lava"})
    add_test(id="null-path", build=named, path=None, lab=lava)
    add_test(id="null-path-unknown", build=bare, path=None)
    add_test(
        id="0-outside",
        build=keep,
        path="suite.a",
        compatible=["other"],
        platform="other",
    )
    add_test(id="a-miss", build=keep, path="suite.a")
    add_test(id="b-boot-lava", build=keep, path="boot", lab=lava)
    add_test(id="c-boot-broonie", build=keep, path="boot", lab=broonie)
    add_test(id="d-loader", build=keep, path="bootloader", lab=lava)
    add_test(id="e-suite", build=keep, path="suite.a", lab=lava)
    add_test(id="f-null", build=keep, path=None, lab=lava)
    return {
        "lava": lava,
        "broonie": broonie,
        "builds": [named, misc_only, empty_misc, bare, other, capital_build, keep],
    }


def test_build_lab_matches_lab_id_not_misc(rows):
    def ids(labs):
        sql, params = lab_filter_sql(labs, lab_id_column="b.lab_id", param="labs")
        return _ids(sql, params, frm="builds b", column="b.id")

    assert ids({"lava"}) == {"named", "keep"}
    assert "misc-only" not in ids({"only-misc"})
    assert ids({"only-misc"}).isdisjoint({"misc-only", "named", "empty-misc", "bare"})
    unknown = ids({UNKNOWN_STRING})
    assert {"misc-only", "empty-misc", "bare"} <= unknown
    assert "named" not in unknown
    assert ids({"lava", UNKNOWN_STRING}) == {
        "named",
        "keep",
        "misc-only",
        "empty-misc",
        "bare",
    }
    assert ids({"Lava"}) == {"capital-lab"}
    assert ids({"lava "}) == set()
    assert ids({""}) == set()
    assert ids(set()) == {build.id for build in rows["builds"]}


def test_test_side_path_and_null_edges(rows):
    def ids(boot_labs, test_labs):
        sql, params = side_lab_sql(boot_labs, test_labs)
        return _ids(sql, params, frm="tests", column="tests.id")

    boots_only = ids({"lava"}, None)
    assert {"boot-lava", "boot-child"} <= boots_only
    assert "boot-null" not in boots_only
    assert "bootloader" in boots_only
    assert "suite-lava" in boots_only
    assert "null-path" in boots_only

    tests_only = ids(None, {"lava"})
    assert "boot-lava" in tests_only
    assert "boot-null" in tests_only
    assert "bootloader" in tests_only
    assert "suite-lava" in tests_only
    assert "null-path" in tests_only
    assert "suite-misc" not in tests_only
    assert "null-path-unknown" not in tests_only

    both = ids({"broonie"}, {"lava"})
    assert "c-boot-broonie" in both
    assert "b-boot-lava" not in both
    assert "d-loader" in both
    assert "f-null" in both
    assert "e-suite" in both
    assert "a-miss" not in both
    assert "suite-misc" not in both


def test_hardware_tab_scopes_drop_the_other_tab(rows):
    def ids(scope, **labs):
        sql, params = hardware_details_lab_sql(
            scope=scope,
            boot_labs=labs.get("boot"),
            test_labs=labs.get("test"),
            build_labs=labs.get("build"),
        )
        return _ids(
            sql,
            params,
            frm="tests JOIN builds ON tests.build_id = builds.id",
            column="tests.id",
        )

    assert ids("boot", boot={"lava"}) == {"boot-lava", "boot-child", "b-boot-lava"}
    assert "bootloader" not in ids("boot", boot={"lava"})
    assert "null-path" not in ids("boot", boot={"lava"})
    assert "f-null" not in ids("boot", boot={"lava"})
    assert {
        "bootloader",
        "suite-lava",
        "null-path",
        "d-loader",
        "e-suite",
        "f-null",
    } <= ids("test", test={"lava"})
    assert "boot-lava" not in ids("test", test={"lava"})
    assert ids("build", build={"lava"}) >= {"boot-lava", "a-miss"}
    assert "suite-misc" not in ids("build", build={"lava"})
    assert ids("build", build={UNKNOWN_STRING}) >= {"suite-misc", "boot-null"}
    assert "boot-lava" not in ids("build", build={UNKNOWN_STRING})
    assert ids("all", test={"lava"}) == {row.id for row in Tests.objects.all()}


def test_full_page_keeps_one_in_window_row_per_build(rows):
    sql, params = full_page_lab_sql(
        boot_labs={"broonie"}, test_labs={"lava"}, build_labs=None
    )
    query = f"""
        WITH hardware_rows AS (
            SELECT
                tests.id,
                tests.path,
                tests.lab_id,
                builds.lab_id AS build_lab_id,
                tests.build_id
            FROM tests
            JOIN builds ON builds.id = tests.build_id
            WHERE tests.environment_compatible @> ARRAY['board']::text[]
        )
        SELECT id FROM hardware_rows WHERE {sql}
    """
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        found = {row[0] for row in cursor.fetchall()}

    assert "0-outside" not in found
    assert "a-miss" in found
    assert "b-boot-lava" not in found
    assert {"c-boot-broonie", "d-loader", "e-suite", "f-null"} <= found
    assert "suite-misc" not in found


def test_query_records_applies_the_same_window(rows):
    tree = Tree(
        index="0",
        origin="maestro",
        tree_name="",
        git_repository_branch="",
        git_repository_url="",
        head_git_commit_name=None,
        head_git_commit_hash="abc",
        head_git_commit_tag=None,
        selected_commit_status=None,
        is_selected=True,
    )
    Checkouts.objects.filter(id="checkout").update(
        tree_name="",
        git_repository_branch="",
        git_repository_url="",
        git_commit_hash="abc",
    )

    def found(**labs):
        records = query_records(
            hardware_id="board",
            origin="maestro",
            trees=[tree],
            start_date=START,
            end_date=END,
            **labs,
        )
        return {row["id"] for row in records}

    assert "0-outside" not in found()
    assert {"a-miss", "f-null", "bootloader"} <= found()

    filtered = found(boot_labs={"broonie"}, test_labs={"lava"})
    assert "0-outside" not in filtered
    assert "a-miss" in filtered
    assert "b-boot-lava" not in filtered
    assert {"c-boot-broonie", "d-loader", "e-suite", "f-null"} <= filtered

    build_only = found(build_labs={"broonie"})
    assert "a-miss" in build_only
    assert "c-boot-broonie" in build_only
