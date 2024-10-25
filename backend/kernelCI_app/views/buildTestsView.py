from django.http import JsonResponse
from django.views import View

from kernelCI_app.models import Tests


class BuildTests(View):

    def get(self, request, build_id):
        result = Tests.objects.filter(build_id=build_id).values(
            'id', 'duration', 'status', 'path', 'start_time'
        )

        camel_case_result = [
            {
                'id': test['id'],
                'duration': test['duration'],
                'status': test['status'],
                'path': test['path'],
                'startTime': test['start_time'],
            }
            for test in result
        ]

        return JsonResponse(camel_case_result, safe=False)
