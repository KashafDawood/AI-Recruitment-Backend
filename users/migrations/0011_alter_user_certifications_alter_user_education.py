# Generated by Django 5.1.5 on 2025-02-12 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_user_certifications_user_education'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='certifications',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='user',
            name='education',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
