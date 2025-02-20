from datetime import datetime
from kernelCI_app.models import Checkouts


def make_tree_identifier_key(
    *, tree_name: str, git_repository_url: str, git_repository_branch: str
) -> str:
    return f"{tree_name}-{git_repository_url}-{git_repository_branch}"


def get_tree_heads(origin: str, start_date: datetime, end_date: datetime):
    tree_id_fields = [
        "tree_name",
        "git_repository_branch",
        "git_repository_url",
    ]

    checkouts_subquery = (
        Checkouts.objects.filter(
            origin=origin,
            start_time__gte=start_date,
            start_time__lte=end_date,
        )
        .order_by(
            *tree_id_fields,
            "-start_time",
        )
        .distinct(*tree_id_fields)
        .values_list("git_commit_hash", flat=True)
    )

    return checkouts_subquery
