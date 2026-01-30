from django.urls import path
from . import views
from core.views import alterar_senha

urlpatterns = [
    path('', views.configuracoes_dashboard, name='configuracoes_dashboard'),

    # Primeiros Passos (Guia de Configuração Inicial)
    path('primeiros-passos/', views.primeiros_passos, name='primeiros_passos'),

    # Dados da Empresa
    path('empresa/', views.empresa_dados, name='empresa_dados'),

    # Alterar Senha
    path('alterar-senha/', alterar_senha, name='alterar_senha'),

    # Assinatura e Plano (SaaS)
    path('assinatura/', views.assinatura_gerenciar, name='configuracoes_assinatura'),
    path('assinatura/alterar-plano/', views.assinatura_alterar_plano, name='assinatura_alterar_plano'),
    path('assinatura/cancelar/', views.assinatura_cancelar, name='assinatura_cancelar'),
    path('assinatura/reativar/', views.assinatura_reativar, name='assinatura_reativar'),
    path('assinatura/checkout/', views.assinatura_gerar_checkout, name='assinatura_gerar_checkout'),

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

    # Usuarios da Empresa
    path('usuarios/', views.usuarios_lista, name='usuarios_lista'),
    path('usuarios/novo/', views.usuario_criar, name='usuario_criar'),
    path('usuarios/<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),
    path('usuarios/<int:pk>/deletar/', views.usuario_deletar, name='usuario_deletar'),

    # Horários de Funcionamento
    path('horarios/', views.horarios_funcionamento, name='horarios_funcionamento'),
    path('horarios/datas-especiais/', views.datas_especiais_lista, name='datas_especiais_lista'),
    path('horarios/datas-especiais/nova/', views.data_especial_criar, name='data_especial_criar'),
    path('horarios/datas-especiais/<int:pk>/editar/', views.data_especial_editar, name='data_especial_editar'),
    path('horarios/datas-especiais/<int:pk>/deletar/', views.data_especial_deletar, name='data_especial_deletar'),

    # WhatsApp / Evolution API
    path('whatsapp/', views.whatsapp_dashboard, name='whatsapp_dashboard'),
    path('whatsapp/criar-instancia/', views.whatsapp_criar_instancia, name='whatsapp_criar_instancia'),
    path('whatsapp/obter-qr/', views.whatsapp_obter_qr, name='whatsapp_obter_qr'),
    path('whatsapp/status/', views.whatsapp_verificar_status, name='whatsapp_verificar_status'),
    path('whatsapp/desconectar/', views.whatsapp_desconectar, name='whatsapp_desconectar'),
    path('whatsapp/deletar/', views.whatsapp_deletar_instancia, name='whatsapp_deletar'),
    path('whatsapp/reconfigurar/', views.whatsapp_reconfigurar, name='whatsapp_reconfigurar'),
    path('whatsapp/sincronizar/', views.whatsapp_sincronizar, name='whatsapp_sincronizar'),
    path('whatsapp/resetar/', views.whatsapp_resetar_config, name='whatsapp_resetar'),
]