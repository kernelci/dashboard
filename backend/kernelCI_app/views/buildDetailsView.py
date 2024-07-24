from django.http import JsonResponse, HttpResponseNotFound
from django.views import View
from querybuilder.query import Query
from kernelCI_app.models import Builds


class BuildDetails(View):

    def get(self, request, build_id):
        build_fields = [
            "id", "_timestamp", "checkout_id", "origin",
            "comment", "start_time", "duration", "architecture",
            "command", "compiler", "config_name", "config_url",
            "log_url", "valid", "misc"]

        query = Query().from_table(Builds, build_fields)
        query.join(
            'checkouts',
            fields=[
                'git_repository_branch', 'git_commit_name', 'git_repository_url', 'git_commit_hash'
            ],
            condition='checkouts.id = builds.checkout_id',
        )
        query.where(**{'builds.id__eq': build_id})

        records = query.select()
        if not records:
            return HttpResponseNotFound('{}')
        return JsonResponse(records[0])
