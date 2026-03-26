"""
Modelos para la app Expenses - Gastos y cortes de caja.
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from accounts.models import User
from products.models import Supplier
from .managers import ExpenseManager, CashShiftManager
from .validators import validate_amount_positive


class Expense(models.Model):
    """Gasto o egreso."""
    
    class Category(models.TextChoices):
        SERVICIOS = 'servicios', 'Servicios (Luz, Agua, Internet)'
        NOMINA = 'nomina', 'Nómina / Sueldos'
        PROVEEDORES = 'proveedores', 'Pago a Proveedores'
        INVENTARIO = 'inventario', 'Inventario / Reabastecimiento'
        VARIOS = 'varios', 'Gastos Varios'
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[validate_amount_positive],
        help_text="Monto del gasto"
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        help_text="Categoría del gasto"
    )
    description = models.CharField(
        max_length=255,
        help_text="Descripción"
    )
    receipt_url = models.URLField(
        max_length=800,
        blank=True,
        null=True,
        help_text="URL del recibo"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Usuario"
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Proveedor"
    )
    cash_shift = models.ForeignKey(
        'CashShift',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses',
        help_text="Turno de caja"
    )
    date = models.DateField(auto_now_add=True)
    
    objects = ExpenseManager()
    
    class Meta:
        db_table = 'expense'
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"
        indexes = [
            models.Index(fields=['category', 'date']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self) -> str:
        return f"{self.category} - ${self.amount}"


class CashShift(models.Model):
    """Turno de caja."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Cajero"
    )
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    starting_cash = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Efectivo inicial"
    )
    expected_cash = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Efectivo esperado"
    )
    actual_cash = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Efectivo contado"
    )
    difference = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Diferencia"
    )
    notes = models.TextField(blank=True, help_text="Notas del cierre")
    
    objects = CashShiftManager()
    
    class Meta:
        db_table = 'cash_shift'
        verbose_name = "Turno de Caja"
        verbose_name_plural = "Turnos de Caja"
        indexes = [
            models.Index(fields=['opened_at']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self) -> str:
        status = "Abierto" if not self.closed_at else "Cerrado"
        return f"Turno {status} - {self.opened_at.strftime('%Y-%m-%d %H:%M')}"
