from django.urls import path
from django.views.decorators.cache import cache_page
from django.conf import settings
from kernelCI_app import views
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

timeout = settings.CACHE_TIMEOUT
cache = cache_page(timeout)


def viewCache(view):
    return cache(view.as_view())


urlpatterns = [
    path("test/<str:test_id>",
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
    path("tree/<str:commit_hash>/summary",
         views.TreeDetailsSummary.as_view(),
         name="treeDetailsSummaryView"
         ),
    path("tree/<str:commit_hash>/builds",
         views.TreeDetailsBuilds.as_view(),
         name="treeDetailsBuildsView"
         ),
    path("tree/<str:commit_hash>/boots",
         views.TreeDetailsBoots.as_view(),
         name="treeDetailsBootsView"
         ),
    path("tree/<str:commit_hash>/tests",
         views.TreeDetailsTests.as_view(),
         name="treeDetailsTestsView"
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
    path("hardware/<str:hardware_id>/builds",
         viewCache(views.HardwareDetailsBuilds),
         name="hardwareDetailsBuilds"
         ),
    path("hardware/<str:hardware_id>/commit-history",
         viewCache(views.HardwareDetailsCommitHistoryView),
         name="hardwareDetailsCommitHistory"
         ),
    path("hardware/<str:hardware_id>/boots",
         views.HardwareDetailsBoots.as_view(),
         name="hardwareDetailsBoots"
         ),
    path("hardware/<str:hardware_id>/summary",
         views.HardwareDetailsSummary.as_view(),
         name="hardwareDetailsSummary"
         ),
    path("hardware/<str:hardware_id>/tests",
         views.HardwareDetailsTests.as_view(),
         name="hardwareDetailsTests"
         ),
    path("hardware/",
         viewCache(views.HardwareView),
         name="hardware"),
    path("issue/extras/",
         viewCache(views.IssueExtraDetails),
         name="issueExtraDetails"
         ),
    path("issue/<str:issue_id>",
         viewCache(views.IssueDetails),
         name="issueDetails"),
    path("issue/<str:issue_id>/tests",
         viewCache(views.IssueDetailsTests),
         name="issueDetailsTests"),
    path("issue/<str:issue_id>/builds",
         viewCache(views.IssueDetailsBuilds),
         name="issueDetailsBuilds"),
    # DRF Spectacular
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
