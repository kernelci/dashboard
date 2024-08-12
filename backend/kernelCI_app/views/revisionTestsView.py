from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View
from django.db.models import Q, TextField, Sum, Count, Case, When, F, Func, Value, Min
from django.db.models.functions import Concat
from django.contrib.postgres.aggregates import ArrayAgg

from kernelCI_app.models import Tests
from kernelCI_app.serializers import BuildTestsSerializer
from kernelCI_app.utils import getErrorResponseBody


class revisionTests(View):

    def get(self, request):
        commit = request.GET.get('git_commit_hash')
        if not commit:
            return HttpResponseBadRequest(
                getErrorResponseBody('missing required field `git_commit_hash`')
            )

        patchset = request.GET.get('patchset_hash', '')
        path = request.GET.get('path', '')
        path_level = 1

        if path:
            if not path.endswith('.'):
                path += '.'
            path_level += path.count('.')
            filterQ = Q(path__startswith=path) | Q(path=path.rstrip('.'))
        else:
            filterQ = Q(path__startswith=path)

        commit_hash = '001f8443d480773117a013a07f774d252f369bea'

        result = (
            Tests.objects
            .filter(
                filterQ,
                build__checkout__git_commit_hash=commit_hash,
                build__checkout__patchset_hash=patchset
            )
            .values(
                path_sublevel=Func(
                    F('path'), Value('.'), Value(path_level),
                    function='SPLIT_PART', output_field=TextField()
                )
            )
            .annotate(
                fail_tests=Sum(Case(When(status='FAIL', then=1), default=0)),
                error_tests=Sum(Case(When(status='ERROR', then=1), default=0)),
                miss_tests=Sum(Case(When(status='MISS', then=1), default=0)),
                pass_tests=Sum(Case(When(status='PASS', then=1), default=0)),
                done_tests=Sum(Case(When(status='DONE', then=1), default=0)),
                skip_tests=Sum(Case(When(status='SKIP', then=1), default=0)),
                null_tests=Sum(Case(When(status__isnull=True, then=1), default=0)),
                total_tests=Count('id'),
                current_path=Concat(Value(path), F('path_sublevel'), output_field=TextField()),
                origins=ArrayAgg('origin', distinct=True),
                start_time=Min('start_time'),
            )
        )

        for r in result:
            print('r:', r)

        serializer = BuildTestsSerializer(result, many=True)
        return JsonResponse(serializer.data, safe=False)
