"""
URLs para la app Expenses.
ARCHITECTURE_V2: Caja, gastos y compras a proveedores.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CashShiftViewSet, CashMovementViewSet, ExpenseCategoryViewSet,
    ExpenseViewSet, PurchaseOrderViewSet
)

router = DefaultRouter()
router.register('cash-shifts', CashShiftViewSet, basename='cash-shift')
router.register('cash-movements', CashMovementViewSet, basename='cash-movement')
router.register('expense-categories', ExpenseCategoryViewSet, basename='expense-category')
router.register('expenses', ExpenseViewSet, basename='expense')
router.register('purchase-orders', PurchaseOrderViewSet, basename='purchase-order')

urlpatterns = [
    path('', include(router.urls)),
]
