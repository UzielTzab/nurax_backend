"""
Managers y QuerySets personalizados para la app Products.
"""
from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from .models import Product


class ProductQuerySet(models.QuerySet):
    """QuerySet personalizado para Product."""
    
    def in_stock(self) -> "ProductQuerySet":
        """Productos con stock disponible."""
        return self.filter(stock__gt=0)
    
    def low_stock(self, threshold: int = 10) -> "ProductQuerySet":
        """Productos con stock bajo."""
        return self.filter(stock__lte=threshold, stock__gt=0)
    
    def out_of_stock(self) -> "ProductQuerySet":
        """Productos sin stock."""
        return self.filter(stock=0)
    
    def with_related(self) -> "ProductQuerySet":
        """Optimiza queries relacionadas."""
        return self.select_related('category', 'supplier', 'user')


class ProductManager(models.Manager):
    """Manager personalizado para Product."""
    
    def get_queryset(self) -> ProductQuerySet:
        return ProductQuerySet(self.model, using=self._db)
    
    def in_stock(self) -> ProductQuerySet:
        return self.get_queryset().in_stock()
    
    def low_stock(self, threshold: int = 10) -> ProductQuerySet:
        return self.get_queryset().low_stock(threshold)
    
    def out_of_stock(self) -> ProductQuerySet:
        return self.get_queryset().out_of_stock()
    
    def with_related(self) -> ProductQuerySet:
        return self.get_queryset().with_related()


class SupplierQuerySet(models.QuerySet):
    """QuerySet personalizado para Supplier."""
    
    def active(self) -> "SupplierQuerySet":
        """Proveedores activos."""
        return self


class SupplierManager(models.Manager):
    """Manager personalizado para Supplier."""
    
    def get_queryset(self) -> SupplierQuerySet:
        return SupplierQuerySet(self.model, using=self._db)
