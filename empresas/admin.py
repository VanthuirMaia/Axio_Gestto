from django.contrib import admin
from .models import Empresa, Servico, Profissional, HorarioFuncionamento, DataEspecial

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'cidade', 'ativa')
    list_filter = ('ativa',)
    search_fields = ('nome', 'cnpj')

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'preco', 'duracao_minutos')
    list_filter = ('empresa',)

@admin.register(Profissional)
class ProfissionalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'email', 'ativo')
    list_filter = ('empresa', 'ativo')

@admin.register(HorarioFuncionamento)
class HorarioFuncionamentoAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'dia_semana_display', 'hora_abertura', 'hora_fechamento', 'intervalo', 'ativo')
    list_filter = ('empresa', 'dia_semana', 'ativo')
    ordering = ('empresa', 'dia_semana')

    def dia_semana_display(self, obj):
        return obj.get_dia_semana_display()
    dia_semana_display.short_description = 'Dia da Semana'

    def intervalo(self, obj):
        if obj.intervalo_inicio and obj.intervalo_fim:
            return f"{obj.intervalo_inicio.strftime('%H:%M')} - {obj.intervalo_fim.strftime('%H:%M')}"
        return '-'
    intervalo.short_description = 'Intervalo'

@admin.register(DataEspecial)
class DataEspecialAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'data', 'descricao', 'tipo', 'horarios')
    list_filter = ('empresa', 'tipo', 'data')
    ordering = ('empresa', '-data')

    def horarios(self, obj):
        if obj.tipo == 'feriado':
            return 'FECHADO'
        elif obj.hora_abertura and obj.hora_fechamento:
            return f"{obj.hora_abertura.strftime('%H:%M')} - {obj.hora_fechamento.strftime('%H:%M')}"
        return '-'
    horarios.short_description = 'Horários'
