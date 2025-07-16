from http import HTTPStatus

from pydantic import ValidationError
from kernelCI_app.helpers.errorHandling import create_api_error_response
from rest_framework.views import APIView
from rest_framework.response import Response
from kernelCI_app.helpers.logger import log_message
from kernelCI_app.queries.checkout import get_origins
from drf_spectacular.utils import extend_schema

from kernelCI_app.typeModels.origins import OriginsQueryParameters, OriginsResponse


# For now we are hardcoding test origins since fetching them dynamically in a query is taking
# around 8 minutes to finish. That time will result in a timeout every request, so this is a
# temporary solution. Another option would be to create a cron job that feeds a TestOriginsCache
# sqlite table, from which this endpoint would fetch.
#
# TODO: replace with a dynamic approach
TEST_ORIGINS = [
    "0dayci",
    "arm",
    "broonie",
    "linaro",
    "maestro",
    "microsoft",
    "redhat",
    "riscv",
    "syzbot",
    "ti",
]


def separate_origin_records(*, records: list[dict[str, str]]) -> set[str]:
    """Iterates over the records for origins and returns a set for each table defined by those records

    Params:
      records: a list of records in the form of {"origin": "foo", "table": "bar"}

    Returns:
      The origin sets for each table"""

    if not records:
        return set()

    checkout_origins: set[str] = set()
    for record in records:
        origin = record.get("origin")
        if not origin:
            continue

        table = record.get("table")
        match table:
            case "checkouts":
                checkout_origins.add(origin)
            case _:
                log_message(f"Unable to treat table {table} in origins view")

    return checkout_origins


class OriginsView(APIView):
    def __init__(self):
        self.checkout_origins: set[str] = set()

    @extend_schema(
        parameters=[OriginsQueryParameters],
        responses={
            HTTPStatus.OK: OriginsResponse,
            HTTPStatus.BAD_REQUEST: dict[str, str],
        },
        methods=["GET"],
    )
    def get(self, request) -> Response:
        try:
            query_parameters = OriginsQueryParameters.model_validate(request.GET.dict())
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        origin_records = get_origins(interval_in_days=query_parameters.interval_in_days)

        if len(origin_records) == 0:
            return create_api_error_response(error_message="No origins found")

        self.checkout_origins = separate_origin_records(records=origin_records)

        try:
            valid_response = OriginsResponse(
                checkout_origins=sorted(self.checkout_origins),
                test_origins=TEST_ORIGINS,
            )
        except ValidationError as e:
            return Response(e.json(), HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())
