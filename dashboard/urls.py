from django.urls import path
from . import views

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("upload-log/", views.LogFileUploadView.as_view(), name="upload_log"),
    path("list-logs/", views.LogFileListView.as_view(), name="list_logs"), # Added URL for listing logs
    path("process-netflow/", views.NetFlowProcessView.as_view(), name="process_netflow"),
    path("clear-elasticsearch/", views.ElasticsearchClearView.as_view(), name="clear_elasticsearch"),
    path("update-sof-elk/", views.SOFELKUpdateView.as_view(), name="update_sof_elk"),
    path("system-status/", views.SystemStatusView.as_view(), name="system_status"),
    path("api/system-status/", views.APISystemStatusView.as_view(), name="api_system_status"),
]
