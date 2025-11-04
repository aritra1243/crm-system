from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from authentication.models import CustomUser
from marketing.models import Job

@login_required
def dashboard_view(request):
    """
    Main dashboard view that routes users to their role-specific dashboard
    """
    role = request.user.role
    
    # Map roles to their respective templates
    template_map = {
        'user': 'dashboards/user_dashboard.html',
        'marketing': 'dashboards/marketing_dashboard.html',
        'allocator': 'dashboards/allocator_dashboard.html',
        'writer': 'dashboards/writer_dashboard.html',
        'process': 'dashboards/process_dashboard.html',
        'manager': 'dashboards/manager_dashboard.html',
        'admin': 'dashboards/admin_dashboard.html',
        'superadmin': 'dashboards/superadmin_dashboard.html',
        'accounts_team': 'dashboards/accounts_dashboard.html',
    }
    
    template = template_map.get(role, 'dashboards/user_dashboard.html')
    
    context = {
        'user': request.user,
    }
    
    # Add additional context for admin and superadmin
    if role in ['admin', 'superadmin']:
        context['users'] = CustomUser.objects.filter(
            approval_status='approved'
        ).order_by('-date_joined')
        
        # Get pending approval users
        context['pending_users'] = CustomUser.objects.filter(
            approval_status='pending'
        ).order_by('-date_joined')
        
        # Get rejected users
        context['rejected_users'] = CustomUser.objects.filter(
            approval_status='rejected'
        ).order_by('-date_joined')
    
    # Add additional context for allocator
    if role == 'allocator':
        # Get all jobs pending allocation
        context['pending_jobs'] = Job.objects.filter(
            status='pending_allocation'
        ).order_by('-completed_form_at')
        
        # Get allocated jobs
        context['allocated_jobs'] = Job.objects.filter(
            status__in=['allocated', 'in_progress']
        ).order_by('-allocated_at')
        
        # Get completed jobs
        context['completed_jobs'] = Job.objects.filter(
            status='completed'
        ).order_by('-updated_at')[:10]
        
        # Get available writers
        context['writers'] = CustomUser.objects.filter(
            role='writer',
            is_active=True,
            approval_status='approved'
        )
        
        # Statistics
        context['stats'] = {
            'pending_count': Job.objects.filter(status='pending_allocation').count(),
            'allocated_today': Job.objects.filter(
                allocated_at__date=timezone.now().date()
            ).count(),
            'active_writers': CustomUser.objects.filter(
                role='writer',
                is_active=True,
                approval_status='approved'
            ).count(),
            'overdue_count': Job.objects.filter(
                status__in=['allocated', 'in_progress'],
                strict_deadline__lt=timezone.now()
            ).count(),
        }
    
    return render(request, template, context)


@login_required
def change_user_role(request, user_id):
    """
    Allow admin and superadmin to change user roles
    """
    if request.user.role not in ['admin', 'superadmin']:
        messages.error(request, 'You do not have permission to change user roles.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=user_id)
        new_role = request.POST.get('role')
        
        # Prevent changing own role
        if user.id == request.user.id:
            messages.warning(request, 'You cannot change your own role.')
            return redirect('dashboard')
        
        # Validate role choice
        valid_roles = [choice[0] for choice in CustomUser.ROLE_CHOICES]
        if new_role in valid_roles:
            old_role = user.get_role_display()
            user.role = new_role
            user.save()
            messages.success(
                request, 
                f'Role changed successfully for {user.email} from {old_role} to {user.get_role_display()}'
            )
        else:
            messages.error(request, 'Invalid role selected.')
    
    return redirect('dashboard')


@login_required
def approve_user(request, user_id):
    """
    Approve a pending user registration
    """
    if request.user.role not in ['admin', 'superadmin']:
        messages.error(request, 'You do not have permission to approve users.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=user_id)
        
        if user.approval_status != 'pending':
            messages.warning(request, f'User {user.email} is not pending approval.')
            return redirect('dashboard')
        
        # Get selected role from form
        selected_role = request.POST.get('role')
        
        # Validate role
        valid_roles = [choice[0] for choice in CustomUser.ROLE_CHOICES]
        if selected_role not in valid_roles:
            messages.error(request, 'Invalid role selected.')
            return redirect('dashboard')
        
        # Approve user
        user.approval_status = 'approved'
        user.is_active = True
        user.role = selected_role
        user.approved_by = request.user
        user.approved_at = timezone.now()
        user.save()
        
        messages.success(
            request, 
            f'User {user.email} has been approved with role: {user.get_role_display()}'
        )
    
    return redirect('dashboard')


@login_required
def reject_user(request, user_id):
    """
    Reject a pending user registration
    """
    if request.user.role not in ['admin', 'superadmin']:
        messages.error(request, 'You do not have permission to reject users.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=user_id)
        
        if user.approval_status != 'pending':
            messages.warning(request, f'User {user.email} is not pending approval.')
            return redirect('dashboard')
        
        # Get rejection reason
        rejection_reason = request.POST.get('rejection_reason', '')
        
        # Reject user
        user.approval_status = 'rejected'
        user.is_active = False
        user.rejection_reason = rejection_reason
        user.approved_by = request.user
        user.approved_at = timezone.now()
        user.save()
        
        messages.success(
            request, 
            f'User {user.email} registration has been rejected.'
        )
    
    return redirect('dashboard')


@login_required
def delete_user(request, user_id):
    """
    Delete a user (only rejected or pending users)
    """
    if request.user.role not in ['admin', 'superadmin']:
        messages.error(request, 'You do not have permission to delete users.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=user_id)
        
        # Prevent deleting own account
        if user.id == request.user.id:
            messages.warning(request, 'You cannot delete your own account.')
            return redirect('dashboard')
        
        # Only allow deleting pending or rejected users
        if user.approval_status in ['pending', 'rejected']:
            email = user.email
            user.delete()
            messages.success(request, f'User {email} has been deleted.')
        else:
            messages.error(request, 'You can only delete pending or rejected users.')
    
    return redirect('dashboard')