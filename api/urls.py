from django.urls import path
from . import views

urlpatterns = [
    # Meetings
    path('meetings/', views.MeetingListCreateAPIView.as_view(), name='api_meeting_list_create'),
    path('meetings/<int:pk>/', views.MeetingRetrieveUpdateDestroyAPIView.as_view(), name='api_meeting_detail'),

    # Actions
    path('actions/', views.ActionItemListCreateAPIView.as_view(), name='api_action_list_create'),
    path('actions/<int:pk>/', views.ActionItemRetrieveUpdateDestroyAPIView.as_view(), name='api_action_detail'),
    path('actions/<int:pk>/status/', views.ActionItemStatusUpdateAPIView.as_view(), name='api_action_status_update'),

    # AI Insights & Action Extraction
    path('ai/generate/', views.GenerateAIInsightsAPIView.as_view(), name='api_ai_generate'),
    path('ai/extract-actions/', views.ExtractActionItemsAPIView.as_view(), name='api_ai_extract_actions'),

    # Dashboard Stats
    path('dashboard/stats/', views.DashboardStatsAPIView.as_view(), name='api_dashboard_stats'),
]
