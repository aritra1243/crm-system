from django.urls import path
from . import views

urlpatterns = [
    path('job-drop/', views.job_drop_view, name='job_drop'),
    path('job-completion/<int:job_id>/', views.job_completion_view, name='job_completion'),
    path('job-list/', views.job_list_view, name='job_list'),
]