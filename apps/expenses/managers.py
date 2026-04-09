"""
Managers y QuerySets personalizados para la app Expenses.
"""
from django.db import models


class ExpenseQuerySet(models.QuerySet):
    """QuerySet para gastos."""
    
    def by_category(self, category: str) -> "ExpenseQuerySet":
        """Gastos por categoría."""
        return self.filter(category=category)


class ExpenseManager(models.Manager):
    """Manager para gastos."""
    
    def get_queryset(self) -> ExpenseQuerySet:
        return ExpenseQuerySet(self.model, using=self._db)
    
    def by_category(self, category: str) -> ExpenseQuerySet:
        return self.get_queryset().by_category(category)


class CashShiftQuerySet(models.QuerySet):
    """QuerySet para turnos de caja."""
    
    def open(self) -> "CashShiftQuerySet":
        """Turnos abiertos."""
        return self.filter(closed_at__isnull=True)
    
    def closed(self) -> "CashShiftQuerySet":
        """Turnos cerrados."""
        return self.filter(closed_at__isnull=False)


class CashShiftManager(models.Manager):
    """Manager para turnos de caja."""
    
    def get_queryset(self) -> CashShiftQuerySet:
        return CashShiftQuerySet(self.model, using=self._db)
    
    def open(self) -> CashShiftQuerySet:
        return self.get_queryset().open()
    
    def closed(self) -> CashShiftQuerySet:
        return self.get_queryset().closed()
