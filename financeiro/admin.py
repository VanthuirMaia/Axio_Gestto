from django.contrib import admin
from .models import FormaPagamento, CategoriaFinanceira, LancamentoFinanceiro


@admin.register(FormaPagamento)
class FormaPagamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'ativo')
    list_filter = ('ativo', 'empresa')
    search_fields = ('nome',)


@admin.register(CategoriaFinanceira)
class CategoriaFinanceiraAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'empresa', 'cor', 'ativo')
    list_filter = ('tipo', 'ativo', 'empresa')
    search_fields = ('nome', 'descricao')


@admin.register(LancamentoFinanceiro)
class LancamentoFinanceiroAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'tipo', 'valor', 'data_vencimento', 'status', 'empresa')
    list_filter = ('tipo', 'status', 'categoria', 'data_vencimento', 'empresa')
    search_fields = ('descricao', 'observacoes')
    date_hierarchy = 'data_vencimento'
    readonly_fields = ('criado_em', 'atualizado_em', 'criado_por')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('empresa', 'tipo', 'categoria', 'descricao')
        }),
        ('Valores e Datas', {
            'fields': ('valor', 'data_vencimento', 'data_pagamento')
        }),
        ('Status e Pagamento', {
            'fields': ('status', 'forma_pagamento')
        }),
        ('Vinculações', {
            'fields': ('agendamento',),
            'classes': ('collapse',)
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Auditoria', {
            'fields': ('criado_em', 'atualizado_em', 'criado_por'),
            'classes': ('collapse',)
        }),
    )