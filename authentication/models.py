# ==============================================
# authentication/models.py (UPDATED)
# ==============================================

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('marketing', 'Marketing'),
        ('allocator', 'Allocator'),
        ('writer', 'Writer'),
        ('process', 'Process'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
        ('superadmin', 'Super Admin'),
        ('accounts_team', 'Accounts Team'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    whatsapp_no = models.CharField(max_length=15)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    
    # New fields for approval system
    approval_status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    approved_by = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_users'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'authentication_customuser'
    
    def __str__(self):
        return f"{self.email} - {self.role} ({self.approval_status})"
    
    @property
    def is_pending(self):
        return self.approval_status == 'pending'
    
    @property
    def is_approved(self):
        return self.approval_status == 'approved'
    
    @property
    def is_rejected(self):
        return self.approval_status == 'rejected'