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

