from collections import defaultdict
from django.http import HttpResponseBadRequest, JsonResponse
from django.views import View
from kernelCI_app.utils import (FilterParams, InvalidComparisonOP,
                                extract_error_message, extract_platform, getErrorResponseBody)
from kernelCI_app.models import Checkouts


class TreeTestsView(View):
    # TODO misc_environment is not stable and should be used as a POC only
    # use the standardized field when that gets available
    valid_filter_fields = ['status', 'duration']

    def __paramsFromBootAndFilters(self, commit_hash, path_param, filter_params, params):
        if path_param:
            # TODO: 'boot' and 'boot.', right now is only using 'boot.'
            path_filter = "AND t.path LIKE %s"
            params.append(f'{path_param}%')
        else:
            path_filter = ""

        for f in filter_params.filters:
            field = f['field']
            if field not in self.valid_filter_fields:
                continue
            value = f['value']
            value_is_list = isinstance(value, list)
            if value_is_list:
                placeholder = ",".join(
                    ['%s' for i in value]) if value_is_list else '%s'
                path_filter += f" AND t.{field} IN ({placeholder})"
                params.extend(value)
            else:
                comparison_op = filter_params.get_comparison_op(f, 'raw')
                path_filter += f" AND t.{field} {comparison_op} %s"
                params.append(value)

        return path_filter, params

    def get(self, request, commit_hash: str | None):
        origin_param = request.GET.get("origin")
        git_url_param = request.GET.get("git_url")
        git_branch_param = request.GET.get("git_branch")
        path_param = request.GET.get('path')
        path_filter = ''
        params = [commit_hash, origin_param, git_url_param, git_branch_param]

        try:
            filter_params = FilterParams(request)
        except InvalidComparisonOP as e:
            return HttpResponseBadRequest(getErrorResponseBody(str(e)))

        print("####", params, path_filter)
        path_filter, params = self.__paramsFromBootAndFilters(
            commit_hash, path_param, filter_params, params)
        print("@@@@", params, path_filter)

        names_map = {
            "c.id": "id",
            "c.git_repository_url": "git_repository_url",
            "c.git_commit_hash": "git_commit_hash",
            "t.build_id": "build_id",
            "t.start_time": "start_time",
            "t.status": "status",
            "t.path": "path",
            "b.architecture": "architecture",
            "b.config_name": "config_name",
            "b.compiler": "compiler",
            "t.environment_misc": "environment_misc",
            "t.environment_comment": "environment_comment",
            "t.misc": "misc",
        }

        # TODO - Remove the f string here and use parametrized queries
        query = Checkouts.objects.raw(
            f"""
                SELECT c.id, c.git_repository_url,
                c.git_commit_hash, t.build_id, t.start_time,
                t.status as status, t.path, b.architecture, b.config_name,
                b.compiler, t.environment_misc, t.environment_comment, t.misc
                FROM checkouts AS c
                INNER JOIN builds AS b ON c.id = b.checkout_id
                INNER JOIN tests AS t ON t.build_id = b.id
                WHERE c.git_commit_hash = %s AND c.origin = %s AND c.git_repository_url = %s AND
                    c.git_repository_branch = %s {path_filter}
                ORDER BY
                build_id,
                CASE t.status
                    WHEN 'FAIL' THEN 1
                    WHEN 'ERROR' THEN 2
                    WHEN 'MISS' THEN 3
                    WHEN 'PASS' THEN 4
                ELSE 4
                END,
                t.id;
            """,
            params,
            translations=names_map,
        )

        statusCounts = defaultdict(int)
        errorCounts = defaultdict(int)
        configStatusCounts = defaultdict(lambda: defaultdict(int))
        architectureStatusCounts = defaultdict(lambda: defaultdict(int))
        testHistory = []
        platformsWithError = set()
        compilersPerArchitecture = defaultdict(set)
        errorMessageCounts = defaultdict(int)
        for record in query:
            statusCounts[record.status] += 1
            configStatusCounts[record.config_name][record.status] += 1
            architectureStatusCounts[record.architecture][record.status] += 1
            testHistory.append(
                {"start_time": record.start_time, "status": record.status}
            )
            if (
                record.status == "MISS"
                or record.status == "ERROR"
                or record.status == "FAIL"
            ):
                errorCounts[record.status] += 1
                compilersPerArchitecture[record.architecture].add(
                    record.compiler)
                platformsWithError.add(
                    extract_platform(record.environment_misc))
                currentErrorMessage = extract_error_message(record.misc)
                errorMessageCounts[currentErrorMessage] += 1
                errorMessageCounts[currentErrorMessage] += 1
        for architecture in compilersPerArchitecture:
            compilersPerArchitecture[architecture] = list(
                compilersPerArchitecture[architecture]
            )

        # TODO Validate output
        return JsonResponse(
            {
                "statusCounts": statusCounts,
                "errorCounts": errorCounts,
                "configStatusCounts": configStatusCounts,
                "testHistory": testHistory,
                "architectureStatusCounts": architectureStatusCounts,
                "compilersPerArchitecture": compilersPerArchitecture,
                "platformsWithError": list(platformsWithError),
                "errorMessageCounts": errorMessageCounts,
            }
        )
