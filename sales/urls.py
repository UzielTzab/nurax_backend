"""
URLs para la app Sales.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SaleViewSet, SalePaymentViewSet

router = DefaultRouter()
router.register('sales', SaleViewSet, basename='sale')
router.register('payments', SalePaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]
