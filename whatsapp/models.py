import uuid
from django.db import models
from django.conf import settings


class WhatsAppInstance(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('creating', 'Criando'),
        ('connected', 'Conectado'),
        ('disconnected', 'Desconectado'),
        ('error', 'Erro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='whatsapp_instances'
    )
    instance_name = models.CharField(max_length=100, unique=True)
    evolution_instance_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    webhook_token = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Instância WhatsApp"
        verbose_name_plural = "Instâncias WhatsApp"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.cliente.username} - {self.instance_name}"
