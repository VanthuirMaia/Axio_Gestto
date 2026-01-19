from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from PIL import Image
import secrets

class Empresa(models.Model):
    # Dados básicos
    nome = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    descricao = models.TextField(blank=True)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    cor_primaria = models.CharField(max_length=7, default='#1e3a8a')
    cor_secundaria = models.CharField(max_length=7, default='#3b82f6')

    # Contato
    telefone = models.CharField(max_length=20)
    email = models.EmailField()

    # Endereço
    endereco = models.TextField(blank=True)  # Tornando opcional para onboarding
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    cep = models.CharField(max_length=10, blank=True)
    google_maps_link = models.URLField(
        max_length=500,
        blank=True,
        help_text="Link do Google Maps para localização da empresa"
    )
    cnpj = models.CharField(max_length=20, unique=True)

    # Controle
    ativa = models.BooleanField(default=True)
    is_demo = models.BooleanField(
        default=False,
        help_text="Empresa de demonstração - não aparece nas métricas do Backoffice"
    )

    # ====== NOVOS CAMPOS PARA SaaS ======

    # Onboarding
    onboarding_completo = models.BooleanField(
        default=False,
        help_text="Se a empresa completou o wizard de configuração inicial"
    )
    onboarding_etapa = models.IntegerField(
        default=0,
        help_text="Etapa atual do onboarding (0-4)"
    )

    # WhatsApp / Integração
    whatsapp_numero = models.CharField(
        max_length=20,
        blank=True,
        help_text="Número WhatsApp conectado (com código do país)"
    )
    whatsapp_token = models.CharField(
        max_length=255,
        blank=True,
        help_text="Token da Evolution API / Z-API"
    )
    whatsapp_instance_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="ID da instância no provedor WhatsApp"
    )
    whatsapp_conectado = models.BooleanField(
        default=False,
        help_text="Se WhatsApp está conectado e funcionando"
    )

    # Metadados
    origem_cadastro = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('manual', 'Cadastro Manual'),
            ('checkout', 'Checkout Automático'),
            ('indicacao', 'Indicação'),
        ],
        default='checkout'
    )

    # Timestamps
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['-criada_em']

    def __str__(self):
        return self.nome

    @property
    def assinatura_ativa(self):
        """
        Retorna a assinatura da empresa apenas se estiver ativa (trial ou ativa).
        Usado para verificar permissões por plano.
        """
        try:
            assinatura = self.assinatura
            if assinatura and assinatura.esta_ativa():
                return assinatura
        except Exception:
            pass
        return None


class Servico(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='servicos')
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    duracao_minutos = models.IntegerField(validators=[MinValueValidator(1)])
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Servico'
        verbose_name_plural = 'Servicos'
        ordering = ['nome']
        unique_together = ('empresa', 'nome')

    def __str__(self):
        return f"{self.nome} - {self.empresa}"


class Profissional(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='profissionais')
    nome = models.CharField(max_length=255)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    servicos = models.ManyToManyField(Servico, related_name='profissionais')
    comissao_percentual = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    ativo = models.BooleanField(default=True)

    # 👉 COR DO PROFISSIONAL PARA APARECER NO CALENDÁRIO
    cor_hex = models.CharField(
        max_length=7,
        default="#1e3a8a",
        help_text="Cor dos eventos deste profissional no calendário (ex: #3b82f6)"
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profissional'
        verbose_name_plural = 'Profissionais'
        ordering = ['nome']
        unique_together = ('empresa', 'email')

    def __str__(self):
        return f"{self.nome} - {self.empresa}"


class HorarioFuncionamento(models.Model):
    """
    Horários de funcionamento da empresa por dia da semana
    """
    DIAS_SEMANA = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='horarios_funcionamento')
    dia_semana = models.IntegerField(choices=DIAS_SEMANA, help_text="0=Segunda, 6=Domingo")
    hora_abertura = models.TimeField(help_text="Horário de abertura")
    hora_fechamento = models.TimeField(help_text="Horário de fechamento")

    # Intervalo (ex: almoço)
    intervalo_inicio = models.TimeField(null=True, blank=True, help_text="Início do intervalo (opcional)")
    intervalo_fim = models.TimeField(null=True, blank=True, help_text="Fim do intervalo (opcional)")

    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Horário de Funcionamento'
        verbose_name_plural = 'Horários de Funcionamento'
        ordering = ['empresa', 'dia_semana']
        unique_together = ('empresa', 'dia_semana')

    def __str__(self):
        return f"{self.empresa.nome} - {self.get_dia_semana_display()}: {self.hora_abertura.strftime('%H:%M')} às {self.hora_fechamento.strftime('%H:%M')}"


