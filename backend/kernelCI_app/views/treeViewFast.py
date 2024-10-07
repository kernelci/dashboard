from django.http import JsonResponse
from django.views import View
from kernelCI_app.models import Checkouts
from kernelCI_app.utils import getQueryTimeInterval

DEFAULT_ORIGIN = "maestro"


class TreeViewFast(View):
    def get(self, request):
        origin = request.GET.get("origin", DEFAULT_ORIGIN)
        interval_days = int(request.GET.get("intervalInDays", "7"))
        interval_days_data = {"days": interval_days}

        checkouts = Checkouts.objects.raw(
            """
            WITH ordered_checkouts AS (
                SELECT
                    id,
                    tree_name,
                    git_repository_branch,
                    git_repository_url,
                    git_commit_hash,
                    git_commit_name,
                    patchset_hash,
                    start_time,
                    ROW_NUMBER() OVER
                    (PARTITION BY git_repository_url, git_repository_branch ORDER BY start_time DESC)
                    as time_order
                FROM
                    checkouts
                WHERE
                    origin = %s
                    AND start_time >= TO_TIMESTAMP(%s)
            )
            SELECT
                id,
                tree_name,
                git_repository_branch,
                git_repository_url,
                git_commit_hash,
                git_commit_name,
                patchset_hash,
                start_time
            FROM
                ordered_checkouts
            WHERE
                time_order = 1
            ORDER BY
                tree_name ASC;
            """,
            [origin, getQueryTimeInterval(**interval_days_data).timestamp()],
        )

        # TODO Use django serializer
        response_data = [
            {
                "id": checkout.id,
                "tree_name": checkout.tree_name,
                "git_repository_branch": checkout.git_repository_branch,
                "git_repository_url": checkout.git_repository_url,
                "git_commit_hash": checkout.git_commit_hash,
                "git_commit_name": checkout.git_commit_name,
                "patchset_hash": checkout.patchset_hash,
                "start_time": checkout.start_time,
            }
            for checkout in checkouts
        ]

        return JsonResponse(response_data, safe=False)
