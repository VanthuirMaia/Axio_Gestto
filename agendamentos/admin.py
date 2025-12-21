from django.contrib import admin
from .models import Agendamento, AgendamentoRecorrente, LogMensagemBot, DisponibilidadeProfissional


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'servico', 'profissional', 'data_hora_inicio', 'status', 'valor_cobrado']
    list_filter = ['status', 'empresa', 'data_hora_inicio']
    search_fields = ['cliente__nome', 'servico__nome', 'profissional__nome']
    date_hierarchy = 'data_hora_inicio'
    readonly_fields = ['criado_em', 'atualizado_em']


@admin.register(AgendamentoRecorrente)
class AgendamentoRecorrenteAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'servico', 'get_frequencia_display', 'hora_inicio', 'ativo', 'data_inicio', 'data_fim']
    list_filter = ['frequencia', 'ativo', 'empresa']
    search_fields = ['cliente__nome', 'servico__nome']
    readonly_fields = ['criado_em', 'atualizado_em', 'criado_por']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('empresa', 'cliente', 'servico', 'profissional')
        }),
        ('Recorrência', {
            'fields': ('frequencia', 'dias_semana', 'dia_mes', 'hora_inicio')
        }),
        ('Período', {
            'fields': ('data_inicio', 'data_fim', 'ativo')
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em', 'criado_por'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LogMensagemBot)
class LogMensagemBotAdmin(admin.ModelAdmin):
    list_display = ['telefone', 'intencao_detectada', 'status', 'criado_em']
    list_filter = ['status', 'intencao_detectada', 'empresa']
    search_fields = ['telefone', 'mensagem_original']
    date_hierarchy = 'criado_em'
    readonly_fields = ['criado_em']


@admin.register(DisponibilidadeProfissional)
class DisponibilidadeProfissionalAdmin(admin.ModelAdmin):
    list_display = ['profissional', 'get_dia_semana_display', 'hora_inicio', 'hora_fim', 'ativo']
    list_filter = ['dia_semana', 'ativo']
    search_fields = ['profissional__nome']
