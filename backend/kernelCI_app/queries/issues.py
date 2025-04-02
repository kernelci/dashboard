from django.db import connection
from django.db.utils import ProgrammingError
from kernelCI_app.helpers.database import dict_fetchall
from kernelCI_app.helpers.environment import DEFAULT_SCHEMA_VERSION, set_schema_version
from kernelCI_app.helpers.logger import log_message
from kernelCI_app.models import Issues
from kernelCI_app.helpers.build import (
    is_valid_does_not_exist_exception,
    valid_status_field,
)
from datetime import datetime
from django.db.models import Q


def get_issue_builds(*, issue_id: str, version: int) -> list[dict]:
    params = {
        "issue_id": issue_id,
        "issue_version": version,
    }

    query = f"""
        SELECT
            B.ID,
            B.ARCHITECTURE,
            B.CONFIG_NAME,
            B.{valid_status_field()} AS build_status,
            B.START_TIME,
            B.DURATION,
            B.COMPILER,
            B.LOG_URL,
            C.TREE_NAME,
            C.GIT_REPOSITORY_BRANCH
        FROM
            INCIDENTS INC
            INNER JOIN BUILDS B ON (INC.BUILD_ID = B.ID)
            LEFT JOIN CHECKOUTS C ON (B.CHECKOUT_ID = C.ID)
        WHERE
            (
                INC.ISSUE_ID = %(issue_id)s
                AND INC.ISSUE_VERSION = %(issue_version)s
            )
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            return dict_fetchall(cursor)
    except ProgrammingError as e:
        if is_valid_does_not_exist_exception(e):
            set_schema_version()
            log_message(
                f"Issue Builds -- Schema version updated to {DEFAULT_SCHEMA_VERSION}"
            )
            return get_issue_builds(issue_id=issue_id, version=version)
        else:
            raise


def get_issue_tests(*, issue_id: str, version: int) -> list[dict]:
    params = {
        "issue_id": issue_id,
        "issue_version": version,
    }

    query = """
        SELECT
            T.ID,
            T.STATUS,
            T.DURATION,
            T.PATH,
            T.START_TIME,
            T.ENVIRONMENT_COMPATIBLE,
            T.ENVIRONMENT_MISC,
            C.TREE_NAME,
            C.GIT_REPOSITORY_BRANCH
        FROM
            INCIDENTS INC
            INNER JOIN TESTS T ON (INC.TEST_ID = T.ID)
            LEFT JOIN BUILDS B ON (T.BUILD_ID = B.ID)
            LEFT JOIN CHECKOUTS C ON (B.CHECKOUT_ID = C.ID)
        WHERE
            (
                INC.ISSUE_ID = %(issue_id)s
                AND INC.ISSUE_VERSION = %(issue_version)s
            )
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return dict_fetchall(cursor)


def get_issue_listing_data(
    *,
    interval_date: datetime,
    culprit_code: bool | None,
    culprit_harness: bool | None,
    culprit_tool: bool | None,
) -> list[dict]:
    filters = Q(field_timestamp__gte=interval_date)

    culprit_query = Q()

    if culprit_code:
        culprit_query |= Q(culprit_code=True)
    if culprit_harness:
        culprit_query |= Q(culprit_harness=True)
    if culprit_tool:
        culprit_query |= Q(culprit_tool=True)

    filters = filters & culprit_query

    issues_records = Issues.objects.values(
        "id",
        "field_timestamp",
        "comment",
        "version",
        "origin",
        "culprit_code",
        "culprit_harness",
        "culprit_tool",
    ).filter(filters)
    return issues_records
