from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.queries.labs import get_lab_origins
from kernelCI_app.typeModels.origins import LabOriginsResponse, OriginsQueryParameters


class LabOriginsView(APIView):
    @extend_schema(
        parameters=[OriginsQueryParameters],
        responses={
            HTTPStatus.OK: LabOriginsResponse,
            HTTPStatus.BAD_REQUEST: dict[str, str],
        },
        methods=["GET"],
    )
    def get(self, request) -> Response:
        try:
            query_parameters = OriginsQueryParameters.model_validate(request.GET.dict())
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        lab_origins = get_lab_origins(
            interval_in_days=query_parameters.interval_in_days
        )

        try:
            valid_response = LabOriginsResponse(origins=sorted(lab_origins))
        except ValidationError as e:
            return Response(e.json(), HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())
