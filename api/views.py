from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from meetings.models import Meeting, MeetingInsight
from actions.models import ActionItem
from .serializers import (
    MeetingSerializer,
    MeetingDetailSerializer,
    MeetingInsightSerializer,
    ActionItemSerializer
)
from ai_service.client import AIServiceClient


class MeetingListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Meeting.objects.filter(user=self.request.user)
        query = self.request.query_params.get('q', '').strip()
        m_type = self.request.query_params.get('type', '').strip()

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(participants__icontains=query) |
                Q(transcript__icontains=query)
            )
        if m_type:
            queryset = queryset.filter(meeting_type=m_type)

        return queryset.order_by('-date', '-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MeetingRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MeetingDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Meeting.objects.filter(user=self.request.user)


class ActionItemListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ActionItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = ActionItem.objects.filter(user=self.request.user).select_related('meeting')
        query = self.request.query_params.get('q', '').strip()
        status_filter = self.request.query_params.get('status', '').strip()
        priority_filter = self.request.query_params.get('priority', '').strip()
        owner_filter = self.request.query_params.get('owner', '').strip()
        due_date_filter = self.request.query_params.get('due_date', '').strip()
        overdue = self.request.query_params.get('overdue', '').strip().lower() in ('true', '1', 'yes')
        meeting_id = self.request.query_params.get('meeting_id', '').strip()

        if query:
            queryset = queryset.filter(
                Q(task__icontains=query) |
                Q(owner__icontains=query) |
                Q(meeting__title__icontains=query)
            )
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        if owner_filter:
            queryset = queryset.filter(owner=owner_filter)
        if due_date_filter:
            queryset = queryset.filter(due_date=due_date_filter)
        if meeting_id:
            queryset = queryset.filter(meeting_id=meeting_id)
        if overdue:
            queryset = queryset.filter(
                due_date__lt=timezone.localdate()
            ).exclude(status='COMPLETED')

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ActionItemRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ActionItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ActionItem.objects.filter(user=self.request.user)


class ActionItemStatusUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        action = get_object_or_404(ActionItem, pk=pk, user=request.user)
        new_status = request.data.get('status')
        valid_statuses = dict(ActionItem.STATUS_CHOICES).keys()
        if new_status in valid_statuses:
            action.status = new_status
            action.save()
            serializer = ActionItemSerializer(action)
            return Response(serializer.data)
        return Response({'error': 'Invalid status choice'}, status=status.HTTP_400_BAD_REQUEST)


class GenerateAIInsightsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        meeting_id = request.data.get('meeting_id')
        if not meeting_id:
            return Response({'error': 'meeting_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        meeting = get_object_or_404(Meeting, pk=meeting_id, user=request.user)

        ai_client = AIServiceClient()
        insights_data, provider = ai_client.generate_insights(
            title=meeting.title,
            transcript=meeting.transcript,
            participants=meeting.participants,
            meeting_type=meeting.get_meeting_type_display(),
            date=str(meeting.date)
        )

        # Save or update MeetingInsight in database
        insight_obj, _ = MeetingInsight.objects.update_or_create(
            meeting=meeting,
            defaults={
                'summary': insights_data.get('summary', ''),
                'discussion_points': insights_data.get('discussion_points', []),
                'key_decisions': insights_data.get('key_decisions', []),
                'risks_and_concerns': insights_data.get('risks_and_concerns', []),
                'unanswered_questions': insights_data.get('unanswered_questions', []),
                'raw_ai_response': insights_data,
                'ai_provider': provider,
            }
        )

        return Response({
            'success': True,
            'meeting_id': meeting.id,
            'insights': insights_data,
            'provider': provider,
            'updated_at': insight_obj.updated_at.isoformat()
        }, status=status.HTTP_200_OK)


class ExtractActionItemsAPIView(APIView):
    """Bulk create ActionItem models from AI extracted action items"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        meeting_id = request.data.get('meeting_id')
        action_items_data = request.data.get('action_items', [])

        meeting = None
        if meeting_id:
            meeting = get_object_or_404(Meeting, pk=meeting_id, user=request.user)

        if not isinstance(action_items_data, list) or not action_items_data:
            return Response({'error': 'action_items must be a non-empty list'}, status=status.HTTP_400_BAD_REQUEST)

        created_items = []
        for item in action_items_data:
            task = item.get('task', '').strip()
            if not task:
                continue

            owner = item.get('owner', 'Unassigned').strip() or 'Unassigned'
            due_date_str = item.get('due_date', '').strip()
            
            due_date = None
            if due_date_str and due_date_str.lower() not in ('not specified', 'unassigned', 'none', 'null', ''):
                for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%d-%m-%Y', '%B %d, %Y', '%b %d, %Y'):
                    try:
                        due_date = timezone.datetime.strptime(due_date_str, fmt).date()
                        break
                    except ValueError:
                        pass

            priority = item.get('priority', 'MEDIUM').upper().strip()
            if priority not in ('LOW', 'MEDIUM', 'HIGH'):
                priority = 'MEDIUM'

            action_obj = ActionItem.objects.create(
                user=request.user,
                meeting=meeting,
                task=task,
                owner=owner,
                due_date=due_date,
                priority=priority,
                status='OPEN'
            )
            created_items.append(action_obj)

        serializer = ActionItemSerializer(created_items, many=True)
        return Response({
            'success': True,
            'count': len(created_items),
            'action_items': serializer.data
        }, status=status.HTTP_201_CREATED)


class DashboardStatsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.localdate()

        user_actions = ActionItem.objects.filter(user=user)
        total_actions = user_actions.count()
        open_actions = user_actions.filter(status='OPEN').count()
        in_progress = user_actions.filter(status='IN_PROGRESS').count()
        blocked = user_actions.filter(status='BLOCKED').count()
        completed_actions = user_actions.filter(status='COMPLETED').count()
        overdue_actions = user_actions.filter(due_date__lt=today).exclude(status='COMPLETED').count()

        total_meetings = Meeting.objects.filter(user=user).count()

        completion_rate = 0
        if total_actions > 0:
            completion_rate = round((completed_actions / total_actions) * 100, 1)

        return Response({
            'total_meetings': total_meetings,
            'total_actions': total_actions,
            'open_actions': open_actions,
            'in_progress_actions': in_progress,
            'blocked_actions': blocked,
            'completed_actions': completed_actions,
            'overdue_actions': overdue_actions,
            'completion_rate': completion_rate
        })
