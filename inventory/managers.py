"""
Managers y QuerySets personalizados para la app Inventory.
"""
from django.db import models


class InventoryTransactionQuerySet(models.QuerySet):
    """QuerySet para transacciones de inventario."""
    
    def entries(self) -> "InventoryTransactionQuerySet":
        """Entradas de inventario."""
        return self.filter(transaction_type='in')
    
    def exits(self) -> "InventoryTransactionQuerySet":
        """Salidas de inventario."""
        return self.filter(transaction_type='out')


class InventoryTransactionManager(models.Manager):
    """Manager para transacciones de inventario."""
    
    def get_queryset(self) -> InventoryTransactionQuerySet:
        return InventoryTransactionQuerySet(self.model, using=self._db)
    
    def entries(self) -> InventoryTransactionQuerySet:
        return self.get_queryset().entries()
    
    def exits(self) -> InventoryTransactionQuerySet:
        return self.get_queryset().exits()
