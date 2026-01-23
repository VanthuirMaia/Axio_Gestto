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
