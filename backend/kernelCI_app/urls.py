from django.urls import path
from django.views.decorators.cache import cache_page
from django.conf import settings
from kernelCI_app import views

timeout = settings.CACHE_TIMEOUT
cache = cache_page(timeout)


def viewCache(view):
    return cache(view.as_view())


urlpatterns = [
    path("tests/<str:commit_hash>",
         viewCache(views.TestsByTreeAndCommitHash),
         name="testsByTreeAndCommitHash"
         ),
    path("tests/test/<str:test_id>",
         viewCache(views.TestDetails),
         name="testDetails"
         ),
    path("tree/",
         viewCache(views.TreeView),
         name="tree"
         ),
    path("tree-fast/",
         viewCache(views.TreeViewFast),
         name="tree-fast"
         ),
    path("tree/<str:commit_hash>/full",
         views.TreeDetails.as_view(),
         name="treeDetailsView"
         ),
    path("tree/<str:commit_hash>/commits",
         viewCache(views.TreeCommitsHistory),
         name="treeCommits"
         ),
    path("tree/<str:tree_name>/<str:branch>",
         viewCache(views.TreeLatest),
         name="treeLatest"
         ),
    path("build/<str:build_id>",
         viewCache(views.BuildDetails),
         name="buildDetails"
         ),
    path("build/<str:build_id>/tests",
         viewCache(views.BuildTests),
         name="buildTests"
         ),
    path("build/<str:build_id>/status-count",
         viewCache(views.BuildStatusCountView),
         name="buildStatusCount"
         ),
    path("build/<str:build_id>/issues",
         viewCache(views.IssueView),
         name="issues",
         ),
    path("test/<str:test_id>/issues",
         viewCache(views.IssueView),
         name="issues",
         ),
    path("log-downloader/",
         viewCache(views.LogDownloaderView),
         name="logDownloader"
         ),
    path("hardware/<str:hardware_id>",
         viewCache(views.HardwareDetails),
         name="hardwareDetails"
         ),
    path("hardware/<str:hardware_id>/commit-history",
         viewCache(views.HardwareDetailsCommitHistoryView),
         name="hardwareDetailsCommitHistory"
         ),
    path("hardware/",
         viewCache(views.HardwareView),
         name="hardware"),
    path("issue/<str:issue_id>/version/<str:version>",
         viewCache(views.IssueDetails),
         name="issueDetails"),
    path("issue/<str:issue_id>/version/<str:version>/tests",
         viewCache(views.IssueDetailsTests),
         name="issueDetailsTests"),
    path("issue/<str:issue_id>/version/<str:version>/builds",
         viewCache(views.IssueDetailsBuilds),
         name="issueDetailsBuilds"),
]
