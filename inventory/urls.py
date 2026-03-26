"""
URLs para la app Inventory.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventoryTransactionViewSet, InventoryMovementViewSet

router = DefaultRouter()
router.register('transactions', InventoryTransactionViewSet, basename='transaction')
router.register('movements', InventoryMovementViewSet, basename='movement')

urlpatterns = [
    path('', include(router.urls)),
]
