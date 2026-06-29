import uuid
from django.db import models

class GlobalProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    barcode = models.CharField(max_length=64, unique=True, help_text="Código de barras global")
    name = models.CharField(max_length=255, help_text="Nombre del producto")
    brand = models.CharField(max_length=255, blank=True, help_text="Marca del producto")
    category = models.CharField(max_length=255, blank=True, help_text="Categoría del producto")
    image_url = models.URLField(max_length=500, blank=True, help_text="URL de la imagen del producto")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'global_product'
        verbose_name = 'Producto Global'
        verbose_name_plural = 'Productos Globales'

    def __str__(self):
        return f"{self.barcode} - {self.name}"
