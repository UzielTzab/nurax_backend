from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProductViewSet, CategoryViewSet, SupplierViewSet,
    ProductPackagingViewSet, ProductCodeViewSet, ProductVariationViewSet
)

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('categories', CategoryViewSet, basename='category')
router.register('suppliers', SupplierViewSet, basename='supplier')
router.register('packagings', ProductPackagingViewSet, basename='packaging')
router.register('codes', ProductCodeViewSet, basename='code')
router.register('variations', ProductVariationViewSet, basename='variation')

urlpatterns = [
    path('', include(router.urls)),
]
