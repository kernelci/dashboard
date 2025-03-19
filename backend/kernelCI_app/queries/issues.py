import os
from django.db import connection
from django.db.utils import ProgrammingError
from kernelCI_app.helpers.database import dict_fetchall
from kernelCI_app.helpers.logger import log_message
import typing_extensions
from kernelCI_app.helpers.build import valid_do_not_exist_exception, valid_status_field
from kernelCI_app.constants.general import SCHEMA_VERSION_ENV


@typing_extensions.deprecated(
    "This implementation is temporary while the schema is being updated."
)
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
        if valid_do_not_exist_exception(e):
            os.environ[SCHEMA_VERSION_ENV] = "5"
            log_message("Issue Builds -- Schema version updated to 5")
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
