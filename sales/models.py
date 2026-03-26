"""
Modelos para la app Sales - Ventas, items y pagos.
"""
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import User
from products.models import Product
from .managers import SaleManager


class Sale(models.Model):
    """Transacción de venta."""
    
    class Status(models.TextChoices):
        COMPLETED = 'completed', 'Completada'
        PENDING = 'pending', 'Pendiente'
        CANCELLED = 'cancelled', 'Cancelada'
        CREDIT = 'credit', 'Crédito'
        LAYAWAY = 'layaway', 'Apartado'
    
    transaction_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="ID único de transacción"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Usuario que realizó la venta"
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.COMPLETED,
        help_text="Estado de la venta"
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Total de la venta"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    customer_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Nombre del cliente"
    )
    customer_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Teléfono del cliente"
    )
    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Monto pagado"
    )
    
    objects = SaleManager()
    
    class Meta:
        db_table = 'sale'
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    @property
    def balance_due(self) -> Decimal:
        """Saldo adeudado."""
        total_payments = sum(
            payment.amount for payment in self.payments.all()
        ) or Decimal('0')
        if self.status in [self.Status.COMPLETED, self.Status.CANCELLED]:
            return Decimal('0')
        return self.total - total_payments
    
    def __str__(self) -> str:
        return f"{self.transaction_id} — ${self.total}"


class SaleItem(models.Model):
    """Item dentro de una venta."""
    
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Venta asociada"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Producto vendido"
    )
    product_name = models.CharField(
        max_length=250,
        help_text="Snapshot del nombre del producto"
    )
    quantity = models.PositiveIntegerField(
        help_text="Cantidad vendida"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Precio unitario"
    )
    
    class Meta:
        db_table = 'sale_item'
        verbose_name = "Item de Venta"
        verbose_name_plural = "Items de Venta"
    
    @property
    def subtotal(self) -> Decimal:
        """Subtotal del item."""
        return self.quantity * self.unit_price
    
    def __str__(self) -> str:
        return f"{self.product_name} x {self.quantity}"


class SalePayment(models.Model):
    """Pago o abono a una venta."""
    
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='payments',
        help_text="Venta asociada"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Monto del abono"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Usuario que realizó el pago"
    )
    
    class Meta:
        db_table = 'sale_payment'
        verbose_name = "Pago de Venta"
        verbose_name_plural = "Pagos de Ventas"
        indexes = [
            models.Index(fields=['sale', 'created_at']),
        ]
    
    def __str__(self) -> str:
        return f"Abono ${self.amount} a {self.sale.transaction_id}"
