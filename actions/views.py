import csv
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import ActionItem
from .forms import ActionItemForm
from meetings.models import Meeting


@login_required
def action_tracker_view(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    priority_filter = request.GET.get('priority', '').strip()
    owner_filter = request.GET.get('owner', '').strip()
    due_date_filter = request.GET.get('due_date', '').strip()
    overdue_only = request.GET.get('overdue', '').strip().lower() in ('true', '1', 'yes')
    meeting_filter = request.GET.get('meeting_id', '').strip()

    actions = ActionItem.objects.filter(user=request.user).select_related('meeting')

    # Apply search filter
    if query:
        actions = actions.filter(
            Q(task__icontains=query) |
            Q(owner__icontains=query) |
            Q(meeting__title__icontains=query)
        )

    # Apply category filters
    if status_filter:
        actions = actions.filter(status=status_filter)

    if priority_filter:
        actions = actions.filter(priority=priority_filter)

    if owner_filter:
        actions = actions.filter(owner=owner_filter)

    if due_date_filter:
        actions = actions.filter(due_date=due_date_filter)

    if meeting_filter:
        actions = actions.filter(meeting_id=meeting_filter)

    if overdue_only:
        actions = actions.filter(
            due_date__lt=timezone.localdate()
        ).exclude(status='COMPLETED')

    # Distinct owners for filter dropdown
    all_user_actions = ActionItem.objects.filter(user=request.user)
    distinct_owners = all_user_actions.values_list('owner', flat=True).distinct().order_by('owner')
    user_meetings = Meeting.objects.filter(user=request.user).order_by('-date')

    # Comprehensive Statistics
    today = timezone.localdate()
    stats = {
        'total': all_user_actions.count(),
        'open': all_user_actions.filter(status='OPEN').count(),
        'in_progress': all_user_actions.filter(status='IN_PROGRESS').count(),
        'blocked': all_user_actions.filter(status='BLOCKED').count(),
        'completed': all_user_actions.filter(status='COMPLETED').count(),
        'overdue': all_user_actions.filter(due_date__lt=today).exclude(status='COMPLETED').count(),
    }

    form = ActionItemForm(user=request.user)

    context = {
        'actions': actions,
        'query': query,
        'selected_status': status_filter,
        'selected_priority': priority_filter,
        'selected_owner': owner_filter,
        'selected_due_date': due_date_filter,
        'overdue_only': overdue_only,
        'selected_meeting': meeting_filter,
        'distinct_owners': distinct_owners,
        'user_meetings': user_meetings,
        'status_choices': ActionItem.STATUS_CHOICES,
        'priority_choices': ActionItem.PRIORITY_CHOICES,
        'stats': stats,
        'form': form,
    }
    return render(request, 'actions/action_tracker.html', context)


@login_required
def action_create_view(request):
    if request.method == 'POST':
        form = ActionItemForm(request.POST, user=request.user)
        if form.is_valid():
            action = form.save(commit=False)
            action.user = request.user
            action.save()
            messages.success(request, f"Action item created: {action.task[:30]}...")
            next_url = request.POST.get('next') or request.GET.get('next') or 'action_tracker'
            return redirect(next_url)
        else:
            messages.error(request, "Failed to create action item. Please check inputs.")
    return redirect('action_tracker')


@login_required
def action_edit_view(request, pk):
    action = get_object_or_404(ActionItem, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ActionItemForm(request.POST, instance=action, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Action item updated successfully!")
            next_url = request.POST.get('next') or request.GET.get('next') or 'action_tracker'
            return redirect(next_url)
        else:
            messages.error(request, "Failed to update action item.")
    else:
        form = ActionItemForm(instance=action, user=request.user)

    return render(request, 'actions/action_form.html', {
        'form': form,
        'action': action,
        'title': 'Edit Action Item'
    })


@login_required
@require_POST
def action_delete_view(request, pk):
    action = get_object_or_404(ActionItem, pk=pk, user=request.user)
    task_desc = action.task[:30]
    action.delete()
    messages.success(request, f"Action item '{task_desc}...' deleted.")
    next_url = request.POST.get('next') or request.GET.get('next') or 'action_tracker'
    return redirect(next_url)


@login_required
@require_POST
def action_update_status_api(request, pk):
    """Inline AJAX status update endpoint"""
    action = get_object_or_404(ActionItem, pk=pk, user=request.user)
    new_status = request.POST.get('status')
    
    valid_statuses = dict(ActionItem.STATUS_CHOICES).keys()
    if new_status in valid_statuses:
        action.status = new_status
        action.save()
        return JsonResponse({
            'success': True,
            'id': action.id,
            'status': action.status,
            'status_display': action.get_status_display(),
            'badge_class': action.status_badge_class,
            'is_overdue': action.is_overdue
        })
    return JsonResponse({'error': 'Invalid status choice'}, status=400)


@login_required
def action_export_csv(request):
    """Export action items to CSV"""
    response = HttpResponse(content_type='text/csv')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="action_items_{timestamp}.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Task', 'Meeting', 'Owner', 'Due Date', 'Priority', 'Status', 'Is Overdue', 'Created At'])

    actions = ActionItem.objects.filter(user=request.user).select_related('meeting').order_by('-created_at')
    for a in actions:
        meeting_title = a.meeting.title if a.meeting else 'Standalone'
        writer.writerow([
            a.id,
            a.task,
            meeting_title,
            a.owner,
            a.due_date or 'Not specified',
            a.priority,
            a.status,
            'Yes' if a.is_overdue else 'No',
            a.created_at.strftime('%Y-%m-%d %H:%M')
        ])

    return response
