"""
Vistas para la app Accounts.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import User, Client, StoreProfile
from .serializers import UserSerializer, ClientSerializer, StoreProfileSerializer

User = get_user_model()

# Contraseña por defecto para nuevos clientes
DEFAULT_CLIENT_PASSWORD = 'nurax123'


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet para usuarios."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['GET', 'PATCH'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Obtiene o actualiza el perfil del usuario actual (incluido avatar)."""
        user = request.user
        
        if request.method == 'PATCH':
            # Manejo de archivo avatar si existe
            if 'avatar_file' in request.FILES:
                user.avatar_url = request.FILES['avatar_file']
            
            # Actualizar otros campos si los hay
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['PATCH'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """Cambia la contraseña del usuario actual."""
        user = request.user
        
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        # Validar que todos los campos estén presentes
        if not current_password or not new_password or not confirm_password:
            return Response(
                {'detail': 'current_password, new_password y confirm_password son requeridos'},
                status=400
            )
        
        # Verificar que la contraseña actual sea correcta
        if not user.check_password(current_password):
            return Response(
                {'detail': 'La contraseña actual es incorrecta'},
                status=400
            )
        
        # Verificar que las contraseñas nuevas coincidan
        if new_password != confirm_password:
            return Response(
                {'detail': 'Las contraseñas nuevas no coinciden'},
                status=400
            )
        
        # Cambiar la contraseña
        user.set_password(new_password)
        user.save()
        
        return Response(
            {'detail': 'Contraseña actualizada correctamente', 'success': True}
        )


class ClientViewSet(viewsets.ModelViewSet):
    """ViewSet para clientes.
    
    Al crear un cliente, se crea automáticamente un usuario para que pueda acceder al sistema.
    Usuario creado:
      - email: igual al email del cliente
      - username: igual al email del cliente
      - password: "nurax123" (recomendado cambiar en primer login)
      - role: 'cliente'
      - name: nombre del cliente
    """
    
    permission_classes = [IsAuthenticated]
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    
    @transaction.atomic
    def perform_create(self, serializer):
        """Crea un cliente y su usuario asociado automáticamente.
        
        Esta operación es atómica: si falla la creación del usuario,
        se revierte también la creación del cliente.
        
        Args:
            serializer: ClientSerializer con datos validados
            
        Raises:
            ValidationError: Si el email ya existe en User o Client
        """
        client_data = serializer.validated_data
        
        # Crear usuario
        user = User.objects.create_user(
            email=client_data['email'],
            username=client_data['email'],
            password=DEFAULT_CLIENT_PASSWORD,
            name=client_data['name'],
            role=User.Role.CLIENTE
        )
        
        # Guardar cliente con usuario asociado
        serializer.save(user=user)


class StoreProfileViewSet(viewsets.ModelViewSet):
    """ViewSet para perfiles de tienda."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = StoreProfileSerializer
    
    def get_queryset(self):
        return StoreProfile.objects.filter(user=self.request.user)
