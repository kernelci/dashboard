from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("kernelCI_app", "0028_regzbot_messages"),
    ]

    operations = [
        migrations.AddField(
            model_name="regzbotmessage",
            name="confirmed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
