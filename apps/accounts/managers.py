"""
Managers y QuerySets personalizados para la app Accounts.
"""
from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from .models import User


class UserQuerySet(models.QuerySet):
    """QuerySet personalizado para User."""
    
    def admins(self) -> "UserQuerySet":
        """Retorna solo administradores."""
        return self.filter(role='admin')
    
    def clients(self) -> "UserQuerySet":
        """Retorna solo clientes."""
        return self.filter(role='cliente')
    
    def active(self) -> "UserQuerySet":
        """Retorna solo usuarios activos."""
        return self.filter(is_active=True)


class UserManager(models.Manager):
    """Manager personalizado para User."""
    
    def get_queryset(self) -> UserQuerySet:
        return UserQuerySet(self.model, using=self._db)
    
    def admins(self) -> UserQuerySet:
        """Retorna solo administradores."""
        return self.get_queryset().admins()
    
    def clients(self) -> UserQuerySet:
        """Retorna solo clientes."""
        return self.get_queryset().clients()
    
    def active(self) -> UserQuerySet:
        """Retorna solo usuarios activos."""
        return self.get_queryset().active()
