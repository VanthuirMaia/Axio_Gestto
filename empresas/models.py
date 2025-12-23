from django.db import models
from django.core.validators import MinValueValidator
from PIL import Image

class Empresa(models.Model):
    nome = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    descricao = models.TextField(blank=True)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    cor_primaria = models.CharField(max_length=7, default='#1e3a8a')
    cor_secundaria = models.CharField(max_length=7, default='#3b82f6')
    telefone = models.CharField(max_length=20)
    email = models.EmailField()
    endereco = models.TextField()
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=10)
    cnpj = models.CharField(max_length=20, unique=True)
    ativa = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['-criada_em']

    def __str__(self):
        return self.nome


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
