from collections import defaultdict
from django.db import connection
import json
from typing import Dict, Literal, List, TypedDict
from kernelCI_app.helpers.errorHandling import create_error_response
from kernelCI_app.helpers.logger import log_message
from django.utils.decorators import method_decorator
from django.views import View
from datetime import datetime, timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from kernelCI_app.helpers.trees import make_tree_identifier_key
from kernelCI_app.typeModels.hardwareDetails import (
    CommitHead,
    CommitHistoryPostBody,
    CommitHistoryValidCheckout,
)
from pydantic import ValidationError


BuildStatusType = Literal["valid", "invalid", "null"]


class GenerateQueryParamsResponse(TypedDict):
    query_params: Dict[str, Dict[str, str]]
    tuple_str: str


def generate_query_params(
    commit_heads: List[CommitHead],
) -> GenerateQueryParamsResponse:
    tuple_list = []
    params = {}

    for index, commit_head in enumerate(commit_heads):
        tree_name_key = f"tree_name{index}"
        git_repository_url_key = f"git_repository_url{index}"
        git_repository_branch_key = f"git_repository_branch{index}"
        git_commit_hash_key = f"git_commit_hash{index}"

        tuple_string = (
            f"(%({tree_name_key})s,"
            f"%({git_repository_url_key})s, %({git_repository_branch_key})s,"
            f"%({git_commit_hash_key})s)"
        )

        tuple_list.append(tuple_string)
        params[tree_name_key] = commit_head.treeName
        params[git_repository_url_key] = commit_head.repositoryUrl
        params[git_repository_branch_key] = commit_head.branch
        params[git_commit_hash_key] = commit_head.commitHash

    tuple_str = ", ".join(tuple_list)
    return {"tuple_str": f"({tuple_str})", "query_params": params}


# disable django csrf protection https://docs.djangoproject.com/en/5.0/ref/csrf/
# that protection is recommended for ‘unsafe’ methods (POST, PUT, and DELETE)
# but we are using POST here just to follow the convention to use the request body
# also the csrf protection require the usage of cookies which is not currently
# supported in this project
@method_decorator(csrf_exempt, name="dispatch")
class HardwareDetailsCommitHistoryView(View):
    required_params_get = ["origin"]
    cache_key_get_tree_data = "hardwareDetailsTreeData"
    cache_key_get_full_data = "hardwareDetailsFullData"

    def __init__(self):
        self.filterParams = None

    def get_commit_history(
        self,
        *,
        origin: str,
        start_date: datetime,
        end_date: datetime,
        commit_heads: List[CommitHead],
    ):
        # We need a subquery because if we filter by any hardware, it will get the
        # last head that has that hardware, but not the real head of the trees
        relevant_commit = commit_heads[0] if commit_heads else None

        if relevant_commit is None:
            return

        relevant_param_data = generate_query_params(commit_heads)

        raw_query = f"""
        WITH filtered_checkouts AS (
            SELECT
                DISTINCT ON	(tree_name,
                git_repository_url,
                git_repository_branch)
                tree_name,
                git_repository_url,
                git_repository_branch,
                start_time
            FROM
                checkouts c
            WHERE
                (c.tree_name,
                c.git_repository_url,
                c.git_repository_branch,
                c.git_commit_hash) IN {relevant_param_data['tuple_str']}
                AND c.origin = %(origin)s
            ORDER BY
                tree_name,
                git_repository_url,
                git_repository_branch,
                c.start_time)
            SELECT
                fc.tree_name AS tree_name,
                fc.git_repository_url AS git_repository_url,
                fc.git_repository_branch AS git_repository_branch,
                lateralus.git_commit_tags AS git_commit_tags,
                lateralus.git_commit_name AS git_commit_name,
                lateralus.git_commit_hash AS git_commit_hash,
                lateralus.start_time AS start_time
            FROM
                filtered_checkouts fc,
                LATERAL (
                SELECT
                    DISTINCT ON (c.git_commit_hash)
                    c.git_commit_tags,
                    c.git_commit_name,
                    c.git_commit_hash,
                    c.start_time
                FROM
                    checkouts c
                WHERE
                    c.tree_name = fc.tree_name
                    AND c.git_repository_branch = fc.git_repository_branch
                    AND c.git_repository_url = fc.git_repository_url
                    AND c.start_time <= fc.start_time
                    AND c.start_time >= %(start_date)s
                    AND c.start_time <= %(end_date)s
                ORDER BY c.git_commit_hash, c.start_time
            ) AS lateralus;
        """

        with connection.cursor() as cursor:
            cursor.execute(
                raw_query,
                {
                    **relevant_param_data["query_params"],
                    "origin": origin,
                    "start_date": start_date,
                    "end_date": end_date,
                },
            )
            checkouts_query_set = cursor.fetchall()

        formatted_checkouts = defaultdict(list)

        for checkout in checkouts_query_set:
            dict_checkout = {
                "tree_name": checkout[0],
                "git_repository_url": checkout[1],
                "git_repository_branch": checkout[2],
                "git_commit_tags": checkout[3],
                "git_commit_name": checkout[4],
                "git_commit_hash": checkout[5],
                "start_time": checkout[6],
            }
            try:
                validate_checkout = CommitHistoryValidCheckout(**dict_checkout)
                table_response_key = make_tree_identifier_key(
                    tree_name=validate_checkout.tree_name,
                    git_repository_url=validate_checkout.git_repository_url,
                    git_repository_branch=validate_checkout.git_repository_branch,
                )

                formatted_checkouts[table_response_key].append(
                    validate_checkout.model_dump()
                )
            except ValidationError as e:
                log_message(f"Error validating checkout {dict_checkout}: {e.json()}")
                continue

        return formatted_checkouts

    # Using post to receive a body request
    def post(self, request, hardware_id) -> JsonResponse:
        try:
            body = json.loads(request.body)

            post_body = CommitHistoryPostBody(**body)

            origin = post_body.origin
            end_datetime = datetime.fromtimestamp(
                int(post_body.endTimestampInSeconds), timezone.utc
            )

            start_datetime = datetime.fromtimestamp(
                int(post_body.startTimestampInSeconds), timezone.utc
            )

            commit_heads = post_body.commitHeads

        except ValidationError as e:
            return create_error_response(e.json())
        except json.JSONDecodeError:
            return create_error_response(
                "Invalid body, request body must be a valid json string"
            )
        except (ValueError, TypeError):
            return create_error_response(
                "startTimestampInSeconds and endTimestampInSeconds must be a Unix Timestamp"
            )

        commit_history = self.get_commit_history(
            origin=origin,
            start_date=start_datetime,
            end_date=end_datetime,
            commit_heads=commit_heads,
        )

        return JsonResponse({"commitHistoryTable": commit_history}, safe=False)
