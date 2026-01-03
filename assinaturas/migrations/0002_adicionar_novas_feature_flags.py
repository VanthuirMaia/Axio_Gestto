# Generated manually - Adicionar novas feature flags específicas
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assinaturas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='plano',
            name='permite_financeiro',
            field=models.BooleanField(default=False, help_text='Permite acesso ao módulo Financeiro completo'),
        ),
        migrations.AddField(
            model_name='plano',
            name='permite_dashboard_clientes',
            field=models.BooleanField(default=False, help_text='Permite acesso ao Dashboard de Clientes com métricas'),
        ),
        migrations.AddField(
            model_name='plano',
            name='permite_recorrencias',
            field=models.BooleanField(default=False, help_text='Permite criar agendamentos recorrentes'),
        ),
        migrations.AlterField(
            model_name='plano',
            name='permite_relatorios_avancados',
            field=models.BooleanField(default=False, help_text='DEPRECATED - usar permite_financeiro e permite_dashboard_clientes'),
        ),
        migrations.AlterField(
            model_name='plano',
            name='permite_integracao_contabil',
            field=models.BooleanField(default=False, help_text='DEPRECATED - funcionalidade não implementada'),
        ),
        migrations.AlterField(
            model_name='plano',
            name='permite_multi_unidades',
            field=models.BooleanField(default=False, help_text='DEPRECATED - funcionalidade não implementada'),
        ),
    ]
