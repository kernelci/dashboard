from http import HTTPStatus
from typing import Optional
from django.http import HttpRequest
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from pydantic import ValidationError

from kernelCI_app.helpers.errorHandling import (
    create_api_error_response,
)
from kernelCI_app.helpers.filters import FilterParams
from kernelCI_app.helpers.issueExtras import assign_issue_first_seen
from kernelCI_app.queries.issues import get_issue_listing_data
from kernelCI_app.typeModels.issueListing import (
    IssueListingResponse,
    IssueListingQueryParameters,
)
from kernelCI_app.typeModels.issues import (
    CULPRIT_CODE,
    CULPRIT_HARNESS,
    CULPRIT_TOOL,
    FirstIncident,
    PossibleIssueCulprits,
    ProcessedExtraDetailedIssues,
)


class IssueView(APIView):
    def __init__(self):
        self.processed_extra_issue_details: ProcessedExtraDetailedIssues = {}
        self.first_incidents: dict[str, FirstIncident] = {}

        self.filters: Optional[FilterParams] = None

    def _should_discard_issue_by_culprit(
        self, *, culprit_filters: set[PossibleIssueCulprits], record: dict
    ) -> bool:
        """Returns true if the record should be discarted from the resulting set of records"""

        if not culprit_filters:
            return False

        if record["culprit_code"] is True and CULPRIT_CODE in culprit_filters:
            return False
        if record["culprit_harness"] is True and CULPRIT_HARNESS in culprit_filters:
            return False
        if record["culprit_tool"] is True and CULPRIT_TOOL in culprit_filters:
            return False

        return True  # Discards if has filter but all the culprits are None

    def _filter_base_records(self, *, issue_records: list[dict]) -> list[dict]:
        """Filters the base list of issue records using self.filters"""
        culprit_filters = self.filters.filter_issue_culprits

        result: list[dict] = []
        for issue in issue_records:
            if self._should_discard_issue_by_culprit(
                culprit_filters=culprit_filters, record=issue
            ):
                continue

            result.append(issue)

        return result

    def _format_processing_for_response(self) -> None:
        for (
            issue_extras_id,
            issue_extras_data,
        ) in self.processed_extra_issue_details.items():
            self.first_incidents[issue_extras_id] = issue_extras_data["first_incident"]

    @extend_schema(
        parameters=[IssueListingQueryParameters],
        responses=IssueListingResponse,
        methods=["GET"],
    )
    def get(self, _request: HttpRequest) -> Response:
        try:
            request_params = IssueListingQueryParameters(
                interval_in_days=_request.GET.get("intervalInDays"),
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        interval_in_days = request_params.interval_in_days

        issue_records: list[dict] = get_issue_listing_data(
            interval=f"{interval_in_days} days",
        )

        if len(issue_records) == 0:
            return create_api_error_response(
                error_message="No issues found", status_code=HTTPStatus.OK
            )

        self.filters = FilterParams(_request)
        filtered_records = self._filter_base_records(issue_records=issue_records)

        issue_key_list = [(issue["id"], issue["version"]) for issue in filtered_records]
        assign_issue_first_seen(
            issue_key_list=issue_key_list,
            processed_issues_table=self.processed_extra_issue_details,
        )

        try:
            self._format_processing_for_response()
            valid_data = IssueListingResponse(
                issues=filtered_records, extras=self.first_incidents
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return Response(data=valid_data.model_dump())
