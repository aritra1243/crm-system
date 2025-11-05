from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from marketing.models import Job
from authentication.models import CustomUser
from .models import WriterSubmission
from .forms import StartJobForm, StructureUploadForm, FinalUploadForm

@login_required
def writer_dashboard(request):
    if request.user.role != 'writer':
        messages.error(request, 'You do not have permission to access the writer dashboard.')
        return redirect('dashboard')

    # Jobs assigned to this writer
    assigned_qs = Job.objects.filter(
        allocated_to=request.user,
        status__in=['allocated', 'in_progress', 'submitted']
    ).order_by('status', 'expected_deadline')

    # Strategic rule: only first job is fully visible, rest appear blurred until the first is submitted
    visible_job = None
    blurred_jobs = []

    for j in assigned_qs:
        # if a job is already submitted, skip it from the "gate"
        if j.status == 'submitted':
            continue

        visible_job = j
        break

    if visible_job:
        blurred_jobs = [j for j in assigned_qs if j.id != visible_job.id]
    else:
        # either no jobs or all submitted
        blurred_jobs = list(assigned_qs)

    # Ensure a submission row exists for the visible job
    if visible_job:
        WriterSubmission.objects.get_or_create(job=visible_job, writer=request.user)

    # Stats
    stats = {
        'assigned_count': Job.objects.filter(allocated_to=request.user, status__in=['allocated', 'in_progress']).count(),
        'in_progress': Job.objects.filter(allocated_to=request.user, status='in_progress').count(),
        'completed': Job.objects.filter(allocated_to=request.user, status__in=['submitted', 'completed']).count(),
        # rating is placeholder, integrate later with a reviews model if needed
        'rating': 4.8
    }

    context = {
        'visible_job': visible_job,
        'blurred_jobs': blurred_jobs,
        'stats': stats,
    }
    return render(request, 'dashboards/writer_dashboard.html', context)


@login_required
def start_job(request, job_id):
    if request.user.role != 'writer':
        messages.error(request, 'You do not have permission.')
        return redirect('dashboard')

    job = get_object_or_404(Job, job_id=job_id, allocated_to=request.user)

    submission, _ = WriterSubmission.objects.get_or_create(job=job, writer=request.user)

    if request.method == 'POST':
        form = StartJobForm(request.POST)
        if form.is_valid():
            # Move job into in_progress and mark submission started
            if job.status == 'allocated':
                job.status = 'in_progress'
                job.save(update_fields=['status', 'updated_at'])
            submission.mark_started()
            messages.success(request, f'You have started Job {job.job_id}.')
            return redirect('writer_dashboard')
    else:
        form = StartJobForm()

    return render(request, 'writer/job_start_confirm.html', {'job': job, 'form': form})


@login_required
def upload_structure(request, job_id):
    if request.user.role != 'writer':
        messages.error(request, 'You do not have permission.')
        return redirect('dashboard')

    job = get_object_or_404(Job, job_id=job_id, allocated_to=request.user)
    submission = get_object_or_404(WriterSubmission, job=job, writer=request.user)

    if request.method == 'POST':
        form = StructureUploadForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            form.save()
            # Automatically move job to in_progress if not already
            if job.status == 'allocated':
                job.status = 'in_progress'
                job.save(update_fields=['status', 'updated_at'])
            if not submission.started_at:
                submission.mark_started()
            messages.success(request, 'Structure uploaded.')
            return redirect('writer_dashboard')
    else:
        form = StructureUploadForm(instance=submission)

    return render(request, 'writer/upload_structure.html', {'job': job, 'form': form})


@login_required
def upload_final(request, job_id):
    if request.user.role != 'writer':
        messages.error(request, 'You do not have permission.')
        return redirect('dashboard')

    job = get_object_or_404(Job, job_id=job_id, allocated_to=request.user)
    submission = get_object_or_404(WriterSubmission, job=job, writer=request.user)

    if request.method == 'POST':
        form = FinalUploadForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            form.save()
            submission.mark_submitted()
            # Move job to submitted so allocator/process team can take over
            job.status = 'submitted'
            job.save(update_fields=['status', 'updated_at'])
            messages.success(request, 'Final files uploaded and summary saved. Job submitted for review.')
            return redirect('writer_dashboard')
    else:
        form = FinalUploadForm(instance=submission)

    return render(request, 'writer/upload_final.html', {'job': job, 'form': form})
