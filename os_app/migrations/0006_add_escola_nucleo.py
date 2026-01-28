# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('os_app', '0005_escolanucleo_bairro_alter_escola_bairro'),  # ← COLOQUE AQUI O NOME DO PASSO 3
    ]

    operations = [
        migrations.AddField(
            model_name='professor',
            name='escola_nucleo',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='os_app.escolanucleo',
                verbose_name='Escola Núcleo (caso não tenha dependente)',
                help_text='Use este campo se o professor está lotado direto no núcleo'
            ),
        ),
    ]