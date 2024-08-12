from django.urls import path
from kernelCI_app import views


urlpatterns = [
    path('tree/', views.TreeView.as_view(), name='tree'),
    path('tree/<str:commit_hash>', views.TreeDetails.as_view(), name='treeDetails'),
    path('build/<str:build_id>', views.BuildDetails.as_view(), name='buildDetails'),
    path('build/<str:build_id>/tests', views.BuildTests.as_view(), name='buildTests'),
    path('tree/<str:commit_hash>/tests/', views.TreeTestsView.as_view(), name='treeTests'),
    path('revision/tests/', views.revisionTests.as_view(), name='revisionTests'),
]
