from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("kernelCI_cache", "0005_checkoutscache_origin_finish_time"),
    ]

    operations = [
        migrations.DeleteModel(
            name="CheckoutsCache",
        ),
    ]
