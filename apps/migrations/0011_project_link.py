# Generated by Django 5.0.2 on 2024-05-28 01:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0010_settings_priority_column'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='link',
            field=models.URLField(blank=True, null=True),
        ),
    ]
