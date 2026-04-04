"""
URLs para la app Inventory.
ARCHITECTURE_V2: Movimientos de inventario (Kárdex).
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventoryMovementViewSet

router = DefaultRouter()
router.register('movements', InventoryMovementViewSet, basename='movement')

urlpatterns = [
    path('', include(router.urls)),
]
