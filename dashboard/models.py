from django.db import models

class Dashboard(models.Model):
    empresa = models.OneToOneField('empresas.Empresa', on_delete=models.CASCADE, related_name='dashboard')
    
    class Meta:
        verbose_name = 'Dashboard'
        verbose_name_plural = 'Dashboards'

    def __str__(self):
        return f"Dashboard - {self.empresa}"
