from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("kernelCI_app", "0022_lab_daily"),
    ]

    operations = [
        migrations.CreateModel(
            name="HardwareRegistrySync",
            fields=[
                (
                    "id",
                    models.PositiveSmallIntegerField(primary_key=True, serialize=False),
                ),
                ("synced_at", models.DateTimeField()),
                ("files", models.JSONField(default=list)),
            ],
            options={
                "db_table": "hardware_registry_sync",
            },
        ),
    ]
