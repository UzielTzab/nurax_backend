from django.db import models


class ExpenseQuerySet(models.QuerySet):
    def by_category(self, category) -> "ExpenseQuerySet":
        return self.filter(category=category)


class ExpenseManager(models.Manager):
    def get_queryset(self) -> ExpenseQuerySet:
        return ExpenseQuerySet(self.model, using=self._db)

    def by_category(self, category) -> ExpenseQuerySet:
        return self.get_queryset().by_category(category)


class CashShiftQuerySet(models.QuerySet):
    def open(self) -> "CashShiftQuerySet":
        return self.filter(closed_at__isnull=True)

    def closed(self) -> "CashShiftQuerySet":
        return self.filter(closed_at__isnull=False)


class CashShiftManager(models.Manager):
    def get_queryset(self) -> CashShiftQuerySet:
        return CashShiftQuerySet(self.model, using=self._db)

    def open(self) -> CashShiftQuerySet:
        return self.get_queryset().open()

    def closed(self) -> CashShiftQuerySet:
        return self.get_queryset().closed()
