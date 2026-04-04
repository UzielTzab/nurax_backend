"""
URLs para la app Sales.
ARCHITECTURE_V2: Ventas, items y pagos.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SaleViewSet, SaleItemViewSet, SalePaymentViewSet

router = DefaultRouter()
router.register('sales', SaleViewSet, basename='sale')
router.register('items', SaleItemViewSet, basename='sale-item')
router.register('payments', SalePaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]
