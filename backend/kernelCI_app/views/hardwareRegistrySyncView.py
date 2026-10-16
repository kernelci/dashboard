from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.models import HardwareRegistrySync
from kernelCI_app.typeModels.hardwareListing import HardwareRegistrySyncResponse


class HardwareRegistrySyncView(APIView):
    @extend_schema(responses=HardwareRegistrySyncResponse)
    def get(self, request) -> Response:
        row = HardwareRegistrySync.objects.filter(pk=1).first()
        result = HardwareRegistrySyncResponse(
            synced_at=None if row is None else row.synced_at,
            files=[] if row is None else row.files,
        )
        return Response(data=result.model_dump(mode="json"), status=HTTPStatus.OK)
