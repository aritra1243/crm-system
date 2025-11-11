from django.urls import path
from . import views

app_name = 'allocate'

urlpatterns = [
    path('<int:job_id>/', views.allocate_job_view, name='allocate_job'),
    path('get-assignees/', views.get_assignees_ajax, name='get_assignees'),
]