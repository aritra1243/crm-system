# ==============================================
# marketing/forms.py
# ==============================================

from django import forms
from .models import Job
from django.utils import timezone
from datetime import timedelta

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
            'attachment': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }
    
    def clean_job_id(self):
        job_id = self.cleaned_data.get('job_id')
        if Job.objects.filter(job_id=job_id).exists():
            raise forms.ValidationError('This Job ID already exists. Please use a unique ID.')
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
            'amount'
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
            'referencing_style': forms.Select(attrs={
                'class': 'form-select'
            }),
            'writing_style': forms.Select(attrs={
                'class': 'form-select'
            }),
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
            })
        }
        labels = {
            'topic': 'Topic',
            'word_count': 'Word Count',
            'referencing_style': 'Referencing Style',
            'writing_style': 'Writing Style',
            'completion_instructions': 'Instructions',
            'amount': 'Amount (₹)'
        }
    
    def clean_expected_deadline(self):
        expected_deadline = self.cleaned_data.get('expected_deadline')
        
        # Ensure deadline is in the future
        if expected_deadline:
            now = timezone.now()
            if expected_deadline <= now:
                raise forms.ValidationError('Expected deadline must be in the future.')
            
            # Ensure deadline is at least 1 hour from now
            min_deadline = now + timedelta(hours=1)
            if expected_deadline < min_deadline:
                raise forms.ValidationError('Expected deadline must be at least 1 hour from now.')
        
        return expected_deadline
    
    def clean_word_count(self):
        word_count = self.cleaned_data.get('word_count')
        if word_count is not None and word_count <= 0:
            raise forms.ValidationError('Word count must be greater than 0.')
        return word_count
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError('Amount must be greater than 0.')
        return amount