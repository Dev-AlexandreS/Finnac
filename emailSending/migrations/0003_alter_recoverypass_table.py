# Generated by Django 5.1.1 on 2024-10-11 03:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emailSending', '0002_alter_recoverypass_id_user'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='recoverypass',
            table='recoverypass',
        ),
    ]
