from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class TipoLancamento(models.TextChoices):
    RECEITA = 'receita', 'Receita'
    DESPESA = 'despesa', 'Despesa'


class StatusLancamento(models.TextChoices):
    PENDENTE = 'pendente', 'Pendente'
    PAGO = 'pago', 'Pago'
    VENCIDO = 'vencido', 'Vencido'
    CANCELADO = 'cancelado', 'Cancelado'


class FormaPagamento(models.Model):
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, related_name='formas_pagamento')
    nome = models.CharField(max_length=50)  # Ex: Dinheiro, PIX, Cartão Débito, Cartão Crédito
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Forma de Pagamento'
        verbose_name_plural = 'Formas de Pagamento'
        unique_together = ('empresa', 'nome')
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class CategoriaFinanceira(models.Model):
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, related_name='categorias_financeiras')
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TipoLancamento.choices)
    descricao = models.TextField(blank=True)
    cor = models.CharField(max_length=7, default='#6c757d')  # Cor em hexadecimal para gráficos
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Categoria Financeira'
        verbose_name_plural = 'Categorias Financeiras'
        unique_together = ('empresa', 'nome', 'tipo')
        ordering = ['tipo', 'nome']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nome}"


class LancamentoFinanceiro(models.Model):
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, related_name='lancamentos')
    
    # Tipo e categoria
    tipo = models.CharField(max_length=10, choices=TipoLancamento.choices)
    categoria = models.ForeignKey(CategoriaFinanceira, on_delete=models.PROTECT, related_name='lancamentos')
    
    # Vinculação opcional com agendamento (para receitas automáticas)
    agendamento = models.ForeignKey(
        'agendamentos.Agendamento', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='lancamentos'
    )
    
    # Dados financeiros
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    
    # Datas
    data_vencimento = models.DateField()
    data_pagamento = models.DateField(null=True, blank=True)
    
    # Status e pagamento
    status = models.CharField(max_length=20, choices=StatusLancamento.choices, default=StatusLancamento.PENDENTE)
    forma_pagamento = models.ForeignKey(
        FormaPagamento, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        related_name='lancamentos'
    )
    
    # Observações
    observacoes = models.TextField(blank=True)
    
    # Auditoria
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey('core.Usuario', on_delete=models.SET_NULL, null=True, related_name='lancamentos_criados')
    
    class Meta:
        verbose_name = 'Lançamento Financeiro'
        verbose_name_plural = 'Lançamentos Financeiros'
        ordering = ['-data_vencimento', '-criado_em']
        indexes = [
            models.Index(fields=['empresa', 'tipo', 'status']),
            models.Index(fields=['data_vencimento']),
            models.Index(fields=['data_pagamento']),
        ]
    
    def __str__(self):
        sinal = '+' if self.tipo == 'receita' else '-'
        return f"{sinal} R$ {self.valor} - {self.descricao} ({self.get_status_display()})"
    
    def marcar_como_pago(self, data_pagamento=None, forma_pagamento=None):
        """Marca o lançamento como pago"""
        from django.utils.timezone import now
        self.status = StatusLancamento.PAGO
        self.data_pagamento = data_pagamento or now().date()
        if forma_pagamento:
            self.forma_pagamento = forma_pagamento
        self.save()
    
    def cancelar(self):
        """Cancela o lançamento"""
        self.status = StatusLancamento.CANCELADO
        self.save()