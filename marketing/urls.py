from django.urls import path
from . import views

urlpatterns = [
    path('job-drop/', views.job_drop_view, name='job_drop'),
    # accept hyphens, letters and digits for your custom string job_id like "JOB-2024-001"
    path('job-completion/<slug:job_id>/', views.job_completion_view, name='job_completion'),
    path('job-edit/<int:job_id>/', views.job_edit_view, name='job_edit'),
    path('jobs/', views.job_list_view, name='job_list'),
]
