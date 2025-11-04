from django.urls import path
from . import views

urlpatterns = [
    path('job-drop/', views.job_drop_view, name='job_drop'),
    path('jobs/', views.job_list_view, name='job_list'),
]