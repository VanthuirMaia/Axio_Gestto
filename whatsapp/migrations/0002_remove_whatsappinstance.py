# Generated manually to remove duplicate WhatsAppInstance model

from django.db import migrations


class Migration(migrations.Migration):
    """
    Remove a tabela whatsapp_whatsappinstance que estava incorretamente
    vinculada a User. O modelo correto agora está em empresas.models
    vinculado a Empresa.
    """

    dependencies = [
        ('whatsapp', '0001_initial'),
        ('empresas', '0007_add_whatsappinstance'),  # Garante que a nova tabela existe
    ]

    operations = [
        migrations.DeleteModel(
            name='WhatsAppInstance',
        ),
    ]
