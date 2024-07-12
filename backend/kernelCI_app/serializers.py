from rest_framework import serializers
from kernelCI_app.models import Checkouts
from kernelCI_app.utils import get_visible_record_config


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
    tree_name = serializers.SerializerMethodField(method_name="get_tree_name")
    git_commit_name = serializers.SerializerMethodField(method_name="get_git_commit_name")
    git_repository_branch = serializers.SerializerMethodField(method_name="get_git_repository_branch")
    git_commit_hash = serializers.SerializerMethodField(method_name="get_git_commit_hash")

    class Meta():
        fields = [
            'tree_name', 'git_commit_name', 'git_repository_branch',
            'build_status', 'test_status', 'git_commit_hash'
        ]

    def get_config(self, obj):
        return get_visible_record_config('checkouts', obj.id)

    def get_field_from_config(self, obj, field):
        config = self.get_config(obj)
        return config.get(field)

    def get_tree_name(self, obj):
        return self.get_field_from_config(obj, 'tree_name')

    def get_git_commit_name(self, obj):
        return self.get_field_from_config(obj, 'git_commit_name')

    def get_git_repository_branch(self, obj):
        return self.get_field_from_config(obj, 'git_repository_branch')

    def get_git_commit_hash(self, obj):
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
    start_time = serializers.CharField()
    duration = serializers.CharField()
    compiler = serializers.CharField()
    config_url = serializers.CharField()
    log_url = serializers.CharField()
    test_status = serializers.DictField()
    misc = serializers.JSONField()
