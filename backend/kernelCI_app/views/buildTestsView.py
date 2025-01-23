from django.http import JsonResponse
from django.views import View
from http import HTTPStatus
from kernelCI_app.helpers.errorHandling import create_error_response
from kernelCI_app.models import Tests


class BuildTests(View):
    def get(self, request, build_id):
        result = Tests.objects.filter(build_id=build_id).values(
            "id", "duration", "status", "path", "start_time", "environment_compatible"
        )

        if not result:
            return create_error_response(
                error_message="No tests found for this build",
                status_code=HTTPStatus.OK,
            )

        return JsonResponse(list(result), safe=False)
