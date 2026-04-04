"""
URLs para la app Carts.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActiveCartViewSet

router = DefaultRouter()
router.register(r'carts', ActiveCartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
]
