"""
URLs para la app Accounts.
ARCHITECTURE_V2: Usuarios, tiendas y membresías.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, StoreViewSet, StoreMembershipViewSet, ClientViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('stores', StoreViewSet, basename='store')
router.register('memberships', StoreMembershipViewSet, basename='membership')
router.register('clients', ClientViewSet, basename='client')

urlpatterns = [
    path('', include(router.urls)),
]
