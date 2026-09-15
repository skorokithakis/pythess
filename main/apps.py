from django.apps import AppConfig
from django.contrib.auth.signals import user_logged_in


class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main"

    def ready(self) -> None:
        # Django stamps auth_user.last_login on every login, which dirtied db.sqlite3.
        # That file is committed, so each local login produced a pointless binary diff,
        # and nothing here reads the value. The column itself cannot go: it is declared
        # on AbstractBaseUser, and the ORM selects it on every User query, so dropping it
        # would need a custom user model. Cutting the receiver that writes it is enough.
        # Migration 0013 clears the timestamps that were already recorded.
        #
        # django.contrib.auth is listed before main in INSTALLED_APPS, so its ready() has
        # already connected the receiver by the time this runs. Passing dispatch_uid on
        # its own is what lets us avoid importing the receiver from auth.models, which is
        # not safe to import at module scope in an AppConfig.
        user_logged_in.disconnect(dispatch_uid="update_last_login")
