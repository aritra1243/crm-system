from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('change-role/<int:user_id>/', views.change_user_role, name='change_role'),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('reject-user/<int:user_id>/', views.reject_user, name='reject_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
]