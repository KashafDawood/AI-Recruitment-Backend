# Generated by Django 5.1.5 on 2025-03-28 04:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0008_joblisting_applicants'),
    ]

    operations = [
        migrations.AddField(
            model_name='joblisting',
            name='experience_level',
            field=models.CharField(blank=True, choices=[('entry', 'Entry Level'), ('mid', 'Mid Level'), ('senior', 'Senior Level'), ('executive', 'Executive Level')], default='entry', max_length=20, null=True),
        ),
    ]
