from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone

from marketing.models import Job

@login_required
def process_dashboard(request):
    if request.user.role != 'process':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')

    queue = Job.objects.filter(process_user=request.user, status='processing_queue').order_by('expected_deadline')
    done = Job.objects.filter(process_user=request.user, status='processing').order_by('-process_assigned_at')[:10]

    stats = {
        'in_queue': queue.count(),
        'completed_today': Job.objects.filter(
            process_user=request.user, status='completed',
            process_assigned_at__date=timezone.now().date()
        ).count()
    }

    return render(request, 'process/dashboard.html', {
        'queue': queue,
        'done': done,
        'stats': stats,
    })
