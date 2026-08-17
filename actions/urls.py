from django.urls import path
from . import views

urlpatterns = [
    path('', views.action_tracker_view, name='action_tracker'),
    path('create/', views.action_create_view, name='action_create'),
    path('<int:pk>/edit/', views.action_edit_view, name='action_edit'),
    path('<int:pk>/delete/', views.action_delete_view, name='action_delete'),
    path('<int:pk>/update-status/', views.action_update_status_api, name='action_update_status_api'),
    path('export/csv/', views.action_export_csv, name='action_export_csv'),
]
