from django.http import JsonResponse
from django.views import View
from querybuilder.query import Query
from kernelCI_app.models import Checkouts, Builds
from kernelCI_app.serializers import TreeSerializer
from kernelCI_app.utils import get_visible_record_identifiers


class TreeView(View):

    def get(self, _):
        commit_hashs = get_visible_record_identifiers('checkouts')
        placeholders = ','.join(['%s'] * len(commit_hashs))

        checkouts = Checkouts.objects.raw(
            f"""
            SELECT
                checkouts.git_commit_hash AS id,
                COUNT(DISTINCT CASE WHEN builds.valid = true THEN builds.id END) AS valid_builds,
                COUNT(DISTINCT CASE WHEN builds.valid = false THEN builds.id END) AS invalid_builds,
                COUNT(DISTINCT CASE WHEN builds.valid IS NULL AND builds.id IS NOT NULL THEN builds.id END)
                    AS null_builds,
                COUNT(DISTINCT builds.id) AS total_builds,
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
                checkouts
            LEFT JOIN
                builds ON builds.checkout_id = checkouts.id
            LEFT JOIN
                tests ON tests.build_id = builds.id
            WHERE checkouts.git_commit_hash IN ({placeholders})
            GROUP BY
                checkouts.git_commit_hash;
            """,
            commit_hashs
        )

        serializer = TreeSerializer(checkouts, many=True)
        resp = JsonResponse(serializer.data, safe=False)
        return resp


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
                status = arch_summ.setdefault(arch, self.create_default_status())
                status[status_key] += 1
                compiler = build['compiler']
                if compiler and compiler not in status.setdefault('compilers', []):
                    status['compilers'].append(compiler)

        return {"builds": build_summ, "configs": config_summ, "architectures": arch_summ}

    def get_test_staus(self, build_id):
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

        for k in request.GET.keys():
            if k.startswith('filter_'):
                field = k[7:]
                if field in build_fields or field in checkout_fields:
                    filter_list = request.GET.getlist(k)
                    query.where({field: filter_list})

        records = query.select()
        for r in records:
            status = self.get_test_staus(r.get('id'))
            r['status'] = status

        summary = self.create_summary(records)

        return JsonResponse({"builds": records, "summary": summary}, safe=False)
