"""
Managers y QuerySets personalizados para la app Sales.
"""
from django.db import models


class SaleQuerySet(models.QuerySet):
    """QuerySet personalizado para Sale."""
    
    def completed(self) -> "SaleQuerySet":
        """Ventas completadas."""
        return self.filter(status='completed')
    
    def pending(self) -> "SaleQuerySet":
        """Ventas pendientes."""
        return self.filter(status='pending')
    
    def with_payments(self) -> "SaleQuerySet":
        """Optimiza queries con pagos."""
        return self.prefetch_related('payments', 'items')


class SaleManager(models.Manager):
    """Manager personalizado para Sale."""
    
    def get_queryset(self) -> SaleQuerySet:
        return SaleQuerySet(self.model, using=self._db)
    
    def completed(self) -> SaleQuerySet:
        return self.get_queryset().completed()
    
    def pending(self) -> SaleQuerySet:
        return self.get_queryset().pending()
