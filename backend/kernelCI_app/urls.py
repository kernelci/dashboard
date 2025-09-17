from django.urls import path
from django.views.decorators.cache import cache_page
from django.conf import settings
from kernelCI_app import views
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

timeout = settings.CACHE_TIMEOUT
cache = cache_page(timeout)


def view_cache(view):
    return cache(view.as_view())


urlpatterns = [
    path(
        "test/status-history",
        view_cache(views.TestStatusHistory),
        name="testStatusHistory",
    ),
    path("test/<str:test_id>", view_cache(views.TestDetails), name="testDetails"),
    path("tree/", view_cache(views.TreeView), name="tree"),
    path("tree-fast/", view_cache(views.TreeViewFast), name="tree-fast"),
    path(
        "tree/<str:commit_hash>/full",
        views.TreeDetails.as_view(),
        name="treeDetailsView",
    ),
    path(
        "tree/<str:commit_hash>/summary",
        views.TreeDetailsSummary.as_view(),
        name="treeDetailsSummaryView",
    ),
    path(
        "tree/<str:commit_hash>/builds",
        views.TreeDetailsBuilds.as_view(),
        name="treeDetailsBuildsView",
    ),
    path(
        "tree/<str:commit_hash>/boots",
        views.TreeDetailsBoots.as_view(),
        name="treeDetailsBootsView",
    ),
    path(
        "tree/<str:commit_hash>/tests",
        views.TreeDetailsTests.as_view(),
        name="treeDetailsTestsView",
    ),
    path(
        "tree/<str:commit_hash>/commits",
        view_cache(views.TreeCommitsHistory),
        name="treeCommits",
    ),
    path(
        "tree/<str:tree_name>/<path:git_branch>/<str:commit_hash>/commits",
        view_cache(views.TreeCommitsHistoryDirect),
        name="treeCommitsDirectView",
    ),
    path(
        "tree/<str:tree_name>/<path:git_branch>/<str:commit_hash>/boots",
        views.TreeDetailsBootsDirect.as_view(),
        name="treeDetailsBootsDirectView",
    ),
    path(
        "tree/<str:tree_name>/<path:git_branch>/<str:commit_hash>/builds",
        views.TreeDetailsBuildsDirect.as_view(),
        name="treeDetailsBuildsDirectView",
    ),
    path(
        "tree/<str:tree_name>/<path:git_branch>/<str:commit_hash>/full",
        views.TreeDetailsDirect.as_view(),
        name="treeDetailsDirectView",
    ),
    path(
        "tree/<str:tree_name>/<path:git_branch>/<str:commit_hash>/summary",
        views.TreeDetailsSummaryDirect.as_view(),
        name="treeDetailsDirectSummaryView",
    ),
    path(
        "tree/<str:tree_name>/<path:git_branch>/<str:commit_hash>/tests",
        views.TreeDetailsTestsDirect.as_view(),
        name="treeDetailsTestsDirectView",
    ),
    path(
        "tree/<str:tree_name>/<path:git_branch>",
        view_cache(views.TreeLatest),
        name="treeLatest",
    ),
    path("build/<str:build_id>", view_cache(views.BuildDetails), name="buildDetails"),
    path("build/<str:build_id>/tests", view_cache(views.BuildTests), name="buildTests"),
    path(
        "build/<str:build_id>/issues",
        view_cache(views.BuildIssuesView),
        name="buildIssues",
    ),
    path(
        "test/<str:test_id>/issues",
        view_cache(views.TestIssuesView),
        name="testIssues",
    ),
    path("log-downloader/", view_cache(views.LogDownloaderView), name="logDownloader"),
    path(
        "hardware/<str:hardware_id>",
        view_cache(views.HardwareDetails),
        name="hardwareDetails",
    ),
    path(
        "hardware/<str:hardware_id>/builds",
        view_cache(views.HardwareDetailsBuilds),
        name="hardwareDetailsBuilds",
    ),
    path(
        "hardware/<str:hardware_id>/commit-history",
        view_cache(views.HardwareDetailsCommitHistoryView),
        name="hardwareDetailsCommitHistory",
    ),
    path(
        "hardware/<str:hardware_id>/boots",
        views.HardwareDetailsBoots.as_view(),
        name="hardwareDetailsBoots",
    ),
    path(
        "hardware/<str:hardware_id>/summary",
        views.HardwareDetailsSummary.as_view(),
        name="hardwareDetailsSummary",
    ),
    path(
        "hardware/<str:hardware_id>/tests",
        views.HardwareDetailsTests.as_view(),
        name="hardwareDetailsTests",
    ),
    path("hardware/", view_cache(views.HardwareView), name="hardware"),
    path("issue/", view_cache(views.IssueView), name="issue"),
    path(
        "issue/extras/", view_cache(views.IssueExtraDetails), name="issueExtraDetails"
    ),
    path("issue/<str:issue_id>", view_cache(views.IssueDetails), name="issueDetails"),
    path(
        "issue/<str:issue_id>/tests",
        view_cache(views.IssueDetailsTests),
        name="issueDetailsTests",
    ),
    path(
        "issue/<str:issue_id>/builds",
        view_cache(views.IssueDetailsBuilds),
        name="issueDetailsBuilds",
    ),
    # DRF Spectacular
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
    path("proxy/", views.ProxyView.as_view(), name="proxyView"),
    path("origins/", views.OriginsView.as_view(), name="originsView"),
    path("tree-report/", views.TreeReport.as_view(), name="treeReportView"),
]
