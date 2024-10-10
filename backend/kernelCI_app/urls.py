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
    path("tree/tests/",
         viewCache(views.groupedTests),
         name="treeGroupedTests"
         ),
    path("tree/<str:commit_hash>",
         viewCache(views.TreeDetails),
         name="treeDetails"
         ),
    path("tree/<str:commit_hash>/full",
         viewCache(views.TreeDetailsSlow),
         name="TreeDetailsSlow"
         ),
    path("tree/<str:commit_hash>/commits",
         viewCache(views.TreeCommitsHistory),
         name="treeCommits"
         ),
    path("tree/<str:commit_hash>/tests/",
         viewCache(views.TreeTestsView),
         name="treeTests"
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
         )
]
