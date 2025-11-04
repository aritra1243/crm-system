from django.contrib import admin
from .models import JobDrop

@admin.register(JobDrop)
class JobDropAdmin(admin.ModelAdmin):
    list_display = ['job_id', 'created_by', 'created_at', 'updated_at', 'has_attachment']
    list_filter = ['created_at', 'created_by']
    search_fields = ['job_id', 'instructions', 'created_by__email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Job Information', {
            'fields': ('job_id', 'instructions', 'attachment')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_attachment(self, obj):
        return bool(obj.attachment)
    has_attachment.boolean = True
    has_attachment.short_description = 'Attachment'
