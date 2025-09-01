from datetime import datetime
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
from kernelCI_app.helpers.issueExtras import process_issues_extra_details
from kernelCI_app.helpers.issueListing import should_discard_issue_record
from kernelCI_app.queries.issues import get_issue_listing_data
from kernelCI_app.typeModels.issueListing import (
    IssueListingFilters,
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
from kernelCI_app.constants.localization import ClientStrings


class IssueView(APIView):
    def __init__(self):
        self.processed_extra_issue_details: ProcessedExtraDetailedIssues = {}
        self.first_incidents: dict[str, FirstIncident] = {}

        self.unprocessed_origins: set[str] = set()
        self.unprocessed_culprits: set[PossibleIssueCulprits] = set()
        self.unprocessed_categories: set[str] = set()

        self.filters: Optional[FilterParams] = None

    def _add_unprocessed_culprits(self, *, issue: dict) -> None:
        if issue["culprit_code"]:
            self.unprocessed_culprits.add(CULPRIT_CODE)
        if issue["culprit_harness"]:
            self.unprocessed_culprits.add(CULPRIT_HARNESS)
        if issue["culprit_tool"]:
            self.unprocessed_culprits.add(CULPRIT_TOOL)

    def _add_unprocessed_categories(self, *, categories: Optional[list[str]]) -> None:
        if not categories:
            return

        for category in categories:
            self.unprocessed_categories.add(category)

    def _filter_records(self, *, issue_records: list[dict]) -> list[dict]:
        """Filters the base list of issue records using self.filters"""

        result: list[dict] = []

        for issue in issue_records:
            self.unprocessed_origins.add(issue["origin"])
            self._add_unprocessed_culprits(issue=issue)
            self._add_unprocessed_categories(categories=issue["categories"])

            if should_discard_issue_record(filters=self.filters, issue=issue):
                continue

            result.append(issue)

        return result

    def _filter_records_by_extras(self, *, records: list[dict]):
        """Filters out the extra details and the records with it.

        Receives the list of records to be filtered based on the extra details

        Returns the filtered extra_issue_details and filtered records"""
        # Checks if there are issues with no checkouts and filters them out
        issues_without_trees = set()
        processed_extras_with_trees = {}
        for issue_id, issue_extras_data in self.processed_extra_issue_details.items():
            for info in issue_extras_data.versions.values():
                if not info.trees:
                    issues_without_trees.add(issue_id)
                else:
                    processed_extras_with_trees[issue_id] = issue_extras_data

        refiltered_records = []
        for issue in records:
            if issue["id"] in issues_without_trees:
                continue
            refiltered_records.append(issue)

        return (processed_extras_with_trees, refiltered_records)

    def _format_processing_for_response(self) -> None:
        for (
            issue_extras_id,
            issue_extras_data,
        ) in self.processed_extra_issue_details.items():
            self.first_incidents[issue_extras_id] = issue_extras_data.first_incident

    @extend_schema(
        parameters=[IssueListingQueryParameters],
        responses=IssueListingResponse,
        methods=["GET"],
    )
    def get(self, _request: HttpRequest) -> Response:
        try:
            request_params = IssueListingQueryParameters.model_validate(
                _request.GET.dict()
            )

            valid_starting_date = datetime.now()
            if request_params.starting_date_iso_format is not None:
                valid_starting_date = datetime.fromisoformat(
                    request_params.starting_date_iso_format
                )
        except ValidationError as e:
            return create_api_error_response(error_message=e.json())
        except ValueError as e:
            return create_api_error_response(error_message=str(e))

        issue_records: list[dict] = get_issue_listing_data(
            interval=f"{request_params.interval_in_days} days",
            starting_date=valid_starting_date,
        )

        if len(issue_records) == 0:
            return create_api_error_response(
                error_message=ClientStrings.NO_ISSUE_FOUND, status_code=HTTPStatus.OK
            )

        self.filters = FilterParams(_request)
        filtered_records = self._filter_records(issue_records=issue_records)

        issue_key_list = [(issue["id"], issue["version"]) for issue in filtered_records]
        # The endpoint only returns the first_seen data, but getting the trees data is useful
        # to filter out issues with incidents that are related to unexistent builds/checkouts
        process_issues_extra_details(
            issue_key_list=issue_key_list,
            processed_issues_table=self.processed_extra_issue_details,
        )

        (self.processed_extra_issue_details, refiltered_records) = (
            self._filter_records_by_extras(records=filtered_records)
        )

        self._format_processing_for_response()

        try:
            valid_data = IssueListingResponse(
                issues=refiltered_records,
                extras=self.first_incidents,
                filters=IssueListingFilters(
                    origins=sorted(self.unprocessed_origins),
                    culprits=sorted(self.unprocessed_culprits),
                    categories=sorted(self.unprocessed_categories),
                ),
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return Response(data=valid_data.model_dump())
