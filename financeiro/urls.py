from django.urls import path
from . import views

urlpatterns = [
    path('', views.financeiro_dashboard, name='financeiro_dashboard'),
    path('lancamentos/', views.lancamentos_lista, name='lancamentos_lista'),
    path('lancamentos/novo/', views.lancamento_criar, name='lancamento_criar'),
    path('lancamentos/<int:pk>/editar/', views.lancamento_editar, name='lancamento_editar'),
    path('lancamentos/<int:pk>/deletar/', views.lancamento_deletar, name='lancamento_deletar'),
    path('lancamentos/<int:pk>/pagar/', views.marcar_como_pago, name='marcar_como_pago'),
]