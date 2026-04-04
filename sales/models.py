"""
Modelos para la app Sales - Ventas, items y pagos.
ARCHITECTURE_V2: Ventas, créditos y control de flujo de caja.
"""
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
import uuid


class Sale(models.Model):
    """Transacción de venta."""
    
    class Status(models.TextChoices):
        PAID = 'paid', 'Pagada'
        PARTIAL = 'partial', 'Pago Parcial'
        CANCELLED = 'cancelled', 'Cancelada'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(
        'accounts.Store',
        on_delete=models.CASCADE,
        related_name='sales'
    )
    cash_shift = models.ForeignKey(
        'expenses.CashShift',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales',
        help_text="Turno de caja donde se ingresó el dinero"
    )
    customer = models.ForeignKey(
        'accounts.Client',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales',
        help_text="Cliente (opcional para venta rápida)"
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PAID,
        help_text="Estado de la venta"
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Total a cobrar"
    )
    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Suma de abonos + pago inicial"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sale'
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        indexes = [
            models.Index(fields=['store']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    @property
    def balance_due(self) -> Decimal:
        """Saldo adeudado."""
        return self.total_amount - self.amount_paid
    
    def __str__(self) -> str:
        return f"Venta {self.id} — ${self.total_amount}"


class SaleItem(models.Model):
    """Producto dentro de una venta."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        related_name='sale_items'
    )
    quantity = models.PositiveIntegerField(help_text="Cantidad vendida")
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Precio unitario al momento de la venta"
    )
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Costo unitario al momento de la venta"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sale_item'
        verbose_name = "Item de Venta"
        verbose_name_plural = "Items de Venta"
    
    @property
    def subtotal(self) -> Decimal:
        """Subtotal del item."""
        return self.quantity * self.unit_price
    
    @property
    def profit(self) -> Decimal:
        """Ganancia del item."""
        return (self.unit_price - self.unit_cost) * self.quantity
    
    def __str__(self) -> str:
        product_name = self.product.name if self.product else "Product deleted"
        return f"{product_name} x {self.quantity}"


class SalePayment(models.Model):
    """Pago o abono a una venta."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    cash_shift = models.ForeignKey(
        'expenses.CashShift',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sale_payments'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Monto del abono"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sale_payment'
        verbose_name = "Pago de Venta"
        verbose_name_plural = "Pagos de Ventas"
        indexes = [
            models.Index(fields=['sale']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self) -> str:
        return f"Pago ${self.amount}"
