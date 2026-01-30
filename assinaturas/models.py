"""
Models para sistema de assinaturas SaaS
"""
from django.db import models
from django.utils.timezone import now, timedelta
from django.core.validators import MinValueValidator


class Plano(models.Model):
    """
    Planos de assinatura disponíveis
    """
    PLANOS = [
        ('basico', 'Básico'),
        ('essencial', 'Essencial'),
        ('profissional', 'Profissional'),
    ]

    nome = models.CharField(
        max_length=50,
        choices=PLANOS,
        unique=True,
        help_text="Tipo de plano"
    )
    descricao = models.TextField(
        help_text="Descrição do que está incluído no plano"
    )
    preco_mensal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Preço em R$ por mês"
    )

    # Limites do plano
    max_profissionais = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Quantidade máxima de profissionais"
    )
    max_agendamentos_mes = models.IntegerField(
        default=500,
        validators=[MinValueValidator(1)],
        help_text="Máximo de agendamentos por mês"
    )
    max_usuarios = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Quantidade máxima de usuários (logins)"
    )
    max_servicos = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1)],
        help_text="Quantidade máxima de serviços cadastrados"
    )

    # IDs dos produtos nos gateways de pagamento
    stripe_price_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Price ID do produto no Stripe (ex: price_1ABC...)"
    )
    asaas_plan_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="ID do plano no Asaas (se aplicável)"
    )

    # Trial
    trial_dias = models.IntegerField(
        default=15,
        validators=[MinValueValidator(0)],
        help_text="Dias de trial gratuito"
    )

    # Recursos adicionais (features flags)
    # NOVAS FLAGS ESPECÍFICAS (estratégia 2 planos simplificada)
    permite_financeiro = models.BooleanField(
        default=False,
        help_text="Permite acesso ao módulo Financeiro completo"
    )
    permite_dashboard_clientes = models.BooleanField(
        default=False,
        help_text="Permite acesso ao Dashboard de Clientes com métricas"
    )
    permite_recorrencias = models.BooleanField(
        default=False,
        help_text="Permite criar agendamentos recorrentes"
    )

    # Follow-up / Lembretes
    permite_lembrete_1_dia = models.BooleanField(
        default=True,
        help_text="Permite enviar lembrete 1 dia (24h) antes do agendamento"
    )
    permite_lembrete_1_hora = models.BooleanField(
        default=False,
        help_text="Permite enviar lembrete 1 hora antes do agendamento (plano superior)"
    )

    # WhatsApp Bot
    permite_whatsapp_bot = models.BooleanField(
        default=True,
        help_text="Permite usar o WhatsApp Bot para agendamentos automáticos"
    )

    # FLAGS ANTIGAS (manter por compatibilidade, serão removidas futuramente)
    permite_relatorios_avancados = models.BooleanField(
        default=False,
        help_text="DEPRECATED - usar permite_financeiro e permite_dashboard_clientes"
    )
    permite_integracao_contabil = models.BooleanField(
        default=False,
        help_text="DEPRECATED - funcionalidade não implementada"
    )
    permite_multi_unidades = models.BooleanField(
        default=False,
        help_text="DEPRECATED - funcionalidade não implementada"
    )

    # Controle
    ativo = models.BooleanField(default=True)
    ordem_exibicao = models.IntegerField(default=0, help_text="Ordem na página de preços")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Plano'
        verbose_name_plural = 'Planos'
        ordering = ['ordem_exibicao', 'preco_mensal']

    def __str__(self):
        return f"{self.get_nome_display()} - R$ {self.preco_mensal}/mês"


