# Generated by Django 4.1.2 on 2023-01-15 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puf_server', '0007_rename_temperture_tests_temperature'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tests',
            name='type',
            field=models.CharField(default='default test', max_length=100),
        ),
    ]
