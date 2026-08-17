from django import forms
from .models import Meeting


class MeetingForm(forms.ModelForm):
    txt_file = forms.FileField(
        required=False,
        label="Import from TXT File",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.txt,text/plain',
            'id': 'txt-file-input'
        })
    )

    class Meta:
        model = Meeting
        fields = ['title', 'date', 'meeting_type', 'participants', 'transcript']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Q3 Product Roadmap & Sprint Planning',
                'id': 'meeting-title',
                'required': True
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'meeting-date',
                'required': True
            }),
            'meeting_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'meeting-type'
            }),
            'participants': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Alice Smith, Bob Johnson, Charlie Davis',
                'id': 'meeting-participants'
            }),
            'transcript': forms.Textarea(attrs={
                'class': 'form-control d-none',
                'id': 'meeting-transcript-hidden',
                'rows': 8
            }),
        }

    def clean_txt_file(self):
        file = self.cleaned_data.get('txt_file')
        if file:
            if not file.name.lower().endswith('.txt'):
                raise forms.ValidationError("Only .txt text files are supported.")
            if file.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("File size cannot exceed 5MB.")
        return file
