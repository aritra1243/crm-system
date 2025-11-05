from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError
from .models import Job
from .forms import JobDropForm, JobCompletionForm

@login_required
def job_drop_view(request):
    """
    Job drop form for marketing team to create initial job
    """
    if request.user.role != 'marketing':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = JobDropForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                job = form.save(commit=False)
                job.created_by = request.user
                job.status = 'pending_completion'
                job.save()

                messages.success(
                    request,
                    f'Job {job.job_id} created successfully! Please complete the job details.'
                )
                # Redirect using the stable string key, not the DB pk
                return redirect('job_completion', job_id=job.job_id)

            except IntegrityError:
                messages.error(
                    request,
                    f'Job ID "{form.cleaned_data.get("job_id")}" already exists. Please use a unique ID.'
                )
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = JobDropForm()
    
    # Get all jobs created by this user
    try:
        jobs = Job.objects.filter(created_by=request.user).order_by('-created_at')
    except Exception:
        jobs = []
    
    context = {
        'form': form,
        'jobs': jobs,
    }
    
    return render(request, 'marketing/job_drop.html', context)


@login_required
def job_completion_view(request, job_id):
    """
    Job completion form to add detailed information
    """
    if request.user.role != 'marketing':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')

    # Look up by the unique string field `job_id`, scoped to the creator
    job = get_object_or_404(Job, job_id=job_id, created_by=request.user)

    # Check if job is in correct status
    if job.status not in ['pending_completion', 'draft']:
        messages.warning(request, 'This job has already been completed.')
        return redirect('job_drop')

    if request.method == 'POST':
        form = JobCompletionForm(request.POST, instance=job)
        if form.is_valid():
            try:
                job = form.save(commit=False)
                job.status = 'pending_allocation'
                job.completed_form_at = timezone.now()
                job.save()

                messages.success(
                    request,
                    f'Job {job.job_id} completion form submitted successfully! '
                    f'Job is now available for allocation.'
                )
                return redirect('job_drop')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = JobCompletionForm(instance=job)

    context = {
        'form': form,
        'job': job,
    }
    return render(request, 'marketing/job_completion.html', context)


@login_required
def job_edit_view(request, job_id):
    """
    Edit job drop details (only if not yet allocated)
    """
    if request.user.role != 'marketing':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    job = get_object_or_404(Job, id=job_id, created_by=request.user)
    
    # Only allow editing if job is not allocated yet
    if job.status in ['allocated', 'in_progress', 'submitted', 'completed']:
        messages.warning(request, 'Cannot edit job that has been allocated or completed.')
        return redirect('job_drop')
    
    if request.method == 'POST':
        form = JobDropForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            try:
                job = form.save()
                messages.success(request, f'Job {job.job_id} updated successfully!')
                return redirect('job_drop')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = JobDropForm(instance=job)
    
    # Get all jobs for sidebar
    try:
        jobs = Job.objects.filter(created_by=request.user).order_by('-created_at')
    except Exception:
        jobs = []
    
    context = {
        'form': form,
        'job': job,
        'jobs': jobs,
        'is_edit': True,
    }
    
    return render(request, 'marketing/job_drop.html', context)


@login_required
def job_list_view(request):
    """
    View all jobs created by marketing user
    """
    if request.user.role != 'marketing':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    try:
        jobs = Job.objects.filter(created_by=request.user).order_by('-created_at')
    except Exception:
        jobs = []
        messages.warning(request, 'Unable to load jobs at this time.')
    
    context = {
        'jobs': jobs,
    }
    
    return render(request, 'marketing/job_list.html', context)