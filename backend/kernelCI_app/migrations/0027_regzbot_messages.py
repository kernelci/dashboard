from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("kernelCI_app", "0025_merge_20261023_1833"),
    ]

    operations = [
        migrations.CreateModel(
            name="RegzbotMessage",
            fields=[
                (
                    "issue_id",
                    models.TextField(primary_key=True, serialize=False),
                ),
                ("message_id", models.TextField()),
            ],
            options={
                "db_table": "regzbot_messages",
            },
        ),
    ]
