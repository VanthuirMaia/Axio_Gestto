from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'empresa', 'ativo')
    list_filter = ('ativo', 'empresa')
    search_fields = ('username', 'email')
