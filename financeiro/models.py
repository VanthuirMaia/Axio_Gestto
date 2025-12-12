from django.db import models
from django.core.validators import MinValueValidator

class Transacao(models.Model):
    TIPO_CHOICES = [
        ('receita', 'Receita'),
        ('despesa', 'Despesa'),
    ]

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]

    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, related_name='transacoes')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmada')
    
    agendamento = models.ForeignKey('agendamentos.Agendamento', on_delete=models.SET_NULL, null=True, blank=True, related_name='transacoes')
    profissional = models.ForeignKey('empresas.Profissional', on_delete=models.SET_NULL, null=True, blank=True, related_name='comissoes')
    
    data_transacao = models.DateField()
    data_vencimento = models.DateField(null=True, blank=True)
    data_pagamento = models.DateField(null=True, blank=True)
    
    notas = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Transacao'
        verbose_name_plural = 'Transacoes'
        ordering = ['-data_transacao']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.descricao} - R$ {self.valor}"

    def esta_paga(self):
        return self.data_pagamento is not None


class Categoria(models.Model):
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, related_name='categorias_financeiras')
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=[('receita', 'Receita'), ('despesa', 'Despesa')])
    cor = models.CharField(max_length=7, default='#3b82f6')
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        unique_together = ('empresa', 'nome', 'tipo')

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"
