from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("kernelCI_app", "0020_add_labs_fk_indexes"),
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
