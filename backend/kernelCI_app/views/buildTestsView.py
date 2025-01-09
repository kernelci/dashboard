from django.http import JsonResponse
from django.views import View
from http import HTTPStatus
from kernelCI_app.helpers.errorHandling import create_error_response
from kernelCI_app.models import Tests


class BuildTests(View):

    def get(self, request, build_id):
        result = Tests.objects.filter(build_id=build_id).values(
            'id', 'duration', 'status', 'path', 'start_time', 'environment_compatible'
        )

        if not result:
            return create_error_response(
                error_message="Tests not found for this build", status_code=HTTPStatus.NOT_FOUND
            )

        camel_case_result = [
            {
                'id': test['id'],
                'duration': test['duration'],
                'status': test['status'],
                'path': test['path'],
                'startTime': test['start_time'],
                'hardware': test['environment_compatible']
            }
            for test in result
        ]

        return JsonResponse(camel_case_result, safe=False)
