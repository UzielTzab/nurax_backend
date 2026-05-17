from django.db import models


class SaleQuerySet(models.QuerySet):
    def paid(self) -> "SaleQuerySet":
        return self.filter(status='paid')

    def partial(self) -> "SaleQuerySet":
        return self.filter(status='partial')

    def cancelled(self) -> "SaleQuerySet":
        return self.filter(status='cancelled')

    def with_payments(self) -> "SaleQuerySet":
        return self.prefetch_related('payments', 'items')


class SaleManager(models.Manager):
    def get_queryset(self) -> SaleQuerySet:
        return SaleQuerySet(self.model, using=self._db)

    def paid(self) -> SaleQuerySet:
        return self.get_queryset().paid()

    def partial(self) -> SaleQuerySet:
        return self.get_queryset().partial()

    def cancelled(self) -> SaleQuerySet:
        return self.get_queryset().cancelled()

    def with_payments(self) -> SaleQuerySet:
        return self.get_queryset().with_payments()
