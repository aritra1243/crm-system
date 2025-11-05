from django.db import models
from django.utils import timezone
from datetime import timedelta
from authentication.models import CustomUser

class Job(models.Model):
    REFERENCING_CHOICES = [
        ('', 'Select Referencing Style'),
        ('apa', 'APA'),
        ('mla', 'MLA'),
        ('harvard', 'Harvard'),
        ('chicago', 'Chicago'),
        ('ieee', 'IEEE'),
        ('other', 'Other'),
    ]
    
    WRITING_STYLE_CHOICES = [
        ('', 'Select Writing Style'),
        ('academic', 'Academic'),
        ('professional', 'Professional'),
        ('creative', 'Creative'),
        ('technical', 'Technical'),
        ('casual', 'Casual'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_completion', 'Pending Completion'),
        ('pending_allocation', 'Pending Allocation'),
        ('allocated', 'Allocated'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Job Drop fields
    job_id = models.CharField(max_length=100, unique=True)
    instructions = models.TextField()
    attachment = models.FileField(upload_to='job_attachments/', null=True, blank=True)
    created_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='created_jobs'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Job Completion fields
    topic = models.CharField(max_length=500, blank=True, null=True)
    word_count = models.IntegerField(null=True, blank=True)
    referencing_style = models.CharField(
        max_length=50, 
        choices=REFERENCING_CHOICES, 
        blank=True, 
        null=True
    )
    writing_style = models.CharField(
        max_length=50, 
        choices=WRITING_STYLE_CHOICES, 
        blank=True, 
        null=True
    )
    completion_instructions = models.TextField(blank=True, null=True)
    expected_deadline = models.DateTimeField(null=True, blank=True)
    strict_deadline = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Status and tracking
    status = models.CharField(
        max_length=30, 
        choices=STATUS_CHOICES, 
        default='draft'
    )
    completed_form_at = models.DateTimeField(null=True, blank=True)
    
    # Allocation fields
    allocated_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='allocated_jobs'
    )
    allocated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='allocations_made'
    )
    allocated_at = models.DateTimeField(null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'marketing_job'
        # REMOVED indexes - Djongo doesn't support them well
    
    def __str__(self):
        return f"{self.job_id} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate strict deadline (24 hours after expected deadline)
        if self.expected_deadline and not self.strict_deadline:
            self.strict_deadline = self.expected_deadline + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        if self.strict_deadline and self.status not in ['completed', 'cancelled']:
            return timezone.now() > self.strict_deadline
        return False
    
    @property
    def time_remaining(self):
        if self.expected_deadline and self.status not in ['completed', 'cancelled']:
            remaining = self.expected_deadline - timezone.now()
            if remaining.total_seconds() > 0:
                days = remaining.days
                hours = remaining.seconds // 3600
                return f"{days}d {hours}h"
        return "Overdue" if self.is_overdue else "N/A"