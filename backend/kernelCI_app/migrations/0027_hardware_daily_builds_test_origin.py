from django.db import migrations, models


class Migration(migrations.Migration):
    atomic = False  # Required for `CONCURRENTLY`

    dependencies = [
        ("kernelCI_app", "0025_merge_20261023_1833"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name="hardwaredailybuilds",
                    name="test_origin",
                    field=models.CharField(max_length=100),
                ),
                migrations.AlterField(
                    model_name="hardwaredailybuilds",
                    name="pk",
                    field=models.CompositePrimaryKey(
                        "checkout_day",
                        "test_origin",
                        "build_origin",
                        "build_lab",
                        "platform",
                        "checkout_id",
                        blank=True,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE hardware_daily_builds
                            ADD COLUMN test_origin varchar(100) NOT NULL DEFAULT '';
                    """,
                    reverse_sql="""
                        ALTER TABLE hardware_daily_builds
                            DROP COLUMN test_origin;
                    """,
                ),
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE hardware_daily_builds
                            ALTER COLUMN test_origin DROP DEFAULT;
                    """,
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
        ),
        migrations.RunSQL(
            sql="""
                CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS
                    hardware_daily_builds_pkey_new
                ON hardware_daily_builds (
                    checkout_day,
                    test_origin,
                    build_origin,
                    build_lab,
                    platform,
                    checkout_id
                );
            """,
            reverse_sql="""
                DROP INDEX CONCURRENTLY IF EXISTS hardware_daily_builds_pkey_new;
            """,
        ),
        migrations.RunSQL(
            sql="""
                ALTER TABLE hardware_daily_builds
                    DROP CONSTRAINT hardware_daily_builds_pkey,
                    ADD CONSTRAINT hardware_daily_builds_pkey
                        PRIMARY KEY USING INDEX hardware_daily_builds_pkey_new;
            """,
            reverse_sql="""
                ALTER TABLE hardware_daily_builds
                    DROP CONSTRAINT hardware_daily_builds_pkey,
                    ADD CONSTRAINT hardware_daily_builds_pkey
                        PRIMARY KEY (
                            checkout_day,
                            build_origin,
                            build_lab,
                            platform,
                            checkout_id
                        );
            """,
        ),
    ]
