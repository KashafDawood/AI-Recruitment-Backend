from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("jobs", "0006_remove_joblisting_description_json_and_more"), 
    ]

    operations = [
        migrations.RunSQL("CREATE EXTENSION IF NOT EXISTS pg_trgm;"),
    ]
