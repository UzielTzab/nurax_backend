"""
Vistas para la app Accounts.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import User, Client, StoreProfile
from .serializers import UserSerializer, ClientSerializer, StoreProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet para usuarios."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)


class ClientViewSet(viewsets.ModelViewSet):
    """ViewSet para clientes."""
    
    permission_classes = [IsAuthenticated]
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class StoreProfileViewSet(viewsets.ModelViewSet):
    """ViewSet para perfiles de tienda."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = StoreProfileSerializer
    
    def get_queryset(self):
        return StoreProfile.objects.filter(user=self.request.user)
