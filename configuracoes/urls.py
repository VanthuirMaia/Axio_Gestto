from django.urls import path
from . import views

urlpatterns = [
    path('', views.configuracoes_dashboard, name='configuracoes_dashboard'),

    # Assinatura e Plano (SaaS)
    path('assinatura/', views.assinatura_gerenciar, name='configuracoes_assinatura'),

    # Serviços
    path('servicos/', views.servicos_lista, name='servicos_lista'),
    path('servicos/novo/', views.servico_criar, name='servico_criar'),
    path('servicos/<int:pk>/editar/', views.servico_editar, name='servico_editar'),
    path('servicos/<int:pk>/deletar/', views.servico_deletar, name='servico_deletar'),

    # Profissionais
    path('profissionais/', views.profissionais_lista, name='profissionais_lista'),
    path('profissionais/novo/', views.profissional_criar, name='profissional_criar'),
    path('profissionais/<int:pk>/editar/', views.profissional_editar, name='profissional_editar'),
    path('profissionais/<int:pk>/deletar/', views.profissional_deletar, name='profissional_deletar'),

    # Categorias
    path('categorias/', views.categorias_lista, name='categorias_lista'),
    path('categorias/nova/', views.categoria_criar, name='categoria_criar'),
    path('categorias/<int:pk>/editar/', views.categoria_editar, name='categoria_editar'),

    # Formas de Pagamento
    path('formas-pagamento/', views.formas_pagamento_lista, name='formas_pagamento_lista'),
    path('formas-pagamento/nova/', views.forma_pagamento_criar, name='forma_pagamento_criar'),
    path('formas-pagamento/<int:pk>/editar/', views.forma_pagamento_editar, name='forma_pagamento_editar'),
]