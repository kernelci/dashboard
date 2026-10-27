import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("kernelCI_app", "0025_merge_20261023_1833")]

    operations = [
        migrations.AlterField(
            model_name="commitmessage",
            name="commit",
            field=models.ForeignKey(
                db_column="commit_id",
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                related_name="message_row",
                serialize=False,
                to="kernelCI_app.commits",
            ),
        ),
        migrations.RemoveField(model_name="commits", name="fetched_from_url"),
    ]
