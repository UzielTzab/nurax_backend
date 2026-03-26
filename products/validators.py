"""
Validadores personalizados para la app Products.
"""
from decimal import Decimal
from django.core.exceptions import ValidationError


def validate_positive_decimal(value: Decimal) -> None:
    """Validar que sea decimal positivo."""
    if value <= 0:
        raise ValidationError("Debe ser un número positivo")


def validate_sku_format(sku: str) -> None:
    """Validar formato de SKU."""
    if not sku or len(sku) < 3 or len(sku) > 50:
        raise ValidationError("SKU debe tener entre 3 y 50 caracteres")


def validate_stock_not_negative(stock: int) -> None:
    """Validar que stock no sea negativo."""
    if stock < 0:
        raise ValidationError("El stock no puede ser negativo")
