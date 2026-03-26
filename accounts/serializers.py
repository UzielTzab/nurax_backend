"""
Serializadores para la app Accounts.
"""
from rest_framework import serializers
from .models import User, Client, StoreProfile, ActiveSessionCart


class UserSerializer(serializers.ModelSerializer):
    """Serializador para usuarios."""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'avatar_url', 'is_active']
        read_only_fields = ['id']


class ClientSerializer(serializers.ModelSerializer):
    """Serializador para clientes."""
    
    class Meta:
        model = Client
        fields = ['id', 'name', 'email', 'company', 'plan', 'active', 'created_at']
        read_only_fields = ['id', 'created_at']


class StoreProfileSerializer(serializers.ModelSerializer):
    """Serializador para perfiles de tienda."""
    
    class Meta:
        model = StoreProfile
        fields = ['id', 'company_name', 'company_email', 'phone', 'address', 'logo_url', 'tax_id']
        read_only_fields = ['id']
