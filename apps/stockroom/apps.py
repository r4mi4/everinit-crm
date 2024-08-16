from django.apps import AppConfig


class StockroomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.stockroom'
    verbose_name = ' انبار'

    def ready(self):
        import apps.stockroom.signals
