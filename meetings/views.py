from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Meeting
from .forms import MeetingForm


@login_required
def meeting_list_view(request):
    query = request.GET.get('q', '').strip()
    m_type = request.GET.get('type', '').strip()
    date_filter = request.GET.get('date', '').strip()

    meetings = Meeting.objects.filter(user=request.user)

    if query:
        meetings = meetings.filter(
            Q(title__icontains=query) |
            Q(participants__icontains=query) |
            Q(transcript__icontains=query)
        )

    if m_type:
        meetings = meetings.filter(meeting_type=m_type)

    if date_filter:
        meetings = meetings.filter(date=date_filter)

    meetings = meetings.order_by('-date', '-created_at')

    # Counts
    total_meetings = request.user.meetings.count()
    total_actions = request.user.action_items.count()

    context = {
        'meetings': meetings,
        'query': query,
        'selected_type': m_type,
        'date_filter': date_filter,
        'meeting_types': Meeting.MEETING_TYPES,
        'total_meetings': total_meetings,
        'total_actions': total_actions,
    }
    return render(request, 'meetings/meeting_list.html', context)


@login_required
def meeting_create_view(request):
    if request.method == 'POST':
        form = MeetingForm(request.POST, request.FILES)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.user = request.user
            
            # If TXT file uploaded and transcript is empty, read TXT file content
            txt_file = form.cleaned_data.get('txt_file')
            if txt_file and not meeting.transcript:
                try:
                    meeting.transcript = txt_file.read().decode('utf-8', errors='replace')
                except Exception:
                    pass
            
            meeting.save()
            messages.success(request, f"Meeting '{meeting.title}' created successfully! You can now generate AI Insights.")
            return redirect('meeting_detail', pk=meeting.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = MeetingForm()

    return render(request, 'meetings/meeting_form.html', {
        'form': form,
        'title': 'Create New Meeting',
        'is_edit': False
    })


@login_required
def meeting_detail_view(request, pk):
    meeting = Meeting.objects.filter(pk=pk, user=request.user).first()
    if not meeting:
        messages.warning(request, "The requested meeting was not found or was recently refreshed. Redirected to Meetings.")
        return redirect('meeting_list')

    insights = getattr(meeting, 'insights', None)
    action_items = meeting.action_items.all().order_by('-created_at')
    
    preloaded_actions = []
    if insights and isinstance(insights.raw_ai_response, dict):
        preloaded_actions = insights.raw_ai_response.get('action_items', [])

    return render(request, 'meetings/meeting_detail.html', {
        'meeting': meeting,
        'insights': insights,
        'action_items': action_items,
        'preloaded_actions': preloaded_actions,
    })


@login_required
def meeting_edit_view(request, pk):
    meeting = Meeting.objects.filter(pk=pk, user=request.user).first()
    if not meeting:
        messages.warning(request, "The requested meeting was not found. Redirected to Meetings.")
        return redirect('meeting_list')

    if request.method == 'POST':
        form = MeetingForm(request.POST, request.FILES, instance=meeting)
        if form.is_valid():
            updated_meeting = form.save(commit=False)
            txt_file = form.cleaned_data.get('txt_file')
            if txt_file:
                try:
                    updated_meeting.transcript = txt_file.read().decode('utf-8', errors='replace')
                except Exception:
                    pass
            updated_meeting.save()
            messages.success(request, f"Meeting '{meeting.title}' updated successfully!")
            return redirect('meeting_detail', pk=meeting.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = MeetingForm(instance=meeting)

    return render(request, 'meetings/meeting_form.html', {
        'form': form,
        'meeting': meeting,
        'title': f'Edit Meeting: {meeting.title}',
        'is_edit': True
    })


@login_required
@require_POST
def meeting_delete_view(request, pk):
    meeting = Meeting.objects.filter(pk=pk, user=request.user).first()
    if not meeting:
        messages.warning(request, "The meeting was already deleted or not found.")
        return redirect('meeting_list')
    title = meeting.title
    meeting.delete()
    messages.success(request, f"Meeting '{title}' and all associated insights were deleted.")
    return redirect('meeting_list')


@login_required
@require_POST
def meeting_upload_txt(request):
    """Endpoint for asynchronous TXT file upload in frontend"""
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)
    
    file = request.FILES['file']
    if not file.name.lower().endswith('.txt'):
        return JsonResponse({'error': 'Only .txt files are allowed'}, status=400)

    try:
        content = file.read().decode('utf-8', errors='replace')
        return JsonResponse({'success': True, 'content': content, 'filename': file.name})
    except Exception as e:
        return JsonResponse({'error': f'Failed to read file: {str(e)}'}, status=500)
