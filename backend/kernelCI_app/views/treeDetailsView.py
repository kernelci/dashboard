from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View
from querybuilder.query import Query
from kernelCI_app.models import Builds
from kernelCI_app.utils import FilterParams, InvalidComparisonOP, getErrorResponseBody


class TreeDetails(View):

    def create_default_status(self):
        return {"valid": 0, "invalid": 0, "null": 0}

    def create_summary(self, builds_dict):
        status_map = {True: 'valid', False: 'invalid', None: 'null'}

        build_summ = self.create_default_status()
        config_summ = {}
        arch_summ = {}

        for build in builds_dict:
            status_key = status_map[build['valid']]
            build_summ[status_key] += 1

            if config := build['config_name']:
                status = config_summ.get(config)
                if not status:
                    status = self.create_default_status()
                    config_summ[config] = status
                status[status_key] += 1

            if arch := build['architecture']:
                status = arch_summ.setdefault(
                    arch, self.create_default_status())
                status[status_key] += 1
                compiler = build['compiler']
                if compiler and compiler not in status.setdefault('compilers', []):
                    status['compilers'].append(compiler)

        return {"builds": build_summ, "configs": config_summ, "architectures": arch_summ}

    def get_test_status(self, build_id):
        status_keys = ["fail_tests", "error_tests", "miss_tests", "pass_tests",
                       "done_tests", "skip_tests", "null_tests", "total_tests"]
        builds = Builds.objects.raw(
            """
            SELECT
                builds.id,
                COUNT(CASE WHEN tests.status = 'FAIL' THEN 1 END) AS fail_tests,
                COUNT(CASE WHEN tests.status = 'ERROR' THEN 1 END) AS error_tests,
                COUNT(CASE WHEN tests.status = 'MISS' THEN 1 END) AS miss_tests,
                COUNT(CASE WHEN tests.status = 'PASS' THEN 1 END) AS pass_tests,
                COUNT(CASE WHEN tests.status = 'DONE' THEN 1 END) AS done_tests,
                COUNT(CASE WHEN tests.status = 'SKIP' THEN 1 END) AS skip_tests,
                SUM(CASE WHEN tests.status IS NULL AND tests.id IS NOT NULL THEN 1 ELSE 0 END)
                    AS null_tests,
                COUNT(tests.id) AS total_tests
            FROM
                builds
            LEFT JOIN
                tests ON tests.build_id = builds.id
            WHERE builds.id = %s
            GROUP BY builds.id;
            """,
            [build_id]
        )
        return {k: getattr(builds[0], k) for k in status_keys}

    def get(self, request, commit_hash):
        build_fields = [
            'id', 'architecture', 'config_name', 'misc', 'config_url',
            'compiler', 'valid', 'duration', 'log_url', 'start_time']
        checkout_fields = [
            'git_repository_branch', 'git_repository_url', 'git_repository_branch']

        query = Query().from_table(Builds, build_fields).join(
            'checkouts',
            condition='checkouts.id = builds.checkout_id',
            fields=checkout_fields
        ).where(git_commit_hash__eq=commit_hash)

        try:
            filter_params = FilterParams(request)
        except InvalidComparisonOP as e:
            return HttpResponseBadRequest(getErrorResponseBody(str(e)))

        for f in filter_params.filters:
            field = f['field']
            table = None
            if field in build_fields:
                table = 'builds'
            elif field in checkout_fields:
                table = 'checkouts'
            elif field == 'buildStatus':
                table = 'builds'
                field = 'valid'
                f['value'] = f['value'] == 'Success'
            if table:
                query.where(
                    **{f'{table}.{field}__{f['comparison_op']}': f['value']})

        records = query.select()
        for r in records:
            status = self.get_test_status(r.get('id'))
            r['status'] = status

        summary = self.create_summary(records)

        return JsonResponse({"builds": records, "summary": summary}, safe=False)
