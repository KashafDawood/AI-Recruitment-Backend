# Generated by Django 5.1.5 on 2025-02-12 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_alter_employerprofile_logo_alter_user_photo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidateprofile',
            name='resume',
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='resumes',
            field=models.JSONField(default=dict),
        ),
    ]
