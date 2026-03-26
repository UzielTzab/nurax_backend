"""
URLs para la app Accounts.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ClientViewSet, StoreProfileViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('clients', ClientViewSet, basename='client')
router.register('store-profiles', StoreProfileViewSet, basename='store-profile')

urlpatterns = [
    path('', include(router.urls)),
]
