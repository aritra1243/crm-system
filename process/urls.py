from django.urls import path
from . import views

urlpatterns = [
    path('', views.process_dashboard, name='process_dashboard'),
]
