from http import HTTPStatus
from urllib.parse import quote_plus

from django.http import HttpRequest
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from pydantic import ValidationError

from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.helpers.trees import sanitize_tree
from kernelCI_app.management.commands.helpers.summary import TreeKey
from kernelCI_app.management.commands.notifications import evaluate_test_results
from kernelCI_app.queries.notifications import get_checkout_summary_data
from kernelCI_app.typeModels.treeReport import (
    TreeReportQueryParameters,
    TreeReportResponse,
)
from kernelCI_app.constants.localization import ClientStrings


class TreeReport(APIView):
    @extend_schema(
        responses=TreeReportResponse,
        parameters=[TreeReportQueryParameters],
        methods=["GET"],
    )
    def get(self, request: HttpRequest):
        try:
            params = TreeReportQueryParameters(
                origin=request.GET.get("origin"),
                git_branch=request.GET.get("git_branch"),
                git_url=request.GET.get("git_url"),
                path=request.GET.getlist("path"),
                group_size=request.GET.get("group_size"),
                min_age_in_hours=request.GET.get("min_age_in_hours"),
                max_age_in_hours=request.GET.get("max_age_in_hours"),
            )
            origin = params.origin
            git_url = params.git_url
            git_branch = params.git_branch
        except ValidationError as e:
            return create_api_error_response(error_message=e.json())

        if params.min_age_in_hours >= params.max_age_in_hours:
            return create_api_error_response(
                error_message=ClientStrings.TREE_REPORT_MIN_MAX_AGE
            )

        min_query_interval = f"{params.min_age_in_hours} hours"
        max_query_interval = f"{params.max_age_in_hours} hours"

        # Even though this is using a single key and could be swapped for the treeListing query directly,
        # it is better to keep the same query as the notification command
        tree_key: TreeKey = (git_branch, git_url, origin)
        records = get_checkout_summary_data(
            tuple_params=[tree_key],
            interval_min=min_query_interval,
            interval_max=max_query_interval,
        )
        if not records:
            return create_api_error_response(
                error_message=ClientStrings.TREE_NOT_FOUND_IN_INTERVAL,
                status_code=HTTPStatus.OK,
            )
        record = records[0]

        checkout = sanitize_tree(record)
        tree_name = checkout.tree_name
        branch = checkout.git_repository_branch
        commit_hash = checkout.git_commit_hash
        git_url_safe = quote_plus(checkout.git_repository_url)

        if tree_name and branch:
            dashboard_url = f"https://d.kernelci.org/tree/{tree_name}/{branch}/{commit_hash}?o={origin}"
        else:
            dashboard_url = f"""https://d.kernelci.org/tree/{commit_hash}
                ?ti%7Cc={checkout.git_commit_name}
                &ti%7Cch={commit_hash}
                &ti%7Cgb={branch}
                &ti%7Cgu={git_url_safe}
                &ti%7Ct={tree_name}
                &o={origin}"""

        try:
            new_issues, fixed_issues, unstable_tests = evaluate_test_results(
                origin=origin,
                giturl=git_url,
                branch=git_branch,
                commit_hash=commit_hash,
                path=params.path,
                interval=max_query_interval,
                group_size=params.group_size,
            )

            valid_response = TreeReportResponse(
                dashboard_url=dashboard_url,
                git_url=git_url,
                git_branch=branch,
                commit_hash=commit_hash,
                origin=origin,
                checkout_start_time=checkout.start_time,
                build_status_summary=checkout.build_status,
                boot_status_summary=checkout.boot_status,
                test_status_summary=checkout.test_status,
                possible_regressions=new_issues,
                fixed_regressions=fixed_issues,
                unstable_tests=unstable_tests,
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)
        except Exception as e:
            return create_api_error_response(
                error_message=str(e),
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        return Response(valid_response.model_dump())
