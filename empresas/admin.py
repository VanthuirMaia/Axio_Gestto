from django.contrib import admin
from django.utils.html import format_html
from .models import Empresa, Servico, Profissional, HorarioFuncionamento, DataEspecial


class AssinaturaInline(admin.StackedInline):
    """
    Inline para criar/editar assinatura junto com a empresa
    Resolve o problema de empresa sem assinatura
    """
    from assinaturas.models import Assinatura
    model = Assinatura
    extra = 0
    max_num = 1
    can_delete = False
    fields = ('plano', 'status', 'data_expiracao', 'trial_ativo', 'gateway')
    verbose_name = 'Assinatura'
    verbose_name_plural = 'Assinatura (Criar aqui se empresa não tiver)'


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'cidade', 'ativa', 'tem_assinatura')
    list_filter = ('ativa', 'onboarding_completo')
    search_fields = ('nome', 'cnpj')
    inlines = [AssinaturaInline]

    def tem_assinatura(self, obj):
        """Mostra se empresa tem assinatura ativa"""
        try:
            if obj.assinatura:
                if obj.assinatura.status in ['trial', 'ativa']:
                    return format_html(
                        '<span style="color: green;">✓ {}</span>',
                        obj.assinatura.plano.get_nome_display()
                    )
                else:
                    return format_html(
                        '<span style="color: orange;">⚠ {}</span>',
                        obj.assinatura.get_status_display()
                    )
        except Exception:
            return format_html('<span style="color: red;">✗ Sem assinatura</span>')
    tem_assinatura.short_description = 'Assinatura'

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
