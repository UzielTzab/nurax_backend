"""
Serializadores para la app Inventory.
ARCHITECTURE_V2: Movimientos de inventario (Kárdex).
"""
from rest_framework import serializers
from .models import InventoryMovement


class InventoryMovementSerializer(serializers.ModelSerializer):
    """Serializer para movimientos de inventario (Kárdex)."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    
    class Meta:
        model = InventoryMovement
        fields = [
            'id', 'product', 'product_name', 'user', 'user_name',
            'movement_type', 'quantity', 'stock_before', 'stock_after', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
