from rest_framework import serializers
from kernelCI_app.models import Checkouts


class CheckoutsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkouts
        fields = [
            'field_timestamp', 'id', 'origin', 'tree_name',
            'git_repository_url', 'git_commit_hash', 'git_commit_name',
            'git_repository_branch', 'patchset_files', 'patchset_hash',
            'message_id', 'comment', 'start_time', 'contacts',
            'log_url', 'log_excerpt', 'valid', 'misc'
        ]


class TreeSerializer(serializers.Serializer):
    build_status = serializers.SerializerMethodField(method_name="get_build_status")
    test_status = serializers.SerializerMethodField(method_name="get_test_status")
    git_commit_hash = serializers.CharField()
    patchset_hash = serializers.CharField()
    tree_names = serializers.ListField()
    git_repository_branch = serializers.CharField()
    git_repository_url = serializers.CharField()
    start_time = serializers.DateTimeField()

    class Meta():
        fields = ['build_status', 'test_status', 'git_commit_hash', 'patchset_hash']

    def get_repository_url(self, obj):
        return obj.id

    def get_build_status(self, obj):
        return {
            "valid": obj.valid_builds,
            "invalid": obj.invalid_builds,
            "null": obj.null_builds,
            "total": obj.total_builds
        }

    def get_test_status(self, obj):
        return {
            "fail": obj.fail_tests,
            "error": obj.error_tests,
            "miss": obj.miss_tests,
            "pass": obj.pass_tests,
            "done": obj.done_tests,
            "skip": obj.skip_tests,
            "null": obj.null_tests,
            "total": obj.total_tests
        }


class TreeDetailsSerializer(serializers.Serializer):
    id = serializers.CharField()
    architecture = serializers.CharField()
    config_name = serializers.CharField()
    valid = serializers.BooleanField()
    start_time = serializers.DateTimeField()
    duration = serializers.CharField()
    compiler = serializers.CharField()
    config_url = serializers.CharField()
    log_url = serializers.CharField()
    test_status = serializers.DictField()
    misc = serializers.JSONField()


class BuildTestsSerializer(serializers.Serializer):
    current_path = serializers.CharField()
    start_time = serializers.DateTimeField()
    fail_tests = serializers.IntegerField()
    error_tests = serializers.IntegerField()
    miss_tests = serializers.IntegerField()
    pass_tests = serializers.IntegerField()
    done_tests = serializers.IntegerField()
    skip_tests = serializers.IntegerField()
    null_tests = serializers.IntegerField()
    total_tests = serializers.IntegerField()
    origins = serializers.ListField()
