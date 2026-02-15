from django.db import models
from django.utils import timezone


class PageView(models.Model):
    """Registra visualizações de páginas da landing"""
    page_url = models.CharField(max_length=500, verbose_name="URL da Página")
    referrer = models.CharField(max_length=500, blank=True, verbose_name="Referenciador")
    user_agent = models.TextField(verbose_name="User Agent")
    ip_address = models.GenericIPAddressField(verbose_name="Endereço IP")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Data/Hora")
    session_id = models.CharField(max_length=100, blank=True, verbose_name="ID da Sessão")
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Visualização de Página"
        verbose_name_plural = "Visualizações de Páginas"
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['page_url']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"{self.page_url} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"


class UserEvent(models.Model):
    """Registra eventos de interação do usuário na landing"""
    EVENT_TYPES = [
        ('click_cta', 'Clique em CTA'),
        ('section_view', 'Visualização de Seção'),
        ('faq_open', 'Abertura de FAQ'),
        ('scroll_depth', 'Profundidade de Scroll'),
        ('time_on_section', 'Tempo em Seção'),
        ('plan_click', 'Clique em Plano'),
        ('whatsapp_click', 'Clique no WhatsApp'),
        ('contact_click', 'Clique em Contato'),
        ('menu_click', 'Clique no Menu'),
    ]
    
    event_type = models.CharField(
        max_length=50, 
        choices=EVENT_TYPES,
        verbose_name="Tipo de Evento"
    )
    event_data = models.JSONField(
        default=dict,
        verbose_name="Dados do Evento"
    )  # Dados adicionais do evento
    page_url = models.CharField(max_length=500, verbose_name="URL da Página")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Data/Hora")
    session_id = models.CharField(max_length=100, blank=True, verbose_name="ID da Sessão")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Endereço IP")
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Evento de Usuário"
        verbose_name_plural = "Eventos de Usuários"
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['event_type']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"


class Waitlist(models.Model):
    """Leads que entraram na lista de espera"""
    nome = models.CharField(max_length=200, verbose_name="Nome Completo")
    email = models.EmailField(unique=True, verbose_name="Email")
    whatsapp = models.CharField(max_length=20, verbose_name="WhatsApp")
    nome_negocio = models.CharField(max_length=200, verbose_name="Nome do Negócio")
    cidade = models.CharField(max_length=100, blank=True, verbose_name="Cidade")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    notificado = models.BooleanField(default=False, verbose_name="Já foi notificado?")
    notas = models.TextField(blank=True, verbose_name="Notas Internas")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Lead da Lista de Espera"
        verbose_name_plural = "Lista de Espera"
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['email']),
            models.Index(fields=['notificado']),
        ]
    
    def __str__(self):
        return f"{self.nome} ({self.email}) - {self.created_at.strftime('%d/%m/%Y')}"
