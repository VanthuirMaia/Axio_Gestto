from django.db import models
from django.core.validators import MinValueValidator


class StatusAgendamento(models.TextChoices):
    PENDENTE = 'pendente', 'Pendente'
    CONFIRMADO = 'confirmado', 'Confirmado'
    CANCELADO = 'cancelado', 'Cancelado'
    CONCLUIDO = 'concluido', 'Concluído'
    NAO_COMPARECEU = 'nao_compareceu', 'Não Compareceu'

class Agendamento(models.Model):
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, related_name='agendamentos')
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE, related_name='agendamentos')
    servico = models.ForeignKey('empresas.Servico', on_delete=models.SET_NULL, null=True, related_name='agendamentos')
    profissional = models.ForeignKey('empresas.Profissional', on_delete=models.SET_NULL, null=True, blank=True, related_name='agendamentos')
    
    data_hora_inicio = models.DateTimeField()
    data_hora_fim = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=StatusAgendamento.choices,
        default=StatusAgendamento.PENDENTE
    )
    
    notas = models.TextField(blank=True)
    valor_cobrado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        ordering = ['-data_hora_inicio']

    def __str__(self):
        return f"{self.cliente} - {self.servico} ({self.data_hora_inicio})"


class DisponibilidadeProfissional(models.Model):
    DIAS_SEMANA = [
        (0, 'Segunda'),
        (1, 'Terca'),
        (2, 'Quarta'),
        (3, 'Quinta'),
        (4, 'Sexta'),
        (5, 'Sabado'),
        (6, 'Domingo'),
    ]

    profissional = models.ForeignKey('empresas.Profissional', on_delete=models.CASCADE, related_name='disponibilidades')
    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Disponibilidade Profissional'
        verbose_name_plural = 'Disponibilidades Profissionais'
        unique_together = ('profissional', 'dia_semana', 'hora_inicio', 'hora_fim')

    def __str__(self):
        return f"{self.profissional} - {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fim}"


class LogMensagemBot(models.Model):
    """
    Registra todas as interações do bot WhatsApp
    Usado para auditoria e debugging
    """
    TIPO_ACAO = [
        ('agendar', 'Agendar'),
        ('cancelar', 'Cancelar'),
        ('reagendar', 'Reagendar'),
        ('consultar', 'Consultar'),
        ('confirmar', 'Confirmar'),
        ('outro', 'Outro'),
    ]

    STATUS_PROCESSAMENTO = [
        ('sucesso', 'Sucesso'),
        ('erro', 'Erro'),
        ('parcial', 'Parcial'),
    ]

    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, related_name='logs_bot')
    telefone = models.CharField(max_length=20, help_text='Telefone do cliente que enviou')
    mensagem_original = models.TextField(help_text='Mensagem original do WhatsApp')
    intencao_detectada = models.CharField(max_length=20, choices=TIPO_ACAO)
    dados_extraidos = models.JSONField(help_text='Dados extraídos pela IA', default=dict)

    agendamento = models.ForeignKey(
        Agendamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Agendamento criado/modificado'
    )

    status = models.CharField(max_length=20, choices=STATUS_PROCESSAMENTO)
    resposta_enviada = models.TextField(help_text='Resposta enviada ao cliente')
    erro_detalhes = models.TextField(blank=True, help_text='Detalhes do erro se houver')

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Log de Mensagem do Bot'
        verbose_name_plural = 'Logs de Mensagens do Bot'
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['telefone', '-criado_em']),
            models.Index(fields=['empresa', 'intencao_detectada']),
        ]

    def __str__(self):
        return f"{self.telefone} - {self.intencao_detectada} ({self.criado_em.strftime('%d/%m/%Y %H:%M')})"


class AgendamentoRecorrente(models.Model):
    """
    Agendamentos que se repetem automaticamente
    Ex: "Toda segunda às 10h", "Todo dia 15 às 14h"
    """
    FREQUENCIA_CHOICES = [
        ('diaria', 'Diária'),
        ('semanal', 'Semanal'),
        ('mensal', 'Mensal'),
    ]

    DIAS_SEMANA_CHOICES = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, related_name='agendamentos_recorrentes')
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE, related_name='agendamentos_recorrentes')
    servico = models.ForeignKey('empresas.Servico', on_delete=models.CASCADE, related_name='agendamentos_recorrentes')
    profissional = models.ForeignKey('empresas.Profissional', on_delete=models.SET_NULL, null=True, blank=True, related_name='agendamentos_recorrentes')

    # Recorrência
    frequencia = models.CharField(
        max_length=20,
        choices=FREQUENCIA_CHOICES,
        help_text='Com que frequência o agendamento se repete'
    )
    dias_semana = models.JSONField(
        default=list,
        help_text='Lista de dias da semana (0=seg, 6=dom). Ex: [0,2,4] = seg/qua/sex'
    )
    dia_mes = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text='Para recorrência mensal: dia do mês (1-31)'
    )
    hora_inicio = models.TimeField(help_text='Horário do agendamento')

    # Período de validade
    data_inicio = models.DateField(help_text='A partir de quando gerar os agendamentos')
    data_fim = models.DateField(
        null=True,
        blank=True,
        help_text='Até quando gerar (deixe vazio para infinito)'
    )

    # Status
    ativo = models.BooleanField(
        default=True,
        help_text='Se False, para de gerar novos agendamentos'
    )

    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(
        'core.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorrencias_criadas'
    )

    class Meta:
        verbose_name = 'Agendamento Recorrente'
        verbose_name_plural = 'Agendamentos Recorrentes'
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['empresa', 'ativo']),
            models.Index(fields=['data_inicio', 'data_fim']),
        ]

    def __str__(self):
        freq = self.get_frequencia_display()
        if self.frequencia == 'semanal' and self.dias_semana:
            dias = ', '.join([self.DIAS_SEMANA_CHOICES[d][1] for d in self.dias_semana])
            return f"{self.cliente} - {self.servico} ({freq}: {dias} às {self.hora_inicio})"
        elif self.frequencia == 'mensal':
            return f"{self.cliente} - {self.servico} ({freq}: dia {self.dia_mes} às {self.hora_inicio})"
        return f"{self.cliente} - {self.servico} ({freq} às {self.hora_inicio})"

    def get_descricao_frequencia(self):
        """Retorna descrição legível da recorrência"""
        if self.frequencia == 'diaria':
            return f"Todos os dias às {self.hora_inicio.strftime('%H:%M')}"

        elif self.frequencia == 'semanal':
            if not self.dias_semana:
                return "Semanal (sem dias definidos)"
            dias_nomes = [self.DIAS_SEMANA_CHOICES[d][1] for d in sorted(self.dias_semana)]
            if len(dias_nomes) == 1:
                return f"Toda {dias_nomes[0]} às {self.hora_inicio.strftime('%H:%M')}"
            return f"Toda {', '.join(dias_nomes)} às {self.hora_inicio.strftime('%H:%M')}"

        elif self.frequencia == 'mensal':
            return f"Todo dia {self.dia_mes} do mês às {self.hora_inicio.strftime('%H:%M')}"

        return "Recorrência não definida"

