from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.queries.labs import get_lab_listing_data
from kernelCI_app.typeModels.commonListing import (
    ListingQueryParameters,
    ListingStatusCount,
)
from kernelCI_app.typeModels.labListing import (
    LabListingItem,
    LabListingResponse,
)


class LabView(APIView):
    def _sanitize_records(self, labs_raw: list[tuple]) -> list[LabListingItem]:
        labs = []
        for lab in labs_raw:
            labs.append(
                LabListingItem(
                    lab_name=lab[0],
                    build_status_summary=ListingStatusCount(
                        PASS=lab[1],
                        FAIL=lab[2],
                        INCONCLUSIVE=lab[3],
                    ),
                    boot_status_summary=ListingStatusCount(
                        PASS=lab[4],
                        FAIL=lab[5],
                        INCONCLUSIVE=lab[6],
                    ),
                    test_status_summary=ListingStatusCount(
                        PASS=lab[7],
                        FAIL=lab[8],
                        INCONCLUSIVE=lab[9],
                    ),
                )
            )

        return labs

    @extend_schema(
        parameters=[ListingQueryParameters],
        responses=LabListingResponse,
    )
    def get(self, request: Request):
        try:
            query_params = ListingQueryParameters(
                origin=request.GET.get("origin"),
                interval_in_days=request.GET.get("interval_in_days"),
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        labs_raw = get_lab_listing_data(
            origin=query_params.origin,
            interval_in_days=query_params.interval_in_days,
        )

        try:
            sanitized_records = self._sanitize_records(labs_raw=labs_raw)
            result = LabListingResponse(labs=sanitized_records)

            if len(result.labs) < 1:
                return create_api_error_response(
                    error_message=ClientStrings.NO_LABS_FOUND,
                    status_code=HTTPStatus.OK,
                )
        except ValidationError as e:
            return create_api_error_response(
                error_message=e.json(),
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        return Response(data=result.model_dump(), status=HTTPStatus.OK)
