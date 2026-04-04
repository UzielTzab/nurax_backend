"""
Modelos para la app Expenses - Caja, gastos y compras a proveedores.
ARCHITECTURE_V2: Control completo de flujo de efectivo y compras.
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class CashShift(models.Model):
    """Turno de caja."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(
        'accounts.Store',
        on_delete=models.CASCADE,
        related_name='cash_shifts'
    )
    opened_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='opened_cash_shifts',
        help_text="Usuario que abrió la caja"
    )
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="NULL si el turno sigue abierto"
    )
    starting_cash = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Fondo de caja inicial"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cash_shift'
        verbose_name = "Turno de Caja"
        verbose_name_plural = "Turnos de Caja"
        indexes = [
            models.Index(fields=['store']),
            models.Index(fields=['opened_at']),
        ]
    
    @property
    def is_open(self) -> bool:
        """Indica si el turno está abierto."""
        return self.closed_at is None
    
    def __str__(self) -> str:
        status = "Abierto" if self.is_open else "Cerrado"
        return f"Turno {status} - {self.opened_at.strftime('%Y-%m-%d %H:%M')}"


class CashMovement(models.Model):
    """Movimiento de efectivo dentro de un turno."""
    
    class MovementType(models.TextChoices):
        IN = 'in', 'Entrada (IN)'
        OUT = 'out', 'Salida (OUT)'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cash_shift = models.ForeignKey(
        CashShift,
        on_delete=models.CASCADE,
        related_name='movements'
    )
    movement_type = models.CharField(
        max_length=5,
        choices=MovementType.choices,
        help_text="IN (Entrada) / OUT (Salida)"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Monto"
    )
    reason = models.CharField(
        max_length=255,
        help_text="Razón (Ej: Venta #10, Pago internet)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cash_movement'
        verbose_name = "Movimiento de Caja"
        verbose_name_plural = "Movimientos de Caja"
        indexes = [
            models.Index(fields=['cash_shift']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self) -> str:
        return f"{self.movement_type} - ${self.amount} - {self.reason}"


class ExpenseCategory(models.Model):
    """Categoría de gastos operativos."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(
        'accounts.Store',
        on_delete=models.CASCADE,
        related_name='expense_categories'
    )
    name = models.CharField(
        max_length=100,
        help_text="Nombre de la categoría (Ej: Servicios, Nómina, Compras)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'expense_category'
        verbose_name = "Categoría de Gasto"
        verbose_name_plural = "Categorías de Gasto"
        unique_together = [['store', 'name']]
    
    def __str__(self) -> str:
        return self.name


class Expense(models.Model):
    """Gasto operativo."""
    
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'Efectivo'
        TRANSFER = 'transfer', 'Transferencia'
        CARD = 'card', 'Tarjeta'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(
        'accounts.Store',
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='expenses'
    )
    cash_shift = models.ForeignKey(
        CashShift,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses',
        help_text="Opcional: Nulo si se pagó por banco"
    )
    purchase_order = models.ForeignKey(
        'PurchaseOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses',
        help_text="Opcional: Si es gasto de mercancía"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Monto del gasto"
    )
    description = models.CharField(max_length=255)
    payment_method = models.CharField(
        max_length=15,
        choices=PaymentMethod.choices,
        help_text="Método de pago: CASH, TRANSFER, CARD"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'expense'
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"
        indexes = [
            models.Index(fields=['store']),
            models.Index(fields=['category']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self) -> str:
        return f"{self.category.name} - ${self.amount}"


class PurchaseOrder(models.Model):
    """Orden de compra a proveedores."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        RECEIVED = 'received', 'Recibida'
        CANCELLED = 'cancelled', 'Cancelada'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(
        'accounts.Store',
        on_delete=models.CASCADE,
        related_name='purchase_orders'
    )
    supplier = models.ForeignKey(
        'products.Supplier',
        on_delete=models.PROTECT,
        related_name='purchase_orders'
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Estado: PENDING, RECEIVED, CANCELLED"
    )
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Costo total"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'purchase_order'
        verbose_name = "Orden de Compra"
        verbose_name_plural = "Órdenes de Compra"
        indexes = [
            models.Index(fields=['store']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self) -> str:
        return f"Compra a {self.supplier.name} - ${self.total_cost}"


class PurchaseOrderItem(models.Model):
    """Item dentro de una orden de compra."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='purchase_order_items'
    )
    quantity = models.PositiveIntegerField(help_text="Cantidad")
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Costo unitario"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'purchase_order_item'
        verbose_name = "Item de Orden de Compra"
        verbose_name_plural = "Items de Órdenes de Compra"
    
    @property
    def subtotal(self) -> Decimal:
        """Subtotal del item."""
        return self.quantity * self.unit_cost
    
    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"
