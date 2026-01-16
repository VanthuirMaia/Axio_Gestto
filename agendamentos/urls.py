from django.urls import path
from . import views

app_name = 'agendamentos'

urlpatterns = [
    # Agendamentos normais
    path('calendario/', views.calendario_view, name='calendario'),
    path('criar/', views.criar_agendamento, name='criar_agendamento'),
    path('editar/<int:id>/', views.editar_agendamento, name='editar_agendamento'),
    path('deletar/<int:id>/', views.deletar_agendamento, name='deletar_agendamento'),
    path('api/', views.api_agendamentos, name='api_agendamentos'),
    path('api/disponibilidade/', views.verificar_disponibilidade, name='verificar_disponibilidade'),
    path('api/horarios-disponiveis/', views.listar_horarios_disponiveis, name='listar_horarios_disponiveis'),

    # Agendamentos recorrentes
    path('recorrencias/', views.listar_recorrencias, name='listar_recorrencias'),
    path('recorrencias/criar/', views.criar_recorrencia, name='criar_recorrencia'),
    path('recorrencias/deletar/<int:id>/', views.deletar_recorrencia, name='deletar_recorrencia'),
    path('recorrencias/ativar-desativar/<int:id>/', views.ativar_desativar_recorrencia, name='ativar_desativar_recorrencia'),
]
