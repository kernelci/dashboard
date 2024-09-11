from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View
from querybuilder.query import Query
from kernelCI_app.models import Builds
from kernelCI_app.utils import FilterParams, InvalidComparisonOP, getErrorResponseBody


class TreeDetails(View):

    def create_default_status(self):
        return {"valid": 0, "invalid": 0, "null": 0}

    def create_summary(self, builds_dict):
        status_map = {True: "valid", False: "invalid", None: "null"}

        build_summ = self.create_default_status()
        config_summ = {}
        arch_summ = {}

        for build in builds_dict:
            status_key = status_map[build["valid"]]
            build_summ[status_key] += 1

            if config := build["config_name"]:
                status = config_summ.get(config)
                if not status:
                    status = self.create_default_status()
                    config_summ[config] = status
                status[status_key] += 1

            if arch := build["architecture"]:
                status = arch_summ.setdefault(arch, self.create_default_status())
                status[status_key] += 1
                compiler = build["compiler"]
                if compiler and compiler not in status.setdefault("compilers", []):
                    status["compilers"].append(compiler)

        return {
            "builds": build_summ,
            "configs": config_summ,
            "architectures": arch_summ,
        }

    def get(self, request, commit_hash):
        build_fields = [
            "id",
            "architecture",
            "config_name",
            "misc",
            "config_url",
            "compiler",
            "valid",
            "duration",
            "log_url",
            "start_time",
        ]
        checkout_fields = [
            "git_repository_branch",
            "git_repository_url",
            "git_repository_branch",
        ]

        query = (
            Query()
            .from_table(Builds, build_fields)
            .join(
                "checkouts",
                condition="checkouts.id = builds.checkout_id",
                fields=checkout_fields,
            )
            .where(git_commit_hash__eq=commit_hash)
        )

        try:
            filter_params = FilterParams(request)
        except InvalidComparisonOP as e:
            return HttpResponseBadRequest(getErrorResponseBody(str(e)))

        for f in filter_params.filters:
            field = f["field"]
            table = None
            if field in build_fields:
                table = "builds"
            elif field in checkout_fields:
                table = "checkouts"
            if table:
                op = filter_params.get_comparison_op(f, "orm")
                query.where(**{f"{table}.{field}__{op}": f["value"]})

        records = query.select()

        summary = self.create_summary(records)

        return JsonResponse({"builds": records, "summary": summary}, safe=False)
