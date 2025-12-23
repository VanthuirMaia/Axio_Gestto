from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email', 'empresa', 'cidade', 'ativo', 'criado_em')
    list_filter = ('empresa', 'ativo', 'cidade', 'estado')
    search_fields = ('nome', 'telefone', 'email', 'cpf')
    readonly_fields = ('criado_em', 'atualizado_em')

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('empresa', 'nome', 'telefone', 'email', 'ativo')
        }),
        ('Dados Pessoais', {
            'fields': ('cpf', 'data_nascimento')
        }),
        ('Endereço', {
            'fields': ('endereco', 'cidade', 'estado', 'cep')
        }),
        ('Observações', {
            'fields': ('notas',)
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Otimizar query com select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('empresa')
