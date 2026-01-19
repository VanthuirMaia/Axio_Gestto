from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='backoffice_dashboard'),
    path('logs/', views.logs_view, name='backoffice_logs'),
    path('infra/', views.infra_view, name='backoffice_infra'),
]
