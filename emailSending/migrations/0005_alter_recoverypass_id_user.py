# Generated by Django 5.1.1 on 2024-10-11 03:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_alter_flow_price'),
        ('emailSending', '0004_alter_recoverypass_id_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recoverypass',
            name='id_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.user'),
        ),
    ]
