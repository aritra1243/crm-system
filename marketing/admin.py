from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = [
        'job_id', 
        'topic', 
        'word_count', 
        'amount', 
        'status', 
        'created_by', 
        'allocated_to',
        'expected_deadline',
        'created_at'
    ]
    list_filter = ['status', 'created_at', 'referencing_style', 'writing_style']
    search_fields = ['job_id', 'topic', 'instructions', 'completion_instructions']
    readonly_fields = ['created_at', 'updated_at', 'completed_form_at', 'allocated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('job_id', 'status', 'created_by', 'created_at')
        }),
        ('Initial Job Drop', {
            'fields': ('instructions', 'attachment')
        }),
        ('Job Completion Details', {
            'fields': (
                'topic', 
                'word_count', 
                'referencing_style', 
                'writing_style',
                'completion_instructions',
                'expected_deadline',
                'strict_deadline',
                'amount',
                'completed_form_at'
            )
        }),
        ('Allocation', {
            'fields': ('allocated_to', 'allocated_by', 'allocated_at')
        }),
        ('Timestamps', {
            'fields': ('updated_at',)
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        # Make strict_deadline readonly since it's auto-calculated
        readonly = list(super().get_readonly_fields(request, obj))
        readonly.append('strict_deadline')
        return readonly