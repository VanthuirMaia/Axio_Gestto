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
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profissional'
        verbose_name_plural = 'Profissionais'
        ordering = ['nome']
        unique_together = ('empresa', 'email')

    def __str__(self):
        return f"{self.nome} - {self.empresa}"
