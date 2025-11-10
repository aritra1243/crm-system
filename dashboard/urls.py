from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('change-role/<int:user_id>/', views.change_user_role, name='change_role'),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('reject-user/<int:user_id>/', views.reject_user, name='reject_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('allocator/allocate/<int:job_id>/', views.allocate_job_by_pk, name='allocate_job'),
    path('allocator/allocate-code/<slug:job_code>/', views.allocate_job_by_code, name='allocate_job_by_code'),
    path('allocator/', views.allocator_dashboard, name='allocator_dashboard'),
    path('allocator/assign/<int:pk>/', views.allocate_job_page, name='allocator_assign'),
]