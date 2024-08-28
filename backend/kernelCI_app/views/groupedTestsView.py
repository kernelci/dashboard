from django.http import JsonResponse
from django.views import View
from django.db.models import Q, TextField, Sum, Count, Case, When, F, Func, Value
from django.db.models.functions import Concat
from django.contrib.postgres.aggregates import ArrayAgg

from utils.validation import validate_required_params
from kernelCI_app.models import Tests
from kernelCI_app.serializers import GroupedTestsSerializer


class groupedTests(View):

    def get(self, request):
        commit = request.GET.get('git_commit_hash')
        branch = request.GET.get('git_repository_branch')
        url = request.GET.get('git_repository_url')
        origin = request.GET.get('origin')

        get_required_params = ['git_commit_hash', 'git_repository_branch', 'git_repository_url' 'origin']
        validate_required_params(request, get_required_params)

        path = request.GET.get('path', '')
        if path:
            if not path.endswith('.'):
                path += '.'

        result = (
            Tests.objects
            .filter(
                build__checkout__git_commit_hash=commit,
                build__checkout__git_repository_branch=branch,
                build__checkout__git_repository_url=url,
                build__checkout__origin=origin,
                path__startswith=path,
            )
            .annotate(
                first_path_segment=Func(
                    F('path'), Value('.'), Value(1),
                    function='SPLIT_PART', output_field=TextField()
                )
            )
            .exclude(
                Q(first_path_segment='boot') | Q(first_path_segment__startswith='boot.')
            )
            .values('first_path_segment')
            .annotate(
                fail_tests=Sum(Case(When(status='FAIL', then=1), default=0)),
                error_tests=Sum(Case(When(status='ERROR', then=1), default=0)),
                miss_tests=Sum(Case(When(status='MISS', then=1), default=0)),
                pass_tests=Sum(Case(When(status='PASS', then=1), default=0)),
                done_tests=Sum(Case(When(status='DONE', then=1), default=0)),
                skip_tests=Sum(Case(When(status='SKIP', then=1), default=0)),
                null_tests=Sum(Case(When(status__isnull=True, then=1), default=0)),
                total_tests=Count('id'),
                path_group=F('first_path_segment'),
                individual_tests=ArrayAgg(
                    Concat(
                        F('path'), Value(', '),
                        F('status'), Value(', '),
                        F('start_time'), Value(', '),
                        F('duration'),
                        output_field=TextField()
                    ),
                    distinct=True
                ),
            )
            .order_by('first_path_segment')
        )

        for item in result:
            item['individual_tests'] = [
                {
                    'path': test[0],
                    'status': test[1],
                    'start_time': test[2],
                    'duration': test[3]
                }
                for test_info in item['individual_tests']
                if (test := test_info.split(', '))
            ]

        serializer = GroupedTestsSerializer(result, many=True)
        return JsonResponse(serializer.data, safe=False)
