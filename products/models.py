"""
Modelos para la app Products - Catálogo, categorías, proveedores y empaques.
ARCHITECTURE_V2: Estructura completa de productos multi-tienda.
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class Category(models.Model):
    """Categoría de productos dentro de una tienda."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(
        'accounts.Store',
        on_delete=models.CASCADE,
        related_name='categories'
    )
    name = models.CharField(max_length=100, help_text="Nombre de la categoría")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'category'
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        unique_together = [['store', 'name']]
        indexes = [
            models.Index(fields=['store']),
        ]
    
    def __str__(self) -> str:
        return self.name


class Supplier(models.Model):
    """Proveedor de productos."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(
        'accounts.Store',
        on_delete=models.CASCADE,
        related_name='suppliers'
    )
    name = models.CharField(max_length=200, help_text="Nombre del proveedor")
    contact_info = models.CharField(
        max_length=255,
        blank=True,
        help_text="Teléfono, email o datos de contacto"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'supplier'
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        indexes = [
            models.Index(fields=['store']),
        ]
    
    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    """Producto del catálogo."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(
        'accounts.Store',
        on_delete=models.CASCADE,
        related_name='products'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    name = models.CharField(max_length=250, help_text="Nombre del producto")
    base_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Costo base para el dueño"
    )
    sale_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Precio de venta al público"
    )
    current_stock = models.PositiveIntegerField(
        default=0,
        help_text="Stock disponible actual"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product'
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        indexes = [
            models.Index(fields=['store']),
            models.Index(fields=['category']),
            models.Index(fields=['supplier']),
        ]
    
    def __str__(self) -> str:
        return self.name


class ProductPackaging(models.Model):
    """Formato de empaque para un producto."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='packagings'
    )
    name = models.CharField(
        max_length=100,
        help_text="Nombre del empaque (Ej: Caja con 50)"
    )
    quantity_per_unit = models.PositiveIntegerField(
        help_text="Cantidad de unidades en este empaque"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_packaging'
        verbose_name = "Empaque de producto"
        verbose_name_plural = "Empaques de producto"
    
    def __str__(self) -> str:
        return f"{self.product.name} - {self.name}"


class ProductCode(models.Model):
    """Código (QR, Código de barras, EAN) asociado a un producto."""
    
    class CodeType(models.TextChoices):
        EAN13 = 'ean13', 'EAN13'
        QR = 'qr', 'QR'
        UPC = 'upc', 'UPC'
        SHELF_LABEL = 'shelf_label', 'Etiqueta de Estante'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='codes'
    )
    code = models.CharField(
        max_length=100,
        help_text="Valor del código (para QR o barras)"
    )
    code_type = models.CharField(
        max_length=15,
        choices=CodeType.choices,
        help_text="Tipo de código"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_code'
        verbose_name = "Código de producto"
        verbose_name_plural = "Códigos de producto"
        unique_together = [['product', 'code']]
    
    def __str__(self) -> str:
        return f"{self.product.name} - {self.code_type}: {self.code}"
