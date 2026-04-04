"""
Modelos para la app Inventory - Movimientos de inventario (Kárdex).
ARCHITECTURE_V2: Auditoría completa de movimientos de stock.
"""
from django.db import models
import uuid


class InventoryMovement(models.Model):
    """Movimiento de inventario (Kárdex/Auditoría)."""
    
    class MovementType(models.TextChoices):
        SALE = 'sale', 'Venta'
        PURCHASE = 'purchase', 'Compra a Proveedor'
        ADJUSTMENT = 'adjustment', 'Ajuste de Inventario'
        RETURN = 'return', 'Devolución'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='inventory_movements'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='inventory_movements',
        help_text="Usuario que realizó el movimiento"
    )
    movement_type = models.CharField(
        max_length=15,
        choices=MovementType.choices,
        help_text="Tipo de movimiento"
    )
    quantity = models.IntegerField(
        help_text="Cantidad (negativo para salida, positivo para entrada)"
    )
    stock_before = models.PositiveIntegerField(
        help_text="Stock antes del movimiento"
    )
    stock_after = models.PositiveIntegerField(
        help_text="Stock exacto resultante después del movimiento"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inventory_movement'
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['movement_type', 'created_at']),
        ]
    
    def __str__(self) -> str:
        return f"{self.movement_type} - {self.product.name} ({self.quantity})"
