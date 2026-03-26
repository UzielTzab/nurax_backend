"""
Validadores personalizados para la app Accounts.
"""
from django.core.exceptions import ValidationError


def validate_email_not_exists(email: str) -> None:
    """
    Validar que el email no exista en el sistema.
    
    Args:
        email: Email a validar
    
    Raises:
        ValidationError: Si el email ya existe
    """
    from .models import User
    
    if User.objects.filter(email=email).exists():
        raise ValidationError(f"El email {email} ya está registrado")
