# Generated by Django 5.0.2 on 2024-05-22 11:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='priority',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('jenis', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='project',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('subject', models.CharField(max_length=50)),
                ('desc', models.TextField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='task',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('subject', models.CharField(max_length=50)),
                ('start_date', models.DateField()),
                ('due_date', models.DateField()),
                ('assignee', models.EmailField(max_length=254)),
                ('id_priority', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apps.priority')),
                ('id_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apps.project')),
            ],
        ),
        migrations.CreateModel(
            name='pic',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('pic', models.EmailField(max_length=254)),
                ('id_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apps.task')),
            ],
        ),
        migrations.CreateModel(
            name='feedback',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField()),
                ('id_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apps.task')),
            ],
        ),
    ]
