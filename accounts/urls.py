"""
URLs para la app Accounts.
ARCHITECTURE_V2: Usuarios, tiendas y membresías.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, StoreViewSet, StoreMembershipViewSet, ClientViewSet

router = DefaultRouter()
# NO registrar UserViewSet en router - usaremos rutas explícitas para tener control
# router.register('users', UserViewSet, basename='user')  # Comentado
router.register('stores', StoreViewSet, basename='store')
router.register('memberships', StoreMembershipViewSet, basename='membership')
router.register('clients', ClientViewSet, basename='client')

# Rutas explícitas para UserViewSet para máximo control sobre nombres de rutas
urlpatterns = [
    path('users/me/', UserViewSet.as_view({'get': 'me', 'patch': 'me'}), name='user-me'),
    path('users/register/', UserViewSet.as_view({'post': 'register'}), name='user-register'),
    path('users/software-clients/', UserViewSet.as_view({'get': 'software_clients'}), name='software-clients-list'),
    path('users/software-clients/<uuid:user_id>/toggle-active/', UserViewSet.as_view({'patch': 'toggle_software_client'}), name='software-clients-toggle'),
    path('users/software-clients/<uuid:user_id>/', UserViewSet.as_view({'delete': 'delete_software_client'}), name='software-clients-delete'),
    path('users/change-password/', UserViewSet.as_view({'patch': 'change_password'}), name='user-change-password'),
    path('stores/create-with-owner/', StoreViewSet.as_view({'post': 'create_with_owner'}), name='store-create-with-owner'),
    path('', include(router.urls)),
]
