"""
Serializers para la app Carts.
"""
from rest_framework import serializers
from .models import ActiveCart, CartItem
from products.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer para items del carrito."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price_at_time', 'subtotal']
    
    def get_subtotal(self, obj):
        return obj.subtotal


class ActiveCartSerializer(serializers.ModelSerializer):
    """Serializer para carritos activos."""
    
    items = CartItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = ActiveCart
        fields = ['id', 'session_id', 'total_temp', 'updated_at', 'items']
        read_only_fields = ['id', 'updated_at']


class CartItemCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear items en el carrito."""
    
    class Meta:
        model = CartItem
        fields = ['product', 'quantity', 'unit_price_at_time']
    
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0")
        return value
