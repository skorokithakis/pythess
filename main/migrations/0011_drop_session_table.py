from django.db import migrations

# Sessions moved to the local-memory cache, so the django_session table is dead weight.
# This lives in "main" rather than in the sessions app because "django.contrib.sessions"
# is no longer in INSTALLED_APPS, which leaves it with nowhere to put a migration of its
# own and leaves its django_migrations rows behind as stale records.
#
# IF EXISTS is required rather than merely cautious: on a fresh database the sessions app
# is already absent from INSTALLED_APPS, so the table is never created in the first place
# and an unguarded DROP would abort the initial migrate.
#
# There is no reverse_sql, so this migration is deliberately irreversible. Reversing it
# would have to recreate a table that nothing reads, and restoring database-backed
# sessions means putting the app back in INSTALLED_APPS anyway.
DROP_SESSION_TABLE = """
    DROP TABLE IF EXISTS django_session;
    DELETE FROM django_migrations WHERE app = 'sessions';
"""


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0010_person_bio"),
    ]

    operations = [
        migrations.RunSQL(DROP_SESSION_TABLE),
    ]
