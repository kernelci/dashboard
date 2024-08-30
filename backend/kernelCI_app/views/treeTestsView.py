from collections import defaultdict
from typing_extensions import Union
from django.http import HttpResponseBadRequest, JsonResponse
from django.views import View
from kernelCI_app.utils import FilterParams, InvalidComparisonOP, getErrorResponseBody
from kernelCI_app.models import Checkouts
import json


class TreeTestsView(View):
    # TODO misc_environment is not stable and should be used as a POC only
    # use the standardized field when that gets available
    def extract_platform(self, misc_environment: Union[str, dict, None]):
        parsedEnvMisc = None
        if isinstance(misc_environment, dict):
            parsedEnvMisc = misc_environment
        elif misc_environment is None:
            return "unknown"
        else:
            parsedEnvMisc = json.loads(misc_environment)
        platform = parsedEnvMisc.get("platform")
        if platform:
            return platform
        print("unknown platform in misc_environment", misc_environment)
        return "unknown"

    # TODO misc is not stable and should be used as a POC only
    def extract_error_message(self, misc: Union[str, dict, None]):
        parsedEnv = None
        if misc is None:
            return "unknown error"
        elif isinstance(misc, dict):
            parsedEnv = misc
        else:
            parsedEnv = json.loads(misc)
        error_message = parsedEnv.get("error_msg")
        if error_message:
            return error_message
        print("unknown error_msg in misc", misc)
        return "unknown error"

    def __paramsFromBootAndFilters(self, commit_hash, path_param, filter_params, params):
        if path_param:
            # TODO: 'boot' and 'boot.', right now is only using 'boot.'
            path_filter = "AND t.path LIKE %s"
            params.append(f'{path_param}%')
            target_field = 'bootStatus'
        else:
            path_filter = ""
            target_field = 'testStatus'

        for f in filter_params.filters:
            if f['field'] != target_field:
                continue
            value = f['value']
            value_list = value if isinstance(value, list) else [value]
            placeholders = ",".join(['%s' for i in value_list])
            path_filter += "AND t.status IN (" + placeholders + ")"
            for value in value_list:
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
        testHistory = []
        errorCountPerArchitecture = defaultdict(int)
        platformsWithError = set()
        compilersPerArchitecture = defaultdict(set)
        errorMessageCounts = defaultdict(int)
        for record in query:
            statusCounts[record.status] += 1
            configStatusCounts[record.config_name][record.status] += 1
            testHistory.append(
                {"start_time": record.start_time, "status": record.status}
            )
            if (
                record.status == "MISS"
                or record.status == "ERROR"
                or record.status == "FAIL"
            ):
                errorCounts[record.status] += 1
                errorCountPerArchitecture[record.architecture] += 1
                compilersPerArchitecture[record.architecture].add(
                    record.compiler)
                platformsWithError.add(
                    self.extract_platform(record.environment_misc))
                currentErrorMessage = self.extract_error_message(record.misc)
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
                "errorCountPerArchitecture": errorCountPerArchitecture,
                "compilersPerArchitecture": compilersPerArchitecture,
                "platformsWithError": list(platformsWithError),
                "errorMessageCounts": errorMessageCounts,
            }
        )
