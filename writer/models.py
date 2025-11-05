from django.db import models
from django.utils import timezone
from authentication.models import CustomUser
from marketing.models import Job

def writer_upload_path(instance, filename):
    return f"writer_submissions/job_{instance.job.job_id}/{filename}"

class WriterSubmission(models.Model):
    """
    Stores a writer’s work for a single Job.
    One submission per job.
    """
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name="writer_submission")
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="writer_submissions")

    # Deliverables
    structure_file = models.FileField(upload_to=writer_upload_path, null=True, blank=True)
    final_copy = models.FileField(upload_to=writer_upload_path, null=True, blank=True)
    associate_file = models.FileField(upload_to=writer_upload_path, null=True, blank=True)  # software or associated file
    final_summary = models.TextField(blank=True, null=True)

    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    # status mirrors the writer’s phase on this job
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "writer_submission"

    def mark_started(self):
        if not self.started_at:
            self.started_at = timezone.now()
        self.status = 'in_progress'
        self.save(update_fields=['started_at', 'status', 'updated_at'])

    def mark_submitted(self):
        if not self.submitted_at:
            self.submitted_at = timezone.now()
        self.status = 'submitted'
        self.save(update_fields=['submitted_at', 'status', 'updated_at'])

    def __str__(self):
        return f"Submission for {self.job.job_id} by {self.writer.email}"
