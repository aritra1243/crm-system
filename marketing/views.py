from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError
from django.http import Http404

from .models import Job
from .forms import JobDropForm, JobCompletionForm


def _dedupe_jobs(qs):
    """
    Return a list of jobs deduped by job_id, keeping the most recent created_at.
    Safe for Djongo because we dedupe in Python, not via SQL/aggregation.
    """
    latest_by_id = {}
    for j in qs:
        current = latest_by_id.get(j.job_id)
        if current is None:
            latest_by_id[j.job_id] = j
        else:
            cur_ts = getattr(current, "created_at", None)
            new_ts = getattr(j, "created_at", None)
            if cur_ts is None or (new_ts and new_ts > cur_ts):
                latest_by_id[j.job_id] = j

    # Sort by created_at desc, fallback to now if missing
    def _key(obj):
        return getattr(obj, "created_at", timezone.now())
    return sorted(latest_by_id.values(), key=_key, reverse=True)


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

    # Load and de-duplicate jobs for this user
    try:
        base_qs = Job.objects.filter(created_by=request.user).order_by('-created_at')
        jobs = _dedupe_jobs(base_qs)
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
    Job completion form to add detailed information.
    Djongo-safe filtering and duplicate handling for same job_id.
    """
    if request.user.role != 'marketing':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')

    # Djongo-safe: avoid .exists()/.count(); use slice-to-list
    try:
        candidates = list(
            Job.objects.filter(job_id=job_id, created_by=request.user).order_by('-created_at')[:20]
        )
    except Exception as e:
        # If the driver itself fails, show 404-like behavior
        raise Http404("Unable to load job records.") from e

    if not candidates:
        raise Http404("Job not found.")

    # Prefer a pending/draft record if present, else the newest
    job = None
    for c in candidates:
        if c.status in ('pending_completion', 'draft'):
            job = c
            break
    if job is None:
        job = candidates[0]

    # Warn if we detect duplicates for same job_id
    if len(candidates) > 1:
        messages.warning(
            request,
            'Multiple records found with the same Job ID. Using the latest pending/draft one.'
        )

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

    # Sidebar jobs, deduped
    try:
        base_qs = Job.objects.filter(created_by=request.user).order_by('-created_at')
        jobs = _dedupe_jobs(base_qs)
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
    View all jobs created by marketing user (deduped by job_id)
    """
    if request.user.role != 'marketing':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')

    try:
        base_qs = Job.objects.filter(created_by=request.user).order_by('-created_at')
        jobs = _dedupe_jobs(base_qs)
    except Exception:
        jobs = []
        messages.warning(request, 'Unable to load jobs at this time.')

    context = {'jobs': jobs}
    return render(request, 'marketing/job_list.html', context)
