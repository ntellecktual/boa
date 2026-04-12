# Generated manually for FeatureFlag model

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('boaapp', '0013_db_storage_overhaul'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeatureFlag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='e.g., enable_job_match, enable_live_apis', max_length=100, unique=True)),
                ('is_enabled', models.BooleanField(default=True)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
