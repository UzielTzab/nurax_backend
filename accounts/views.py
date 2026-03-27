"""
Vistas para la app Accounts.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import User, Client, StoreProfile
from .serializers import UserSerializer, ClientSerializer, StoreProfileSerializer

User = get_user_model()


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
