# Generated by Django 4.1.2 on 2022-12-29 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puf_server', '0003_framtests_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='framtests',
            name='name',
            field=models.CharField(default='Latency', max_length=50),
            preserve_default=False,
        ),
    ]
