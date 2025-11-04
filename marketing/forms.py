from django import forms
from .models import JobDrop

class JobDropForm(forms.ModelForm):
    class Meta:
        model = JobDrop
        fields = ['job_id', 'instructions', 'attachment']
        widgets = {
            'job_id': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter Job ID (e.g., JOB-2024-001)'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 8, 
                'placeholder': 'Enter detailed instructions here...\n\nYou can use special characters like @, #, $, %, etc.'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'job_id': 'Job ID',
            'instructions': 'Instructions',
            'attachment': 'Attachment (Optional)',
        }
    
    def clean_job_id(self):
        job_id = self.cleaned_data.get('job_id')
        if job_id:
            job_id = job_id.strip().upper()
        return job_id
