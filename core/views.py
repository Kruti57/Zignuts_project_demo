from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from meetings.models import Meeting
from actions.models import ActionItem


@login_required
def dashboard_view(request):
    user = request.user
    today = timezone.localdate()

    user_meetings = Meeting.objects.filter(user=user)
    user_actions = ActionItem.objects.filter(user=user).select_related('meeting')

    # Metrics
    total_meetings = user_meetings.count()
    total_actions = user_actions.count()
    open_actions = user_actions.filter(status='OPEN').count()
    in_progress_actions = user_actions.filter(status='IN_PROGRESS').count()
    blocked_actions = user_actions.filter(status='BLOCKED').count()
    completed_actions = user_actions.filter(status='COMPLETED').count()
    overdue_actions = user_actions.filter(due_date__lt=today).exclude(status='COMPLETED').count()

    completion_rate = 0
    if total_actions > 0:
        completion_rate = round((completed_actions / total_actions) * 100)

    # Recent items
    recent_meetings = user_meetings.order_by('-date', '-created_at')[:5]
    urgent_actions = user_actions.filter(
        status__in=['OPEN', 'IN_PROGRESS', 'BLOCKED']
    ).order_by('due_date', '-priority')[:6]

    # Meeting types summary
    meeting_types = {}
    for code, label in Meeting.MEETING_TYPES:
        count = user_meetings.filter(meeting_type=code).count()
        if count > 0:
            meeting_types[label] = count

    context = {
        'total_meetings': total_meetings,
        'total_actions': total_actions,
        'open_actions': open_actions,
        'in_progress_actions': in_progress_actions,
        'blocked_actions': blocked_actions,
        'completed_actions': completed_actions,
        'overdue_actions': overdue_actions,
        'completion_rate': completion_rate,
        'recent_meetings': recent_meetings,
        'urgent_actions': urgent_actions,
        'meeting_types': meeting_types,
        'today': today,
    }
    return render(request, 'dashboard.html', context)


def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)
