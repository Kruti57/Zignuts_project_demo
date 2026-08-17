from django import forms
from django.utils import timezone
from .models import ActionItem
from meetings.models import Meeting


class ActionItemForm(forms.ModelForm):
    meeting_custom = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Select from dropdown or type meeting name...',
            'id': 'action-meeting-custom',
            'list': 'meeting-list-options',
            'autocomplete': 'off'
        })
    )

    class Meta:
        model = ActionItem
        fields = ['task', 'meeting', 'owner', 'due_date', 'priority', 'status']
        widgets = {
            'task': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the specific action item...',
                'rows': 3,
                'id': 'action-task',
                'required': True
            }),
            'meeting': forms.Select(attrs={
                'class': 'form-select d-none',
                'id': 'action-meeting'
            }),
            'owner': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Select or type assignee name...',
                'id': 'action-owner',
                'list': 'owner-list-options',
                'autocomplete': 'off'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'action-due-date'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select',
                'id': 'action-priority'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
                'id': 'action-status'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        self.user = user
        super().__init__(*args, **kwargs)

        if user:
            self.fields['meeting'].queryset = Meeting.objects.filter(user=user)
            self.user_meetings = Meeting.objects.filter(user=user).order_by('-date', '-created_at')

            # Pre-fill meeting_custom if instance has a meeting
            if self.instance and self.instance.pk and self.instance.meeting:
                self.initial['meeting_custom'] = self.instance.meeting.title

            # Extract all distinct assignees/employees
            assignees = set()
            assignees.add('Unassigned')
            for owner in ActionItem.objects.filter(user=user).values_list('owner', flat=True).distinct():
                if owner and owner.strip():
                    assignees.add(owner.strip())
            for parts in Meeting.objects.filter(user=user).values_list('participants', flat=True):
                if parts:
                    for p in parts.split(','):
                        if p.strip():
                            assignees.add(p.strip())

            self.assignee_list = sorted(list(assignees), key=lambda x: (x == 'Unassigned', x.lower()))
        else:
            self.user_meetings = Meeting.objects.none()
            self.assignee_list = ['Unassigned']

        self.fields['meeting'].empty_label = "None (Standalone Action)"

    def clean(self):
        cleaned_data = super().clean()
        meeting_custom = cleaned_data.get('meeting_custom')
        selected_meeting = cleaned_data.get('meeting')

        if meeting_custom and meeting_custom.strip():
            custom_title = meeting_custom.strip()
            if custom_title.lower() in ('none', 'none (standalone action)', 'standalone', 'null', ''):
                cleaned_data['meeting'] = None
            elif self.user and self.user.is_authenticated:
                # Check if existing meeting with same title exists
                existing = Meeting.objects.filter(user=self.user, title__iexact=custom_title).first()
                if existing:
                    cleaned_data['meeting'] = existing
                else:
                    # Create new meeting on the fly for manual entry
                    new_meeting = Meeting.objects.create(
                        user=self.user,
                        title=custom_title,
                        date=timezone.localdate(),
                        meeting_type='other'
                    )
                    cleaned_data['meeting'] = new_meeting
        elif not selected_meeting:
            cleaned_data['meeting'] = None

        return cleaned_data
