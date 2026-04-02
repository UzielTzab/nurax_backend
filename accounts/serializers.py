"""
Serializadores para la app Accounts.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User, Client, StoreProfile, ActiveSessionCart

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializador para usuarios."""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'avatar_url', 'is_active']
        read_only_fields = ['id']


class ClientSerializer(serializers.ModelSerializer):
    """Serializador para clientes.
    
    Al crear un cliente, se crea automáticamente un usuario con:
    - email: email del cliente
    - username: email del cliente
    - password: "nurax123" (hasheada)
    - role: 'cliente'
    - name: nombre del cliente
    """
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Client
        fields = ['id', 'name', 'email', 'company', 'plan', 'active', 'user', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']
    
    def validate_email(self, value: str) -> str:
        """Valida que el email sea único tanto en Client como en User."""
        # Validar en Client
        if Client.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un cliente con este email.")
        
        # Validar en User
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email.")
        
        return value


class StoreProfileSerializer(serializers.ModelSerializer):
    """Serializador para perfiles de tienda."""
    
    class Meta:
        model = StoreProfile
        fields = ['id', 'company_name', 'company_email', 'phone', 'address', 'logo_url', 'tax_id']
        read_only_fields = ['id']
