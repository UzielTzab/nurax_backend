from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.products'
    verbose_name = 'Productos y Catálogo'

    def ready(self):
        import apps.products.signals  # noqa: F401 — registra los receivers
