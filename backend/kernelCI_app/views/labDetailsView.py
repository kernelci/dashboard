from http import HTTPStatus
from typing import Optional

from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.helpers.lab_details import (
    build_lab_attention_response,
    build_lab_boot_rows,
    build_lab_build_rows,
    build_lab_details_response,
    build_lab_test_rows,
    parse_tree_filters,
)
from kernelCI_app.queries.lab_details import (
    get_lab_attention_items,
    get_lab_build_rows,
    get_lab_test_rows,
)
from kernelCI_app.typeModels.commonListing import ListingQueryParameters
from kernelCI_app.typeModels.labDetails import (
    LabAttentionResponse,
    LabBootRowsResponse,
    LabBuildRowsResponse,
    LabDetailsResponse,
    LabTestRowsResponse,
)


def _parse_listing_params(
    request: Request,
) -> tuple[Optional[ListingQueryParameters], Optional[Response]]:
    try:
        params = ListingQueryParameters(
            origin=request.GET.get("origin"),
            interval_in_days=request.GET.get("interval_in_days"),
        )
    except ValidationError as e:
        return None, Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)
    return params, None


class LabDetailsView(APIView):
    @extend_schema(
        parameters=[ListingQueryParameters],
        responses=LabDetailsResponse,
    )
    def get(self, request: Request, lab_name: str) -> Response:
        params, error = _parse_listing_params(request)
        if error:
            return error

        build_rows = get_lab_build_rows(
            lab_name=lab_name,
            origin=params.origin,
            interval_in_days=params.interval_in_days,
        )
        test_rows = get_lab_test_rows(
            lab_name=lab_name,
            origin=params.origin,
            interval_in_days=params.interval_in_days,
        )
        try:
            result = build_lab_details_response(
                lab_name=lab_name,
                interval_in_days=params.interval_in_days,
                build_rows=build_rows,
                test_rows=test_rows,
            )
        except ValidationError as e:
            return create_api_error_response(
                error_message=e.json(),
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        return Response(data=result.model_dump(), status=HTTPStatus.OK)


class LabDetailsBuildsView(APIView):
    @extend_schema(
        parameters=[ListingQueryParameters],
        responses=LabBuildRowsResponse,
    )
    def get(self, request: Request, lab_name: str) -> Response:
        params, error = _parse_listing_params(request)
        if error:
            return error
        tree_filters = parse_tree_filters(request.GET.getlist("tree"))
        build_rows = get_lab_build_rows(
            lab_name=lab_name,
            origin=params.origin,
            interval_in_days=params.interval_in_days,
            tree_filters=tree_filters,
        )
        result = build_lab_build_rows(build_rows)
        return Response(data=result.model_dump(), status=HTTPStatus.OK)


class LabDetailsBootsView(APIView):
    @extend_schema(
        parameters=[ListingQueryParameters],
        responses=LabBootRowsResponse,
    )
    def get(self, request: Request, lab_name: str) -> Response:
        params, error = _parse_listing_params(request)
        if error:
            return error
        tree_filters = parse_tree_filters(request.GET.getlist("tree"))
        test_rows = get_lab_test_rows(
            lab_name=lab_name,
            origin=params.origin,
            interval_in_days=params.interval_in_days,
            tree_filters=tree_filters,
        )
        result = build_lab_boot_rows(test_rows)
        return Response(data=result.model_dump(), status=HTTPStatus.OK)


class LabDetailsTestsView(APIView):
    @extend_schema(
        parameters=[ListingQueryParameters],
        responses=LabTestRowsResponse,
    )
    def get(self, request: Request, lab_name: str) -> Response:
        params, error = _parse_listing_params(request)
        if error:
            return error
        tree_filters = parse_tree_filters(request.GET.getlist("tree"))
        test_rows = get_lab_test_rows(
            lab_name=lab_name,
            origin=params.origin,
            interval_in_days=params.interval_in_days,
            tree_filters=tree_filters,
        )
        result = build_lab_test_rows(test_rows, lab_name=lab_name)
        return Response(data=result.model_dump(), status=HTTPStatus.OK)


class LabDetailsAttentionView(APIView):
    @extend_schema(
        parameters=[ListingQueryParameters],
        responses=LabAttentionResponse,
    )
    def get(self, request: Request, lab_name: str) -> Response:
        params, error = _parse_listing_params(request)
        if error:
            return error
        rows = get_lab_attention_items(
            lab_name=lab_name,
            origin=params.origin,
            interval_in_days=params.interval_in_days,
        )
        result = build_lab_attention_response(rows)
        return Response(data=result.model_dump(), status=HTTPStatus.OK)
