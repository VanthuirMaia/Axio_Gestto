from django.contrib import admin
from .models import Empresa, Servico, Profissional

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
