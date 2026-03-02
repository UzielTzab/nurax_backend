from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, SaleViewSet, ClientViewSet, CategoryViewSet,
    SupplierViewSet, UserViewSet, StoreProfileViewSet,
    ExpenseViewSet, CashShiftViewSet,
    InventoryTransactionViewSet, SalePaymentViewSet
)

router = DefaultRouter()
router.register('products',     ProductViewSet)
router.register('sales',        SaleViewSet)
router.register('clients',      ClientViewSet)
router.register('categories',   CategoryViewSet)
router.register('suppliers',    SupplierViewSet)
router.register('users',        UserViewSet)
router.register('store',        StoreProfileViewSet, basename='store')
router.register('expenses',     ExpenseViewSet)
router.register('shifts',       CashShiftViewSet)
router.register('inventory-tx', InventoryTransactionViewSet)
router.register('payments',     SalePaymentViewSet)

urlpatterns = router.urls
