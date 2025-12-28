"""
Admin para gerenciar planos e assinaturas
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Plano, Assinatura, HistoricoPagamento


@admin.register(Plano)
class PlanoAdmin(admin.ModelAdmin):
    list_display = [
        'nome',
        'preco_mensal_display',
        'max_profissionais',
        'max_agendamentos_mes',
        'max_usuarios',
        'trial_dias',
        'ativo',
        'total_assinaturas'
    ]
    list_filter = ['ativo', 'nome']
    search_fields = ['nome', 'descricao']
    ordering = ['ordem_exibicao', 'preco_mensal']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'preco_mensal', 'ativo', 'ordem_exibicao')
        }),
        ('Limites do Plano', {
            'fields': (
                'max_profissionais',
                'max_agendamentos_mes',
                'max_usuarios',
                'max_servicos',
                'trial_dias'
            )
        }),
        ('Recursos Adicionais', {
            'fields': (
                'permite_relatorios_avancados',
                'permite_integracao_contabil',
                'permite_multi_unidades'
            ),
            'classes': ('collapse',)
        }),
    )

    def preco_mensal_display(self, obj):
        return format_html('<strong>R$ {}</strong>', obj.preco_mensal)
    preco_mensal_display.short_description = 'Preço/Mês'

    def total_assinaturas(self, obj):
        total = obj.assinaturas.count()
        ativas = obj.assinaturas.filter(status__in=['trial', 'ativa']).count()
        return format_html(
            '<span style="color: green;">{}</span> / {} total',
            ativas, total
        )
    total_assinaturas.short_description = 'Assinaturas Ativas'


@admin.register(Assinatura)
class AssinaturaAdmin(admin.ModelAdmin):
    list_display = [
        'empresa',
        'plano',
        'status_badge',
        'trial_ativo',
        'data_expiracao',
        'dias_restantes_display',
        'ultimo_pagamento',
        'acoes'
    ]
    list_filter = ['status', 'trial_ativo', 'plano', 'gateway']
    search_fields = ['empresa__nome', 'empresa__cnpj', 'subscription_id_externo']
    readonly_fields = [
        'criado_em',
        'atualizado_em',
        'data_inicio',
        'subscription_id_externo',
        'customer_id_externo',
        'helper_info'
    ]
    date_hierarchy = 'data_inicio'

    fieldsets = (
        ('Assinatura', {
            'fields': ('helper_info', 'empresa', 'plano', 'status')
        }),
        ('Datas e Trial', {
            'fields': (
                'data_inicio',
                'data_expiracao',
                'trial_ativo',
                'ultimo_pagamento',
                'proximo_vencimento'
            ),
            'description': 'DICA: Se trial_ativo=True, a data_expiracao será automaticamente calculada com base no trial_dias do plano.'
        }),
        ('Gateway de Pagamento', {
            'fields': (
                'gateway',
                'subscription_id_externo',
                'customer_id_externo'
            ),
            'classes': ('collapse',)
        }),
        ('Cancelamento', {
            'fields': (
                'cancelada_em',
                'motivo_cancelamento'
            ),
            'classes': ('collapse',)
        }),
        ('Controle', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )

    def helper_info(self, obj):
        """Mostra informações úteis ao criar assinatura"""
        if obj and obj.pk:
            return format_html(
                '<div style="background: #dbeafe; padding: 10px; border-radius: 5px; border-left: 4px solid #3b82f6;">'
                '<strong>ℹ️ Informação:</strong><br>'
                'Status: {}<br>'
                'Dias restantes: {}<br>'
                'Plano: {} (R$ {}/mês)'
                '</div>',
                obj.get_status_display(),
                obj.dias_restantes(),
                obj.plano.get_nome_display(),
                obj.plano.preco_mensal
            )
        else:
            return format_html(
                '<div style="background: #fef3c7; padding: 10px; border-radius: 5px; border-left: 4px solid #f59e0b;">'
                '<strong>⚠️ Criando Nova Assinatura:</strong><br>'
                '1. Selecione a empresa<br>'
                '2. Escolha o plano<br>'
                '3. Marque trial_ativo se for trial<br>'
                '4. Defina data_expiracao (ex: hoje + 7 dias para trial)<br>'
                '5. Gateway = "manual" se for criação manual'
                '</div>'
            )
    helper_info.short_description = 'Guia Rápido'

    actions = ['renovar_assinaturas', 'suspender_assinaturas', 'reativar_assinaturas']

    def status_badge(self, obj):
        colors = {
            'trial': '#3b82f6',
            'ativa': '#10b981',
            'suspensa': '#f59e0b',
            'cancelada': '#ef4444',
            'expirada': '#6b7280'
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def dias_restantes_display(self, obj):
        dias = obj.dias_restantes()
        if dias == 0:
            return format_html('<span style="color: red;">EXPIRADO</span>')
        elif dias <= 3:
            return format_html('<span style="color: orange;">{} dias</span>', dias)
        else:
            return f'{dias} dias'
    dias_restantes_display.short_description = 'Dias Restantes'

    def acoes(self, obj):
        empresa_url = reverse('admin:empresas_empresa_change', args=[obj.empresa.id])
        return format_html(
            '<a class="button" href="{}">Ver Empresa</a>',
            empresa_url
        )
    acoes.short_description = 'Ações'

    def renovar_assinaturas(self, request, queryset):
        count = 0
        for assinatura in queryset:
            assinatura.renovar(30)
            count += 1
        self.message_user(request, f'{count} assinatura(s) renovada(s) por 30 dias.')
    renovar_assinaturas.short_description = 'Renovar por 30 dias'

    def suspender_assinaturas(self, request, queryset):
        count = queryset.update(status='suspensa')
        self.message_user(request, f'{count} assinatura(s) suspensa(s).')
    suspender_assinaturas.short_description = 'Suspender assinaturas'

    def reativar_assinaturas(self, request, queryset):
        count = 0
        for assinatura in queryset.filter(status='suspensa'):
            assinatura.reativar()
            count += 1
        self.message_user(request, f'{count} assinatura(s) reativada(s).')
    reativar_assinaturas.short_description = 'Reativar assinaturas'


@admin.register(HistoricoPagamento)
class HistoricoPagamentoAdmin(admin.ModelAdmin):
    list_display = [
        'assinatura',
        'valor_display',
        'status_badge',
        'gateway',
        'payment_method',
        'data_criacao',
        'data_aprovacao'
    ]
    list_filter = ['status', 'gateway', 'payment_method']
    search_fields = [
        'assinatura__empresa__nome',
        'transaction_id',
        'assinatura__subscription_id_externo'
    ]
    readonly_fields = [
        'assinatura',
        'valor',
        'gateway',
        'transaction_id',
        'data_criacao',
        'webhook_payload'
    ]
    date_hierarchy = 'data_criacao'

    fieldsets = (
        ('Pagamento', {
            'fields': ('assinatura', 'valor', 'status')
        }),
        ('Gateway', {
            'fields': (
                'gateway',
                'transaction_id',
                'payment_method'
            )
        }),
        ('Datas', {
            'fields': (
                'data_criacao',
                'data_aprovacao',
                'data_vencimento'
            )
        }),
        ('Dados Técnicos', {
            'fields': ('metadados', 'webhook_payload'),
            'classes': ('collapse',)
        }),
    )

    def valor_display(self, obj):
        return format_html('<strong>R$ {}</strong>', obj.valor)
    valor_display.short_description = 'Valor'

    def status_badge(self, obj):
        colors = {
            'pendente': '#6b7280',
            'processando': '#3b82f6',
            'aprovado': '#10b981',
            'recusado': '#ef4444',
            'estornado': '#f59e0b',
            'cancelado': '#ef4444'
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
