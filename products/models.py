"""
Modelos para la app Products - Productos, categorías y proveedores.
"""
from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import User
from .validators import validate_sku_format, validate_stock_not_negative, validate_positive_decimal
from .managers import ProductManager, SupplierManager


class Category(models.Model):
    """Categoría de productos."""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nombre único de la categoría"
    )
    
    class Meta:
        db_table = 'category'
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self) -> str:
        return self.name


class Supplier(models.Model):
    """Proveedor de productos."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Usuario asociado"
    )
    name = models.CharField(max_length=200, help_text="Nombre del proveedor")
    email = models.EmailField(blank=True, help_text="Email del proveedor")
    phone = models.CharField(max_length=20, blank=True, help_text="Teléfono")
    company = models.CharField(max_length=200, blank=True, help_text="Empresa")
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = SupplierManager()
    
    class Meta:
        db_table = 'supplier'
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self) -> str:
        return f"{self.name} ({self.company})" if self.company else self.name


class Product(models.Model):
    """Producto en el catálogo de inventario."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Usuario propietario"
    )
    name = models.CharField(max_length=250, help_text="Nombre del producto")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Categoría"
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Proveedor"
    )
    sku = models.CharField(
        max_length=50,
        validators=[validate_sku_format],
        help_text="SKU único"
    )
    stock = models.PositiveIntegerField(
        default=0,
        validators=[validate_stock_not_negative],
        help_text="Stock disponible"
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[validate_positive_decimal],
        help_text="Precio unitario"
    )
    image_url = models.URLField(
        max_length=800,
        blank=True,
        null=True,
        help_text="URL de imagen en Cloudinary"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ProductManager()
    
    class Meta:
        db_table = 'product'
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['user', 'category']),
            models.Index(fields=['stock']),
        ]
    
    def clean(self):
        """Validaciones de negocio."""
        from django.core.exceptions import ValidationError
        if self.stock < 0:
            raise ValidationError("El stock no puede ser negativo")
    
    @property
    def status(self) -> str:
        """Estado del producto basado en stock."""
        if self.stock == 0:
            return 'out_of_stock'
        if self.stock <= 10:
            return 'low_stock'
        return 'in_stock'
    
    def __str__(self) -> str:
        return f"{self.name} (SKU: {self.sku})"
