import uuid
from typing import TYPE_CHECKING
from django.db import models

if TYPE_CHECKING:
    from .models import Product

class ProductQuerySet(models.QuerySet):

    def in_stock(self) -> "ProductQuerySet":
        return self.filter(current_stock__gt=0)
    
    def low_stock(self, threshold_quantity: int = 10) -> "ProductQuerySet":
        return self.filter(current_stock__lte=threshold_quantity, current_stock__gt=0)
    
    def out_of_stock(self) -> "ProductQuerySet":
        return self.filter(current_stock=0)
    
    def with_related(self) -> "ProductQuerySet":
        return self.select_related('category', 'supplier', 'store')


class ProductManager(models.Manager):
    
    def get_queryset(self) -> ProductQuerySet:
        return ProductQuerySet(self.model, using=self._db)
    
    def in_stock(self) -> ProductQuerySet:
        return self.get_queryset().in_stock()
    
    def low_stock(self, threshold_quantity: int = 10) -> ProductQuerySet:
        return self.get_queryset().low_stock(threshold_quantity)
    
    def out_of_stock(self) -> ProductQuerySet:
        return self.get_queryset().out_of_stock()
    
    def with_related(self) -> ProductQuerySet:
        return self.get_queryset().with_related()


class SupplierQuerySet(models.QuerySet):
    
    def active(self) -> "SupplierQuerySet":
        return self


class SupplierManager(models.Manager):
    
    def get_queryset(self) -> SupplierQuerySet:
        return SupplierQuerySet(self.model, using=self._db)
