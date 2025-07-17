from http import HTTPStatus
import json

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.helpers.issueExtras import (
    process_issues_extra_details,
)
from kernelCI_app.typeModels.issues import (
    IssueExtraDetailsRequest,
    IssueExtraDetailsResponse,
    ProcessedExtraDetailedIssues,
)
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from pydantic import ValidationError
from kernelCI_app.constants.localization import ClientStrings


# disable django csrf protection https://docs.djangoproject.com/en/5.0/ref/csrf/
# that protection is recommended for ‘unsafe’ methods (POST, PUT, and DELETE)
# but we are using POST here just to follow the convention to use the request body
# also the csrf protection require the usage of cookies which is not currently
# supported in this project
@method_decorator(csrf_exempt, name="dispatch")
class IssueExtraDetails(APIView):
    def __init__(self):
        self.processed_detailed_issues: ProcessedExtraDetailedIssues = {}

    @extend_schema(
        request=IssueExtraDetailsRequest,
        responses=IssueExtraDetailsResponse,
        methods=["POST"],
    )
    def post(self, request) -> Response:
        try:
            body = json.loads(request.body)
            valid_body = IssueExtraDetailsRequest(**body)
        except json.JSONDecodeError:
            return create_api_error_response(
                error_message=ClientStrings.INVALID_JSON_BODY,
            )
        except ValidationError as e:
            return Response(e.json(), status=HTTPStatus.BAD_REQUEST)

        issue_list = valid_body.issues

        if len(issue_list) == 0:
            return create_api_error_response(
                error_message=ClientStrings.ISSUE_EMPTY_LIST
            )

        process_issues_extra_details(
            issue_key_list=issue_list,
            processed_issues_table=self.processed_detailed_issues,
        )

        if not self.processed_detailed_issues:
            return create_api_error_response(
                error_message=ClientStrings.ISSUE_NO_EXTRA_DETAILS,
                status_code=HTTPStatus.OK,
            )

        try:
            valid_response = IssueExtraDetailsResponse(
                issues=self.processed_detailed_issues
            )
        except ValidationError as e:
            return Response(e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return Response(valid_response.model_dump(), status=HTTPStatus.OK)
