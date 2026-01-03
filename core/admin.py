from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'empresa', 'ativo', 'is_staff')
    list_filter = ('ativo', 'empresa', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-criado_em',)

    # Campos exibidos no formulário
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('username', 'password', 'email')
        }),
        ('Informações Pessoais', {
            'fields': ('first_name', 'last_name', 'telefone')
        }),
        ('EMPRESA (OBRIGATÓRIO)', {
            'fields': ('empresa',),
            'description': '⚠️ TODO USUÁRIO DEVE ESTAR VINCULADO A UMA EMPRESA. Este campo é obrigatório.'
        }),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'ativo', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Datas Importantes', {
            'fields': ('last_login', 'date_joined', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )

    # Campos para adicionar novo usuário
    add_fieldsets = (
        ('Informações de Login', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('EMPRESA (OBRIGATÓRIO)', {
            'classes': ('wide',),
            'fields': ('empresa',),
            'description': '⚠️ TODO USUÁRIO DEVE ESTAR VINCULADO A UMA EMPRESA. Este campo é obrigatório.'
        }),
        ('Informações Pessoais', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'telefone'),
        }),
        ('Permissões', {
            'classes': ('wide', 'collapse'),
            'fields': ('is_active', 'is_staff', 'ativo'),
        }),
    )

    readonly_fields = ('criado_em', 'atualizado_em', 'last_login', 'date_joined')
