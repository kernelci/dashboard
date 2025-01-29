from typing import Dict
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
    boot_status = serializers.SerializerMethodField(method_name="get_boot_status")
    git_commit_hash = serializers.CharField()
    git_commit_name = serializers.CharField()
    git_commit_tags = serializers.ListField()
    patchset_hash = serializers.CharField()
    tree_names = serializers.ListField()
    git_repository_branch = serializers.CharField()
    git_repository_url = serializers.CharField()
    start_time = serializers.DateTimeField()

    class Meta():
        fields = ['build_status', 'test_status', 'git_commit_hash', 'patchset_hash']

    def get_repository_url(self, obj) -> str:
        return obj.id

    def get_build_status(self, obj) -> Dict:
        return {
            "valid": obj.valid_builds,
            "invalid": obj.invalid_builds,
            "null": obj.null_builds,
        }

    def get_test_status(self, obj) -> Dict:
        return {
            "fail": obj.fail_tests,
            "error": obj.error_tests,
            "miss": obj.miss_tests,
            "pass": obj.pass_tests,
            "done": obj.done_tests,
            "skip": obj.skip_tests,
            "null": obj.null_tests,
        }

    def get_boot_status(self, obj) -> Dict:
        return {
            "fail": obj.fail_boots,
            "error": obj.error_boots,
            "miss": obj.miss_boots,
            "pass": obj.pass_boots,
            "done": obj.done_boots,
            "skip": obj.skip_boots,
            "null": obj.null_boots,
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


class GroupedTestsSerializer(serializers.Serializer):
    path_group = serializers.CharField()
    fail_tests = serializers.IntegerField()
    error_tests = serializers.IntegerField()
    miss_tests = serializers.IntegerField()
    pass_tests = serializers.IntegerField()
    done_tests = serializers.IntegerField()
    skip_tests = serializers.IntegerField()
    null_tests = serializers.IntegerField()
    total_tests = serializers.IntegerField()
    individual_tests = serializers.ListField()
