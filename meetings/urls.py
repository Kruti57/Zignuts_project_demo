from django.urls import path
from . import views

urlpatterns = [
    path('', views.meeting_list_view, name='meeting_list'),
    path('create/', views.meeting_create_view, name='meeting_create'),
    path('<int:pk>/', views.meeting_detail_view, name='meeting_detail'),
    path('<int:pk>/edit/', views.meeting_edit_view, name='meeting_edit'),
    path('<int:pk>/delete/', views.meeting_delete_view, name='meeting_delete'),
    path('upload-txt/', views.meeting_upload_txt, name='meeting_upload_txt'),
]
