# Generated by Django 4.1.2 on 2023-10-13 12:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0010_rowhammeringmeasurmenttestsmodel_hammeringiterations_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rowhammeringmeasurmenttestsmodel',
            old_name='initialValue_2',
            new_name='initialValue_1',
        ),
        migrations.RenameField(
            model_name='rowhammeringtestsmodel',
            old_name='initialValue_2',
            new_name='initialValue_1',
        ),
        migrations.RenameField(
            model_name='writelatencymeasurmenttestsmodel',
            old_name='initialValue_2',
            new_name='initialValue_1',
        ),
        migrations.RenameField(
            model_name='writelatencytestsmodel',
            old_name='initialValue_2',
            new_name='initialValue_1',
        ),
    ]
