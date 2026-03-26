"""
URLs para la app Expenses.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExpenseViewSet, CashShiftViewSet

router = DefaultRouter()
router.register('expenses', ExpenseViewSet, basename='expense')
router.register('cash-shifts', CashShiftViewSet, basename='cash-shift')

urlpatterns = [
    path('', include(router.urls)),
]
