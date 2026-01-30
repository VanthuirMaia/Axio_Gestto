# Generated migration

from django.db import migrations, models


def atualizar_trial_dias(apps, schema_editor):
    """Atualiza trial_dias de 7 para 15 em todos os planos existentes"""
    Plano = apps.get_model('assinaturas', 'Plano')
    Plano.objects.filter(trial_dias=7).update(trial_dias=15)


def reverter_trial_dias(apps, schema_editor):
    """Reverte trial_dias de 15 para 7"""
    Plano = apps.get_model('assinaturas', 'Plano')
    Plano.objects.filter(trial_dias=15).update(trial_dias=7)


class Migration(migrations.Migration):

    dependencies = [
        ('assinaturas', '0004_adicionar_campo_whatsapp_bot'),
    ]

    operations = [
        # Alterar default do campo trial_dias
        migrations.AlterField(
            model_name='plano',
            name='trial_dias',
            field=models.IntegerField(
                default=15,
                validators=[],
                help_text='Dias de trial gratuito'
            ),
        ),
        # Adicionar campo metadados em Assinatura
        migrations.AddField(
            model_name='assinatura',
            name='metadados',
            field=models.JSONField(blank=True, default=dict),
        ),
        # Atualizar planos existentes
        migrations.RunPython(atualizar_trial_dias, reverter_trial_dias),
    ]
