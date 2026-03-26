"""
Validadores personalizados para la app Sales.
"""
from django.core.exceptions import ValidationError
from decimal import Decimal


def validate_sale_total_positive(total: Decimal) -> None:
    """Validar que el total de venta sea positivo."""
    if total <= 0:
        raise ValidationError("El total de la venta debe ser positivo")


def validate_items_not_empty(items: list) -> None:
    """Validar que haya al menos un item."""
    if not items or len(items) == 0:
        raise ValidationError("Una venta debe tener al menos un item")
