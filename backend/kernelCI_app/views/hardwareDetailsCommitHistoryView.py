from django.db.models import Subquery
import json
from typing import Dict, Set, Literal
from kernelCI_app.helpers.errorHandling import create_error_response
from kernelCI_app.helpers.logger import log_message
from django.utils.decorators import method_decorator
from django.views import View
from datetime import datetime, timezone
from django.http import JsonResponse
from kernelCI_app.viewCommon import create_details_build_summary
from kernelCI_app.models import Tests, Checkouts
from kernelCI_app.utils import (
    extract_error_message,
    extract_platform,
)
from django.views.decorators.csrf import csrf_exempt
from kernelCI_app.helpers.trees import get_tree_heads
from kernelCI_app.typeModels.hardwareDetails import CommitHistoryPostBody, CommitHistoryQuerysetItem
from pydantic import ValidationError

DEFAULT_DAYS_INTERVAL = 3
SELECTED_HEAD_TREE_VALUE = 'head'
STATUS_FAILED_VALUE = "FAIL"

BuildStatusType = Literal["valid", "invalid", "null"]




# disable django csrf protection https://docs.djangoproject.com/en/5.0/ref/csrf/
# that protection is recommended for ‘unsafe’ methods (POST, PUT, and DELETE)
# but we are using POST here just to follow the convention to use the request body
# also the csrf protection require the usage of cookies which is not currently
# supported in this project
@method_decorator(csrf_exempt, name='dispatch')
class HardwareDetailsCommitHistoryView(View):
    required_params_get = ["origin"]
    cache_key_get_tree_data = "hardwareDetailsTreeData"
    cache_key_get_full_data = "hardwareDetailsFullData"

    def __init__(self):
        self.filterParams = None


    def get_commit_history(self, hardware_id: str, origin: str, start_date: datetime, end_date: datetime, commit_heads: Dict):
        # We need a subquery because if we filter by any hardware, it will get the
        # last head that has that hardware, but not the real head of the trees

        raw_query = """
        WITH filtered_checkouts AS (
            SELECT
                tree_name,
                git_repository_branch,
                git_repository_url,
                start_time
            FROM
                checkouts c
            WHERE
                (c.tree_name,
                c.git_repository_url,
                c.git_repository_branch,
                c.git_commit_hash) IN (
                        ('stable-rc', 'https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable-rc.git', 'linux-5.10.y', '53504d530e5ecd4c32edd34ab074f6e745bb4e4d'),
                        ('stable-rc', 'https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable-rc.git', 'linux-5.15.y', '765608b24f2192193901d4b27e0d5a0a248e043c')
                    )
                AND c.origin = 'maestro'
            )
            SELECT
                fc.tree_name AS tree_name,
                fc.git_repository_branch AS git_repository_branch,
                fc.git_repository_url AS git_repository_url,
                lateralus.git_commit_hash AS git_commit_hash,
                lateralus.start_time AS start_time
            FROM
                filtered_checkouts fc,
                LATERAL (
                SELECT
                    DISTINCT ON (c.git_commit_hash)
                    c.git_commit_hash,
                    c.start_time
                FROM
                    checkouts c
                WHERE
                    c.tree_name = fc.tree_name
                    AND c.git_repository_branch = fc.git_repository_branch
                    AND c.git_repository_url = fc.git_repository_url
                    AND c.start_time <= fc.start_time
                ORDER BY c.git_commit_hash, c.start_time
                LIMIT 5
            ) AS lateralus;
        """

        checkouts_query_set = Checkouts.objects.raw(raw_query)
        formatted_checkouts = []
        for idx, checkout in enumerate(checkouts_query_set):
            print(checkout)
            try:
                validate_checkout = CommitHistoryQuerysetItem(**checkout)
                formatted_checkouts.append(validate_checkout)
            except ValidationError as e:
                continue

        return formatted_checkouts


    # Using post to receive a body request
    def post(self, request, hardware_id):
        try:
            body = json.loads(request.body)

            post_body = CommitHistoryPostBody(**body)

            origin = post_body.origin
            end_datetime = datetime.fromtimestamp(
                int(post_body.endTimestampInSeconds),
                timezone.utc
            )

            start_datetime = datetime.fromtimestamp(
                int(post_body.startTimestampInSeconds),
                timezone.utc
            )

            commit_heads = post_body.commitHeads

            is_all_selected = len(commit_heads) == 0
        except ValidationError as e:
            return create_error_response(e.json())
        except json.JSONDecodeError:
            return create_error_response("Invalid body, request body must be a valid json string")
        except (ValueError, TypeError):
            return create_error_response("startTimestampInSeconds and endTimestampInSeconds must be a Unix Timestamp")

        commit_history = self.get_commit_history(hardware_id, origin, start_datetime, end_datetime, commit_heads)

        commit_history_table = {}

        return JsonResponse(
            {
                "commit_history_table " : commit_history_table
            }, safe=False
        )
