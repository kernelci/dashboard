from django.urls import path
from kernelCI_app import views


urlpatterns = [
    path('tree/', views.TreeView.as_view(), name='tree'),
    path('tree/<str:commit_hash>', views.TreeDetails.as_view(), name='treeDetails')
]
