# Generated by Django 5.0.2 on 2024-05-25 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0009_alter_project_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='priority_column',
            field=models.IntegerField(default='62'),
        ),
    ]