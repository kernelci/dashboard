import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("kernelCI_app", "0019_labs_builds_lab_tests_lab"),
    ]

    operations = [
        migrations.RenameField(
            model_name="builds",
            old_name="lab",
            new_name="lab_id",
        ),
        migrations.RenameField(
            model_name="tests",
            old_name="lab",
            new_name="lab_id",
        ),
        migrations.AlterField(
            model_name="builds",
            name="lab_id",
            field=models.ForeignKey(
                db_column="lab_id",
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="kernelCI_app.labs",
            ),
        ),
        migrations.AlterField(
            model_name="tests",
            name="lab_id",
            field=models.ForeignKey(
                db_column="lab_id",
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="kernelCI_app.labs",
            ),
        ),
    ]