class DataEspecial(models.Model):
    """
    Datas especiais: feriados (fechado) ou horários diferenciados
    """
    TIPO_CHOICES = [
        ('feriado', 'Feriado - Fechado'),
        ('especial', 'Horário Especial'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='datas_especiais')
    data = models.DateField(help_text="Data do feriado ou horário especial")
    descricao = models.CharField(max_length=200, help_text="Ex: Natal, Ano Novo, Carnaval")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='feriado')

    # Só preencher se tipo='especial'
    hora_abertura = models.TimeField(null=True, blank=True, help_text="Horário de abertura (se horário especial)")
    hora_fechamento = models.TimeField(null=True, blank=True, help_text="Horário de fechamento (se horário especial)")

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Data Especial'
        verbose_name_plural = 'Datas Especiais'
        ordering = ['empresa', 'data']
        unique_together = ('empresa', 'data')

    def __str__(self):
        if self.tipo == 'feriado':
            return f"{self.empresa.nome} - {self.data.strftime('%d/%m/%Y')} - {self.descricao} (FECHADO)"
        else:
            return f"{self.empresa.nome} - {self.data.strftime('%d/%m/%Y')} - {self.descricao} ({self.hora_abertura.strftime('%H:%M')} às {self.hora_fechamento.strftime('%H:%M')})"


class ConfiguracaoWhatsApp(models.Model):
    """
    Configuração completa de integração com Evolution API
    OneToOne com Empresa
    """
    STATUS_CHOICES = [
        ('nao_configurado', 'Não Configurado'),
        ('aguardando_qr', 'Aguardando QR Code'),
        ('conectando', 'Conectando'),
        ('conectado', 'Conectado'),
        ('desconectado', 'Desconectado'),
        ('erro', 'Erro na Conexão'),
    ]

    empresa = models.OneToOneField(
        Empresa,
        on_delete=models.CASCADE,
        related_name='config_whatsapp',
        help_text="Empresa dona desta configuração"
    )

    # Configuração da Evolution API
    evolution_api_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="URL base da Evolution API (ex: https://evolution.seuservidor.com)"
    )
    evolution_api_key = models.CharField(
        max_length=255,
        blank=True,
        help_text="API Key global da Evolution API"
    )

    # Instância
    instance_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Nome único da instância (slug da empresa ou personalizado)"
    )
    instance_token = models.CharField(
        max_length=255,
        blank=True,
        help_text="Token específico da instância (gerado pela Evolution)"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='nao_configurado',
        help_text="Status atual da conexão WhatsApp"
    )

    # QR Code
    qr_code = models.TextField(
        blank=True,
        help_text="QR Code em base64 para conectar WhatsApp"
    )
    qr_code_expira_em = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Data de expiração do QR Code"
    )

    # Webhook
    webhook_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="URL do webhook configurado na Evolution API"
    )
    webhook_secret = models.CharField(
        max_length=255,
        blank=True,
        help_text="Secret para validar webhooks recebidos"
    )

    # Dados da conexão
    numero_conectado = models.CharField(
        max_length=20,
        blank=True,
        help_text="Número WhatsApp conectado (com DDI)"
    )
    nome_perfil = models.CharField(
        max_length=255,
        blank=True,
        help_text="Nome do perfil WhatsApp conectado"
    )
    foto_perfil_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="URL da foto de perfil do WhatsApp"
    )

    # Controle
    ativo = models.BooleanField(
        default=True,
        help_text="Se a integração está ativa"
    )
    ultima_sincronizacao = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Última vez que sincronizou status com Evolution API"
    )
    ultimo_erro = models.TextField(
        blank=True,
        help_text="Último erro ocorrido na integração"
    )

    # Metadados
    metadados = models.JSONField(
        default=dict,
        blank=True,
        help_text="Dados extras da Evolution API"
    )

    # Timestamps
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuração WhatsApp'
        verbose_name_plural = 'Configurações WhatsApp'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.empresa.nome} - {self.get_status_display()}"

    def gerar_webhook_secret(self):
        """Gera um secret aleatório para validar webhooks"""
        if not self.webhook_secret:
            self.webhook_secret = secrets.token_urlsafe(32)
            self.save()
        return self.webhook_secret

    def gerar_instance_name(self):
        """Gera nome da instância baseado no slug da empresa"""
        if not self.instance_name:
            # Remove caracteres especiais e usa slug da empresa
            self.instance_name = f"{self.empresa.slug}_{self.empresa.id}"
            self.save()
        return self.instance_name

    def esta_conectado(self):
        """Verifica se WhatsApp está conectado"""
        return self.status == 'conectado'

class WhatsAppInstance(models.Model):
    """
    Registra as instâncias do WhatsApp criadas via Evolution API.
    Cada empresa pode ter 1 ou N instâncias.
    """
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, related_name="whatsapp_instances")
    instance_name = models.CharField(max_length=255, unique=True)
    evolution_instance_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, default="pending")
    webhook_token = models.CharField(max_length=255, blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Instância WhatsApp"
        verbose_name_plural = "Instâncias WhatsApp"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.empresa.nome} ({self.instance_name})"
