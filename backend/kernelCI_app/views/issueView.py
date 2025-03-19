from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from pydantic import ValidationError

from kernelCI_app.helpers.errorHandling import (
    create_api_error_response,
)
from kernelCI_app.helpers.issueExtras import assign_issue_first_seen
from kernelCI_app.models import Issues
from kernelCI_app.typeModels.commonListing import ListingQueryParameters
from kernelCI_app.typeModels.issueListing import (
    IssueListingResponse,
)
from kernelCI_app.typeModels.issues import FirstIncident, ProcessedExtraDetailedIssues


def get_issue_listing_data(interval_date):
    issues_records = Issues.objects.values(
        "id",
        "field_timestamp",
        "comment",
        "version",
        "origin",
        "culprit_code",
        "culprit_harness",
        "culprit_tool",
    ).filter(
        field_timestamp__gte=interval_date,
    )
    return issues_records


class IssueView(APIView):
    def __init__(self):
        self.issue_records: list[dict[str]] = []
        self.processed_extra_issue_details: ProcessedExtraDetailedIssues = {}
        self.first_incidents: dict[str, FirstIncident] = {}

    def _format_processing_for_response(self) -> None:
        for (
            issue_extras_id,
            issue_extras_data,
        ) in self.processed_extra_issue_details.items():
            self.first_incidents[issue_extras_id] = issue_extras_data["first_incident"]

    @extend_schema(
        parameters=[ListingQueryParameters],
        responses=IssueListingResponse,
        methods=["GET"],
    )
    def get(self, _request) -> Response:
        try:
            request_params = ListingQueryParameters(
                interval_in_days=_request.GET.get("intervalInDays"),
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        interval_in_days = request_params.interval_in_days

        interval_date = datetime.now(timezone.utc) - timedelta(days=interval_in_days)
        interval_param = interval_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        self.issue_records = get_issue_listing_data(interval_date=interval_param)

        if len(self.issue_records) == 0:
            return create_api_error_response(
                error_message="No issues found", status_code=HTTPStatus.OK
            )

        issue_key_list = [
            (issue["id"], issue["version"]) for issue in self.issue_records
        ]
        assign_issue_first_seen(
            issue_key_list=issue_key_list,
            processed_issues_table=self.processed_extra_issue_details,
        )

        try:
            self._format_processing_for_response()
            valid_data = IssueListingResponse(
                issues=self.issue_records, extras=self.first_incidents
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return Response(data=valid_data.model_dump())
