from django.http import QueryDict
from django.test import RequestFactory

from kernelCI_app.constants.general import UNKNOWN_STRING
from kernelCI_app.helpers.filters import FilterParams
from kernelCI_app.helpers.labFilter import (
    as_positional,
    full_page_lab_sql,
    hardware_details_lab_sql,
    lab_filter_sql,
    lab_for_filter,
)
from kernelCI_app.helpers.labFilter import test_side_lab_sql as side_lab_sql


def test_lab_for_filter_treats_null_lab_id_as_unknown():
    assert lab_for_filter(None, "only-misc") == UNKNOWN_STRING
    assert lab_for_filter(None, "") == UNKNOWN_STRING
    assert lab_for_filter(None, None) == UNKNOWN_STRING
    assert lab_for_filter(4, "registered-lab") == "registered-lab"
    assert lab_for_filter(4, None) == "id:4"
    assert lab_for_filter(4, "") == "id:4"


def test_lab_filter_sql_names_and_unknown():
    sql, params = lab_filter_sql(
        {"lava", UNKNOWN_STRING, ""}, lab_id_column="b.lab_id", param="labs"
    )
    assert "labs_row.name = ANY(%(labs)s)" in sql
    assert "b.lab_id IS NULL" in sql
    assert params == {"labs": ["lava"]}
    assert lab_filter_sql(set(), lab_id_column="b.lab_id", param="labs") == ("", {})
    assert lab_filter_sql({""}, lab_id_column="b.lab_id", param="labs")[0] == "FALSE"


def test_issue_lab_filter_is_separate_from_tabs():
    request = RequestFactory().get("/")
    request.GET = QueryDict("filter_issue.lab=lava&filter_issue.lab=Unknown")
    filters = FilterParams(request)
    assert filters.filter_issue_labs == {"lava", UNKNOWN_STRING}
    assert filters.filter_labs["test"] == set()


def test_full_page_representative_stays_inside_the_hardware_window():
    sql, params = full_page_lab_sql(
        boot_labs=None, test_labs={"lava"}, build_labs={"lava"}
    )
    assert "FROM hardware_rows rep" in sql
    assert "FROM tests rep" not in sql
    assert params == {"test_labs": ["lava"], "build_labs": ["lava"]}


def test_full_page_build_lab_alone_stays_out_of_sql():
    assert full_page_lab_sql(boot_labs=None, test_labs=None, build_labs={"lava"}) == (
        "",
        {},
    )


def test_hardware_tab_scopes_do_not_use_the_full_page_predicate():
    assert hardware_details_lab_sql(
        scope="all",
        boot_labs=None,
        test_labs={"lava"},
        build_labs=None,
    ) == ("", {})
    boot_sql, _ = hardware_details_lab_sql(
        scope="boot",
        boot_labs={"lava"},
        test_labs=None,
        build_labs=None,
    )
    assert "tests.path" in boot_sql
    assert "COALESCE(tests.path, '')" in boot_sql
    assert "hardware_rows" not in boot_sql


def test_null_and_bootloader_paths_are_not_boots():
    sql, _ = side_lab_sql(None, {"lava"})
    assert "COALESCE(tests.path, '')" in sql
    boot_sql, _ = hardware_details_lab_sql(
        scope="boot", boot_labs={"lava"}, test_labs=None, build_labs=None
    )
    test_sql, _ = hardware_details_lab_sql(
        scope="test", boot_labs=None, test_labs={"lava"}, build_labs=None
    )
    assert "COALESCE(tests.path, '')" in boot_sql
    assert "NOT" in test_sql
    full_sql, _ = full_page_lab_sql(boot_labs=None, test_labs={"lava"}, build_labs=None)
    assert "COALESCE(path, '')" in full_sql


def test_lab_filter_edges():
    unknown_sql, unknown_params = lab_filter_sql(
        {UNKNOWN_STRING}, lab_id_column="b.lab_id", param="labs"
    )
    assert unknown_sql == "b.lab_id IS NULL"
    assert unknown_params == {}

    assert lab_filter_sql(None, lab_id_column="b.lab_id", param="labs") == ("", {})
    assert lab_filter_sql({"", None}, lab_id_column="b.lab_id", param="labs")[0] == (
        "FALSE"
    )

    sql, params = lab_filter_sql(
        {"Lava", "broonie"}, lab_id_column="t.lab_id", param="issue_labs"
    )
    assert params == {"issue_labs": ["Lava", "broonie"]}
    assert "t.lab_id IS NULL" not in sql

    positional, values = as_positional(sql, params)
    assert "%(issue_labs)s" not in positional
    assert values == [["Lava", "broonie"]]
    assert "boot.%%" in as_positional("path LIKE 'boot.%%'", {})[0]
