# Generated by Django 5.1.5 on 2025-03-10 01:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_candidateprofile_experience_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='address',
            field=models.TextField(blank=True, null=True),
        ),
    ]
