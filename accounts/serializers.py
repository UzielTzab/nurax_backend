"""
Serializadores para la app Accounts.
ARCHITECTURE_V2: Usuarios, tiendas y membresías.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User, Store, StoreMembership, Client

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer para usuarios - retorna campos esperados por frontend."""
    
    # Método para obtener 'name' como combinación de first_name y last_name
    def get_name(self, obj):
        """Retorna nombre completo (first_name + last_name o 'name' field)."""
        if obj.name:
            return obj.name
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name if full_name else obj.username
    
    # Método para combinar en guardar
    def to_representation(self, instance):
        """Customizza la representación para el frontend."""
        data = super().to_representation(instance)
        # Usar el campo 'name' si existe, sino combinar first_name y last_name
        if not data.get('name'):
            data['name'] = f"{instance.first_name} {instance.last_name}".strip() or instance.username
        return data
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'name', 'role', 'avatar_url']
        read_only_fields = ['id']


class StoreSerializer(serializers.ModelSerializer):
    """Serializer para tiendas."""
    
    class Meta:
        model = Store
        fields = ['id', 'name', 'plan', 'tax_id', 'active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class StoreMembershipSerializer(serializers.ModelSerializer):
    """Serializer para membresías de tienda."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    
    class Meta:
        model = StoreMembership
        fields = ['id', 'store', 'store_name', 'user', 'user_email', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']


class ClientSerializer(serializers.ModelSerializer):
    """Serializer para clientes."""
    
    class Meta:
        model = Client
        fields = ['id', 'name', 'credit_limit', 'created_at']
        read_only_fields = ['id', 'created_at']


class StoreWithMembershipsSerializer(serializers.ModelSerializer):
    """Serializer para tienda con membresías."""
    
    memberships = StoreMembershipSerializer(many=True, read_only=True)
    
    class Meta:
        model = Store
        fields = ['id', 'name', 'plan', 'tax_id', 'active', 'memberships', 'created_at']
        read_only_fields = ['id', 'created_at']
