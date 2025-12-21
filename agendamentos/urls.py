from django.urls import path
from . import views

app_name = 'agendamentos'

urlpatterns = [
    path('calendario/', views.calendario_view, name='calendario'),
    path('criar/', views.criar_agendamento, name='criar_agendamento'),
    path('editar/<int:id>/', views.editar_agendamento, name='editar_agendamento'),
    path('deletar/<int:id>/', views.deletar_agendamento, name='deletar_agendamento'),
    path('api/', views.api_agendamentos, name='api_agendamentos'),
]
