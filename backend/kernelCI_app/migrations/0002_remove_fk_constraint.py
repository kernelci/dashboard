import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("kernelCI_app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="builds",
            name="checkout",
            field=models.ForeignKey(
                db_constraint=False,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="kernelCI_app.checkouts",
            ),
        ),
        migrations.AlterField(
            model_name="incidents",
            name="issue",
            field=models.ForeignKey(
                db_constraint=False,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="kernelCI_app.issues",
            ),
        ),
        # The test and build keys for incidents *can* be null since an issue is not always
        # related to both objects (currently none are, but theoretically they could be)
        migrations.AlterField(
            model_name="incidents",
            name="build",
            field=models.ForeignKey(
                blank=True,
                null=True,
                db_constraint=False,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="kernelCI_app.builds",
            ),
        ),
        migrations.AlterField(
            model_name="incidents",
            name="test",
            field=models.ForeignKey(
                blank=True,
                null=True,
                db_constraint=False,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="kernelCI_app.tests",
            ),
        ),
        migrations.AlterField(
            model_name="tests",
            name="build",
            field=models.ForeignKey(
                db_constraint=False,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="kernelCI_app.builds",
            ),
        ),
    ]
