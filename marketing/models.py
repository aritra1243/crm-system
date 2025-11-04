from django.db import models
from authentication.models import CustomUser

class JobDrop(models.Model):
    job_id = models.CharField(max_length=100, unique=True)
    instructions = models.TextField()
    attachment = models.FileField(upload_to='job_attachments/', null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='job_drops')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'marketing_jobdrop'
        ordering = ['-created_at']
        verbose_name = 'Job Drop'
        verbose_name_plural = 'Job Drops'
    
    def __str__(self):
        return f"{self.job_id} - {self.created_by.email}"
