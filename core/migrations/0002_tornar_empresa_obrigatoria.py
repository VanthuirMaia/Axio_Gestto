# Generated manually - Torna o campo empresa obrigatório

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('empresas', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='empresa',
            field=models.ForeignKey(
                help_text='Empresa à qual o usuário está vinculado (obrigatório)',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='usuarios',
                to='empresas.empresa'
            ),
        ),
    ]
