"""
Modelos para la app Inventory - Movimientos de inventario.
"""
from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import User
from products.models import Product
from .managers import InventoryTransactionManager
from .validators import validate_quantity_positive


class InventoryTransaction(models.Model):
    """Movimiento de inventario (Kárdex)."""
    
    class TransactionType(models.TextChoices):
        IN = 'in', 'Entrada (Compra/Proveedor)'
        OUT = 'out', 'Salida (Venta/Manual)'
        ADJUSTMENT = 'adjustment', 'Ajuste de Inventario'
        WASTE = 'waste', 'Merma / Dañado'
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='transactions',
        help_text="Producto"
    )
    transaction_type = models.CharField(
        max_length=15,
        choices=TransactionType.choices,
        help_text="Tipo de transacción"
    )
    quantity = models.PositiveIntegerField(
        validators=[validate_quantity_positive],
        help_text="Cantidad"
    )
    reason = models.CharField(
        max_length=255,
        blank=True,
        help_text="Razón del movimiento"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Usuario que realizó el movimiento"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = InventoryTransactionManager()
    
    class Meta:
        db_table = 'inventory_transaction'
        verbose_name = "Transacción de Inventario"
        verbose_name_plural = "Transacciones de Inventario"
        indexes = [
            models.Index(fields=['transaction_type', 'created_at']),
            models.Index(fields=['product']),
        ]
    
    def __str__(self) -> str:
        return f"{self.transaction_type} - {self.quantity} de {self.product.name}"


class InventoryMovement(models.Model):
    """Movimiento detallado de inventario."""
    
    class MovementType(models.TextChoices):
        SALE = 'sale', 'Venta'
        RESTOCK = 'restock', 'Reabastecimiento'
        ADJUST = 'adjust', 'Ajuste de Inventario'
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='movements',
        help_text="Producto"
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices,
        help_text="Tipo de movimiento"
    )
    quantity = models.PositiveIntegerField(
        validators=[validate_quantity_positive],
        help_text="Cantidad"
    )
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Costo unitario"
    )
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Costo total"
    )
    cash_shift = models.ForeignKey(
        'expenses.CashShift',
        on_delete=models.CASCADE,
        related_name='movements',
        help_text="Turno de caja"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Usuario"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Notas")
    
    class Meta:
        db_table = 'inventory_movement'
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        indexes = [
            models.Index(fields=['movement_type', 'created_at']),
            models.Index(fields=['product']),
        ]
    
    def __str__(self) -> str:
        return f"{self.movement_type} - {self.quantity} de {self.product.name}"
