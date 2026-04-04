"""
URLs para la app Products.
ARCHITECTURE_V2: Catálogo, categorías, proveedores y códigos.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, CategoryViewSet, SupplierViewSet,
    ProductPackagingViewSet, ProductCodeViewSet
)

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('categories', CategoryViewSet, basename='category')
router.register('suppliers', SupplierViewSet, basename='supplier')
router.register('packagings', ProductPackagingViewSet, basename='packaging')
router.register('codes', ProductCodeViewSet, basename='code')

urlpatterns = [
    path('', include(router.urls)),
]
