from django import forms
from .models import WriterSubmission

class StartJobForm(forms.Form):
    confirm = forms.BooleanField(required=True, label="I want to start this job now")

class StructureUploadForm(forms.ModelForm):
    class Meta:
        model = WriterSubmission
        fields = ['structure_file']
        widgets = {
            'structure_file': forms.FileInput(attrs={'class': 'form-control'})
        }

class FinalUploadForm(forms.ModelForm):
    class Meta:
        model = WriterSubmission
        fields = ['final_copy', 'associate_file', 'final_summary']
        widgets = {
            'final_copy': forms.FileInput(attrs={'class': 'form-control'}),
            'associate_file': forms.FileInput(attrs={'class': 'form-control'}),
            'final_summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Paste or write a short summary of the final copy…'})
        }

    def clean(self):
        cleaned = super().clean()
        final_copy = cleaned.get('final_copy')
        if not final_copy:
            self.add_error('final_copy', 'Final copy is required to submit.')
        return cleaned
