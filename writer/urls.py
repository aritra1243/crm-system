from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.writer_dashboard, name='writer_dashboard'),
    path('start/<slug:job_id>/', views.start_job, name='writer_start'),
    path('upload-structure/<slug:job_id>/', views.upload_structure, name='writer_upload_structure'),
    path('upload-final/<slug:job_id>/', views.upload_final, name='writer_upload_final'),
]
