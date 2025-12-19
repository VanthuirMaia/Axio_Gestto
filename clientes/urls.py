from django.urls import path
from . import views

urlpatterns = [
    # Dashboard de Clientes (NOVO)
    path('dashboard/', views.dashboard_clientes, name='dashboard_clientes'),
    
    # Lista e CRUD
    path('', views.listar_clientes, name='clientes_lista'),  # ← Rota principal
    path('listar/', views.listar_clientes, name='listar_clientes'),  # ← Alias para compatibilidade
    path('criar/', views.criar_cliente, name='criar_cliente'),
    path('<int:id>/editar/', views.editar_cliente, name='editar_cliente'),
    path('<int:id>/deletar/', views.deletar_cliente, name='deletar_cliente'),
    
    # Detalhes do Cliente (NOVO)
    path('<int:id>/', views.detalhes_cliente, name='detalhes_cliente'),
]