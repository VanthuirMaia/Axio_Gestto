from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class Usuario(AbstractUser):
    """Usuário customizado para o sistema"""
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='usuarios',
        null=False,
        blank=False,
        help_text='Empresa à qual o usuário está vinculado (obrigatório)'
    )
    telefone = models.CharField(max_length=20, blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-criado_em']

    def clean(self):
        """Validação customizada para garantir que empresa seja sempre informada"""
        super().clean()
        if not self.empresa_id:
            raise ValidationError({
                'empresa': 'Todo usuário deve estar vinculado a uma empresa. Este campo é obrigatório.'
            })

    def save(self, *args, **kwargs):
        """Override save para garantir validação antes de salvar"""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_full_name() or self.username} - {self.empresa}"
