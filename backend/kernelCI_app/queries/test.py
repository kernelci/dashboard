import datetime
from kernelCI_app.models import Tests


def get_test_details_data(*, test_id):
    return (
        Tests.objects.filter(id=test_id)
        .values(
            "id",
            "build_id",
            "status",
            "path",
            "log_excerpt",
            "log_url",
            "misc",
            "environment_misc",
            "start_time",
            "environment_compatible",
            "output_files",
            "field_timestamp",
            "build__compiler",
            "build__architecture",
            "build__config_name",
            "build__checkout__git_commit_hash",
            "build__checkout__git_repository_branch",
            "build__checkout__git_repository_url",
            "build__checkout__git_commit_tags",
            "build__checkout__tree_name",
            "build__checkout__origin",
        )
        .first()
    )


# TODO: combine with the test_details query
def get_test_status_history(
    *,
    path: str,
    origin: str,
    git_repository_url: str,
    git_repository_branch: str,
    platform: str,
    current_test_timestamp: datetime,
):
    return (
        Tests.objects.values(
            "field_timestamp",
            "id",
            "status",
            "build__checkout__git_commit_hash",
        )
        .filter(
            path=path,
            build__checkout__origin=origin,
            build__checkout__git_repository_url=git_repository_url,
            build__checkout__git_repository_branch=git_repository_branch,
            environment_misc__platform=platform,
            field_timestamp__lte=current_test_timestamp,
        )
        .order_by("-field_timestamp")[:10]
    )
