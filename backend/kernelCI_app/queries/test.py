from typing import Optional
from kernelCI_app.models import Tests
from kernelCI_app.typeModels.databases import (
    Build__ConfigName,
    Checkout__GitRepositoryBranch,
    Checkout__GitRepositoryUrl,
    Origin,
    Test__Path,
    Test__StartTime,
)


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


def get_test_status_history(
    *,
    path: Test__Path,
    origin: Origin,
    git_repository_url: Checkout__GitRepositoryUrl,
    git_repository_branch: Checkout__GitRepositoryBranch,
    platform: Optional[str],
    current_test_start_time: Test__StartTime,
    config_name: Build__ConfigName,
):
    query = Tests.objects.filter(
        path=path,
        build__checkout__origin=origin,
        build__checkout__git_repository_url=git_repository_url,
        build__checkout__git_repository_branch=git_repository_branch,
        start_time__lte=current_test_start_time,
        build__config_name=config_name,
    ).values("start_time", "id", "status")

    if platform is None:
        query = query.filter(environment_misc__platform__isnull=True)
    else:
        query = query.filter(environment_misc__platform=platform)

    return query.order_by("-start_time")[:10]