class Assinatura(models.Model):
    """
    Assinatura de uma empresa a um plano
    """
    STATUS = [
        ('trial', 'Trial (Teste Grátis)'),
        ('ativa', 'Ativa'),
        ('suspensa', 'Suspensa por Falta de Pagamento'),
        ('cancelada', 'Cancelada'),
        ('expirada', 'Expirada'),
    ]

    empresa = models.OneToOneField(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='assinatura',
        help_text="Empresa que possui esta assinatura"
    )
    plano = models.ForeignKey(
        Plano,
        on_delete=models.PROTECT,
        related_name='assinaturas',
        help_text="Plano contratado"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='trial',
        help_text="Status atual da assinatura"
    )

    # Datas
    data_inicio = models.DateTimeField(
        auto_now_add=True,
        help_text="Data de criação da assinatura"
    )
    data_expiracao = models.DateTimeField(
        help_text="Data em que a assinatura expira (renova mensalmente)"
    )
    trial_ativo = models.BooleanField(
        default=True,
        help_text="Se está em período de trial"
    )
    ultimo_pagamento = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Data do último pagamento recebido"
    )
    proximo_vencimento = models.DateField(
        null=True,
        blank=True,
        help_text="Data do próximo vencimento"
    )

    # Integração com gateway de pagamento
    gateway = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('stripe', 'Stripe'),
            ('asaas', 'Asaas'),
            ('manual', 'Manual'),
        ],
        help_text="Gateway de pagamento utilizado"
    )
    subscription_id_externo = models.CharField(
        max_length=255,
        blank=True,
        help_text="ID da assinatura no gateway (Stripe/Asaas)"
    )
    customer_id_externo = models.CharField(
        max_length=255,
        blank=True,
        help_text="ID do cliente no gateway"
    )

    # Controle de cancelamento
    cancelada_em = models.DateTimeField(null=True, blank=True)
    motivo_cancelamento = models.TextField(blank=True)

    # Metadados para controle de notificações e outros dados
    metadados = models.JSONField(default=dict, blank=True)

    # Controle
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Assinatura'
        verbose_name_plural = 'Assinaturas'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.empresa.nome} - {self.plano.get_nome_display()} ({self.get_status_display()})"

    def renovar(self, dias=30):
        """
        Renova assinatura por X dias
        Chamado após confirmação de pagamento
        """
        self.data_expiracao = now() + timedelta(days=dias)
        self.ultimo_pagamento = now()
        self.status = 'ativa'
        self.trial_ativo = False
        self.proximo_vencimento = (now() + timedelta(days=dias)).date()
        self.save()

    def suspender(self, motivo=''):
        """Suspende assinatura por falta de pagamento"""
        self.status = 'suspensa'
        if motivo:
            self.motivo_cancelamento = motivo
        self.save()

    def cancelar(self, motivo=''):
        """Cancela permanentemente a assinatura"""
        self.status = 'cancelada'
        self.cancelada_em = now()
        if motivo:
            self.motivo_cancelamento = motivo
        self.save()

    def reativar(self):
        """Reativa assinatura suspensa (após pagamento)"""
        if self.status == 'suspensa':
            self.status = 'ativa'
            self.save()

    def verificar_expiracao(self):
        """
        Verifica se assinatura expirou e atualiza status
        Retorna True se ainda está válida
        """
        if self.status in ['cancelada']:
            return False

        if self.data_expiracao < now():
            if self.trial_ativo:
                self.status = 'expirada'
            else:
                self.status = 'suspensa'
            self.save()
            return False

        return True

    def dias_restantes(self):
        """Retorna quantidade de dias até expiração"""
        delta = self.data_expiracao - now()
        return max(0, delta.days)

    def esta_ativa(self):
        """Verifica se assinatura está ativa (trial ou paga)"""
        return self.verificar_expiracao() and self.status in ['trial', 'ativa']


class HistoricoPagamento(models.Model):
    """
    Registro de todos os pagamentos recebidos
    """
    STATUS_PAGAMENTO = [
        ('pendente', 'Pendente'),
        ('processando', 'Processando'),
        ('aprovado', 'Aprovado'),
        ('recusado', 'Recusado'),
        ('estornado', 'Estornado'),
        ('cancelado', 'Cancelado'),
    ]

    assinatura = models.ForeignKey(
        Assinatura,
        on_delete=models.CASCADE,
        related_name='historico_pagamentos'
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(max_length=20, choices=STATUS_PAGAMENTO)

    # Dados do gateway
    gateway = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=255, unique=True)
    payment_method = models.CharField(max_length=50, blank=True)  # credit_card, boleto, pix

    # Datas
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    data_vencimento = models.DateField(null=True, blank=True)

    # Metadados
    metadados = models.JSONField(default=dict, blank=True)
    webhook_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Histórico de Pagamento'
        verbose_name_plural = 'Histórico de Pagamentos'
        ordering = ['-data_criacao']

    def __str__(self):
        return f"{self.assinatura.empresa.nome} - R$ {self.valor} - {self.get_status_display()}"
