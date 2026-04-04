"""
Vistas para la app Accounts.
ARCHITECTURE_V2: Usuarios, tiendas, membresías y clientes.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import User, Store, StoreMembership, Client
from .serializers import (
    UserSerializer, StoreSerializer, StoreMembershipSerializer,
    ClientSerializer, StoreWithMembershipsSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ViewSet):
    """ViewSet para usuarios (solo lectura del perfil)."""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['GET', 'PATCH'])
    def me(self, request):
        """Obtiene o actualiza el perfil del usuario actual."""
        user = request.user
        
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['PATCH'])
    def change_password(self, request):
        """Cambia la contraseña del usuario actual."""
        user = request.user
        
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        # Validar que todos los campos estén presentes
        if not current_password or not new_password or not confirm_password:
            return Response(
                {'error': 'current_password, new_password y confirm_password son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que la contraseña actual sea correcta
        if not user.check_password(current_password):
            return Response(
                {'error': 'La contraseña actual es incorrecta'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verificar que las contraseñas nuevas coincidan
        if new_password != confirm_password:
            return Response(
                {'error': 'Las contraseñas nuevas no coinciden'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cambiar la contraseña
        user.set_password(new_password)
        user.save()
        
        return Response({'message': 'Contraseña actualizada correctamente'})


class StoreViewSet(viewsets.ModelViewSet):
    """ViewSet para tiendas."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = StoreSerializer
    queryset = Store.objects.all()
    
    def get_queryset(self):
        """Filtrar tiendas donde el usuario es miembro."""
        user = self.request.user
        # Obtener todas las tiendas donde el usuario tiene membresía
        store_ids = StoreMembership.objects.filter(
            user=user
        ).values_list('store_id', flat=True)
        return Store.objects.filter(id__in=store_ids)
    
    def get_serializer_class(self):
        """Usar serializer con membresías en el detalle."""
        if self.action == 'retrieve':
            return StoreWithMembershipsSerializer
        return self.serializer_class
    
    @action(detail=True, methods=['GET'])
    def memberships(self, request, pk=None):
        """Obtener membresías de una tienda."""
        store = self.get_object()
        memberships = StoreMembership.objects.filter(store=store)
        serializer = StoreMembershipSerializer(memberships, many=True)
        return Response(serializer.data)


class StoreMembershipViewSet(viewsets.ModelViewSet):
    """ViewSet para membresías de tienda."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = StoreMembershipSerializer
    queryset = StoreMembership.objects.all()
    
    def get_queryset(self):
        """Filtrar membresías donde el usuario es propietario o gerente."""
        user = self.request.user
        # El usuario solo puede ver membresías de tiendas donde es propietario
        owner_stores = StoreMembership.objects.filter(
            user=user,
            role=StoreMembership.Role.OWNER
        ).values_list('store_id', flat=True)
        return StoreMembership.objects.filter(store_id__in=owner_stores)
    
    @transaction.atomic
    def perform_create(self, serializer):
        """Crear membresía (solo propietarios pueden hacerlo)."""
        # Validar que el creador sea propietario de la tienda
        store = serializer.validated_data['store']
        user = self.request.user
        
        is_owner = StoreMembership.objects.filter(
            store=store,
            user=user,
            role=StoreMembership.Role.OWNER
        ).exists()
        
        if not is_owner:
            raise PermissionError("Solo los propietarios pueden agregar miembros")
        
        serializer.save()


class ClientViewSet(viewsets.ModelViewSet):
    """ViewSet para clientes."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = ClientSerializer
    queryset = Client.objects.all()
    
    def get_queryset(self):
        """Los clientes están asociados a tiendas, no filtrados por usuario."""
        # En la arquitectura V2, los clientes no tienen referencia a usuario
        # solo a tienda (implícita). Por ahora retornamos todos.
        return Client.objects.all()
