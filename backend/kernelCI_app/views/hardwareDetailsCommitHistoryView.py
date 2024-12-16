from collections import defaultdict
from django.db.models import Subquery
import json
from typing import Dict, List, Optional, Set, Literal
from kernelCI_app.helpers.errorHandling import create_error_response
from kernelCI_app.helpers.filters import (
    should_increment_test_issue,
    is_build_invalid,
)
from kernelCI_app.helpers.logger import log_message
from django.utils.decorators import method_decorator
from django.views import View
from datetime import datetime, timezone
from django.http import JsonResponse
from kernelCI_app.viewCommon import create_details_build_summary
from kernelCI_app.models import Tests
from kernelCI_app.utils import (
    extract_error_message,
    extract_platform,
)
from django.views.decorators.csrf import csrf_exempt
from kernelCI_app.helpers.trees import get_tree_heads
from kernelCI_app.typeModels.hardwareDetails import CommitHistoryPostBody
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


    def handle_test(self, record, tests):
        status = record["status"]

        tests["history"].append(get_history(record))
        tests["statusSummary"][status] += 1
        tests["configs"][record["build__config_name"]][status] += 1

        if status == "ERROR" or status == "FAIL" or status == "MISS":
            tests["platformsFailing"].add(
                extract_platform(record["environment_misc"])
            )
            tests["failReasons"][extract_error_message(record["misc"])] += 1

        archKey = f'{record["build__architecture"]}{record["build__compiler"]}'
        archSummary = tests["archSummary"].get(archKey)
        if not archSummary:
            archSummary = get_arch_summary(record)
            tests["archSummary"][archKey] = archSummary
        archSummary["status"][status] += 1

        update_issues(
            issue_id=record["incidents__issue__id"],
            incident_test_id=record["incidents__test_id"],
            build_valid=record["build__valid"],
            issue_comment=record["incidents__issue__comment"],
            issue_report_url=record["incidents__issue__report_url"],
            task=tests,
            is_failed_task=status == STATUS_FAILED_VALUE,
            issue_from="test"
        )

    def get_filter_options(self, records, selected_trees, is_all_selected: bool):
        configs = set()
        archs = set()
        compilers = set()

        for r in records:
            current_tree = get_record_tree(r, selected_trees)
            if not current_tree or not is_record_tree_selected(r, current_tree, is_all_selected):
                continue

            configs.add(r['build__config_name'])
            archs.add(r['build__architecture'])
            compilers.add(r['build__compiler'])

        return list(configs), list(archs), list(compilers)

    # Status Summary should be unaffected by filters because it is placed above filters in the UI
    def handle_tree_status_summary(
        self,
        record: Dict,
        tree_status_summary: Dict,
        tree_index: str,
        processed_builds: Set[str],
        is_record_boot: bool,
    ) -> None:
        tree_status_key = "boots" if is_record_boot else "tests"
        tree_status_summary[tree_index][tree_status_key][record["status"]] += 1

        if record["build_id"] not in processed_builds:
            build_status = get_build_status(record["build__valid"])
            tree_status_summary[tree_index]["builds"][build_status] += 1

    def get_commit_history(self, hardware_id: str, origin: str, start_date: datetime, end_date: datetime, commit_heads: Dict):
        # We need a subquery because if we filter by any hardware, it will get the
        # last head that has that hardware, but not the real head of the trees
        trees_subquery = get_tree_heads(
            origin, start_date, end_date
        )

        tree_id_fields = [
            "build__checkout__tree_name",
            "build__checkout__git_repository_branch",
            "build__checkout__git_repository_url",
        ]

        trees_query_set = Tests.objects.filter(
            environment_compatible__contains=[hardware_id],
            origin=origin,
            build__checkout__start_time__lte=end_date,
            build__checkout__start_time__gte=start_date,
            build__checkout__git_commit_hash__in=Subquery(trees_subquery),
        ).values(
            *tree_id_fields,
            "build__checkout__git_commit_name",
            "build__checkout__git_commit_hash",
        ).distinct(
            *tree_id_fields,
            "build__checkout__git_commit_hash",
        ).order_by(
            *tree_id_fields,
            "build__checkout__git_commit_hash",
            "-build__checkout__start_time"
        )

        trees = []
        for idx, tree in enumerate(trees_query_set):
            trees.append(
                {
                    "treeName": tree["build__checkout__tree_name"],
                    "gitRepositoryBranch": tree[
                        "build__checkout__git_repository_branch"
                    ],
                    "gitRepositoryUrl": tree["build__checkout__git_repository_url"],
                    "headGitCommitName": tree["build__checkout__git_commit_name"],
                    "headGitCommitHash": tree["build__checkout__git_commit_hash"],
                    "index": str(idx),
                }
            )

        return trees


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
