from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import JobDropForm
from .models import JobDrop

@login_required
def job_drop_view(request):
    """
    Job drop form view - accessible only by marketing role
    """
    if request.user.role != 'marketing':
        messages.error(request, 'Access denied. Only marketing users can access this page.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = JobDropForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.created_by = request.user
            job.save()
            messages.success(request, f'Job {job.job_id} has been dropped successfully!')
            return redirect('job_drop')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = JobDropForm()
    
    # Get recent jobs created by this user
    jobs = JobDrop.objects.filter(created_by=request.user).order_by('-created_at')
    
    context = {
        'form': form,
        'jobs': jobs,
    }
    
    return render(request, 'marketing/job_drop.html', context)


@login_required
def job_list_view(request):
    """
    View all jobs - can be accessed by multiple roles
    """
    jobs = JobDrop.objects.all().select_related('created_by').order_by('-created_at')
    
    context = {
        'jobs': jobs,
    }
    
    return render(request, 'marketing/job_list.html', context)
