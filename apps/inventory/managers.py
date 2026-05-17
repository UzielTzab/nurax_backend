from django.db import models


class InventoryMovementQuerySet(models.QuerySet):
    def entries(self) -> "InventoryMovementQuerySet":
        return self.filter(quantity__gt=0)

    def exits(self) -> "InventoryMovementQuerySet":
        return self.filter(quantity__lt=0)

    def for_store(self, store) -> "InventoryMovementQuerySet":
        return self.filter(product__store=store)


class InventoryMovementManager(models.Manager):
    def get_queryset(self) -> InventoryMovementQuerySet:
        return InventoryMovementQuerySet(self.model, using=self._db)

    def entries(self) -> InventoryMovementQuerySet:
        return self.get_queryset().entries()

    def exits(self) -> InventoryMovementQuerySet:
        return self.get_queryset().exits()

    def for_store(self, store) -> InventoryMovementQuerySet:
        return self.get_queryset().for_store(store)
