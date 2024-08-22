from django.urls import path
from kernelCI_app import views


urlpatterns = [
    path("tree/", views.TreeView.as_view(), name="tree"),
    path("tree/tests/", views.revisionTests.as_view(), name="treeRevisionTests"),
    path("tree/<str:commit_hash>", views.TreeDetails.as_view(), name="treeDetails"),
    path(
        "tree/<str:commit_hash>/tests/", views.TreeTestsView.as_view(), name="treeTests"
    ),
    path("build/<str:build_id>", views.BuildDetails.as_view(), name="buildDetails"),
    path("build/<str:build_id>/tests", views.BuildTests.as_view(), name="buildTests"),
    path("tests/test/<str:test_id>", views.TestDetails.as_view(), name="testDetails"),
    path("tests/<str:commit_hash>",
         views.TestsByTreeAndCommitHash.as_view(), name="testsByTreeAndCommitHash"),
]
