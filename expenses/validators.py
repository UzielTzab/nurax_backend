"""
Validadores personalizados para la app Expenses.
"""
from decimal import Decimal
from django.core.exceptions import ValidationError


def validate_amount_positive(amount: Decimal) -> None:
    """Validar que monto sea positivo."""
    if amount <= 0:
        raise ValidationError("El monto debe ser positivo")
