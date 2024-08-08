from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = _("Accounts")
    manage_reserved_roles = True

    def ready(self):
        """
        Import the signals module to ensure that the signals are registered.
        """
        import apps.accounts.signals
