import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("kernelCI_app", "0023_hardware_registry_sync"),
    ]

    operations = [
        migrations.AddField(
            model_name="hardwareregistryplatform",
            name="compatible",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(), blank=True, null=True, size=None
            ),
        ),
    ]
