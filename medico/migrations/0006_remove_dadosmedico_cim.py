# Generated by Django 5.0.4 on 2024-04-21 10:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("medico", "0005_alter_datasabertas_data"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="dadosmedico",
            name="cim",
        ),
    ]
