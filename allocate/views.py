from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from authentication.models import CustomUser
from marketing.models import Job

@login_required
def allocate_job_view(request, job_id):
    """
    Allocate a job to either a Writer or Process user
    """
    if request.user.role != 'allocator':
        messages.error(request, 'You do not have permission to allocate jobs.')
        return redirect('dashboard')
   
    job = get_object_or_404(Job, pk=job_id)
   
    if request.method == 'POST':
        assignee_type = request.POST.get('assignee_type')
        assignee_id = request.POST.get('assignee_id')
       
        if not assignee_type or not assignee_id:
            messages.error(request, 'Please select both assignment type and assignee.')
            return redirect('dashboard')
       
        try:
            assignee = CustomUser.objects.get(
                id=assignee_id,
                role=assignee_type,
                is_active=True,
                approval_status='approved'
            )
        except CustomUser.DoesNotExist:
            messages.error(request, 'Invalid assignee selected.')
            return redirect('dashboard')
       
        # Allocate based on type
        if assignee_type == 'writer':
            job.allocated_to = assignee
            job.allocated_by = request.user
            job.allocated_at = timezone.now()
            job.status = 'allocated'
            job.save(update_fields=['allocated_to', 'allocated_by', 'allocated_at', 'status'])
            messages.success(
                request,
                f'Job {job.job_id} successfully allocated to writer {assignee.first_name} {assignee.last_name}.'
            )
        elif assignee_type == 'process':
            job.process_user = assignee
            job.process_assigned_at = timezone.now()
            job.status = 'processing_queue'
            job.save(update_fields=['process_user', 'process_assigned_at', 'status'])
            messages.success(
                request,
                f'Job {job.job_id} successfully assigned to process user {assignee.first_name} {assignee.last_name}.'
            )
       
        return redirect('dashboard')
   
    # GET request - redirect to dashboard
    return redirect('dashboard')

@login_required
def get_assignees_ajax(request):
    """
    AJAX endpoint to get list of writers or process users
    """
    if request.user.role != 'allocator':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
   
    assignee_type = request.GET.get('type')
   
    if assignee_type not in ['writer', 'process']:
        return JsonResponse({'error': 'Invalid type'}, status=400)
   
    users = CustomUser.objects.filter(
        role=assignee_type,
        is_active=True,
        approval_status='approved'
    ).values('id', 'first_name', 'last_name', 'email').order_by('first_name', 'last_name')
   
    return JsonResponse({'assignees': list(users)})