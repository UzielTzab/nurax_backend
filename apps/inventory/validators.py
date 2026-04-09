"""
Validadores personalizados para la app Inventory.
"""
from django.core.exceptions import ValidationError


def validate_quantity_positive(quantity: int) -> None:
    """Validar que cantidad sea positiva."""
    if quantity <= 0:
        raise ValidationError("La cantidad debe ser positiva")
