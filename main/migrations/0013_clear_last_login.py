from django.db import migrations

# MainConfig.ready() disconnects the receiver that writes auth_user.last_login, so no new
# timestamps are recorded. This clears the ones already committed to db.sqlite3. The
# column stays, because it is declared on AbstractBaseUser and removing it would require
# a custom user model; it is nullable, so leaving it empty is valid.
#
# There is no reverse_sql, because the original timestamps are discarded and cannot be
# reconstructed. Reversing would also mean reconnecting the receiver in apps.py.
CLEAR_LAST_LOGIN = """
    UPDATE auth_user SET last_login = NULL;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0012_alter_person_gender"),
        # This migration reaches outside its own app to write to auth_user, and nothing
        # in main's chain requires the auth app, so without this the graph is free to run
        # main first and the UPDATE hits a table that does not exist yet. A full migrate
        # happens to order auth first today, but "migrate main" on a new database would
        # not. Depending on 0005 rather than auth's initial migration also pins the point
        # where last_login became nullable, which is what makes the UPDATE valid.
        ("auth", "0005_alter_user_last_login_null"),
    ]

    operations = [
        migrations.RunSQL(CLEAR_LAST_LOGIN),
    ]
