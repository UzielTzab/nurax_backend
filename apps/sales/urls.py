"""
URLs para la app Sales.
Arquitectura Final: Ventas, items y pagos.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SaleViewSet, SaleItemViewSet, SalePaymentViewSet, SummaryReportView

router = DefaultRouter()
router.register('sales', SaleViewSet, basename='sale')
router.register('items', SaleItemViewSet, basename='sale-item')
router.register('payments', SalePaymentViewSet, basename='payment')

urlpatterns = [
    path('reports/summary/', SummaryReportView.as_view(), name='summary-report'),
    path('', include(router.urls)),
]
