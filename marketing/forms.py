from django import forms
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

from .models import Job


class JobDropForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['job_id', 'instructions', 'attachment']
        widgets = {
            'job_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter unique job ID (e.g., JOB-2024-001)'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter detailed instructions for the job...'
            }),
            'attachment': forms.FileInput(attrs={'class': 'form-control'})
        }

    # Enforce uniqueness at the app layer to avoid Djongo unique-index quirks
    def clean_job_id(self):
        job_id = self.cleaned_data.get('job_id')
        if not job_id:
            raise ValidationError('Job ID is required.')

        qs = Job.objects.filter(job_id=job_id)
        # When editing, allow keeping the same ID on the same record
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError('This Job ID already exists. Please use a unique ID.')
        return job_id


class JobCompletionForm(forms.ModelForm):
    expected_deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',
        }),
        label='Expected Deadline (IST)',
        help_text='Select the expected completion date and time'
    )

    class Meta:
        model = Job
        fields = [
            'topic',
            'word_count',
            'referencing_style',
            'writing_style',
            'completion_instructions',
            'expected_deadline',
            'amount',
        ]
        widgets = {
            'topic': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the topic (optional)'
            }),
            'word_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter word count',
                'min': '1'
            }),
            'referencing_style': forms.Select(attrs={'class': 'form-select'}),
            'writing_style': forms.Select(attrs={'class': 'form-select'}),
            'completion_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Enter detailed instructions for job completion...'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter amount',
                'step': '0.01',
                'min': '0'
            }),
        }
        labels = {
            'topic': 'Topic',
            'word_count': 'Word Count',
            'referencing_style': 'Referencing Style',
            'writing_style': 'Writing Style',
            'completion_instructions': 'Instructions',
            'amount': 'Amount (₹)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make these truly required at the form level
        self.fields['word_count'].required = True
        self.fields['amount'].required = True

    def clean_expected_deadline(self):
        expected_deadline = self.cleaned_data.get('expected_deadline')
        if expected_deadline:
            now = timezone.now()
            if expected_deadline <= now:
                raise ValidationError('Expected deadline must be in the future.')
            min_deadline = now + timedelta(hours=1)
            if expected_deadline < min_deadline:
                raise ValidationError('Expected deadline must be at least 1 hour from now.')
        return expected_deadline

    def clean_word_count(self):
        word_count = self.cleaned_data.get('word_count')
        if word_count is None:
            raise ValidationError('Word count is required.')
        if word_count <= 0:
            raise ValidationError('Word count must be greater than 0.')
        return word_count

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None:
            raise ValidationError('Amount is required.')
        if amount <= 0:
            raise ValidationError('Amount must be greater than 0.')
        return amount
