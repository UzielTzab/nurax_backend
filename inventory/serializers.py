"""
Serializadores para la app Inventory.
"""
from rest_framework import serializers
from .models import InventoryTransaction, InventoryMovement


class InventoryTransactionSerializer(serializers.ModelSerializer):
    """Serializador para transacciones de inventario."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = InventoryTransaction
        fields = ['id', 'product', 'product_name', 'transaction_type', 'quantity', 'reason', 'created_at']
        read_only_fields = ['id', 'created_at']


class InventoryMovementSerializer(serializers.ModelSerializer):
    """Serializador para movimientos de inventario."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = InventoryMovement
        fields = [
            'id', 'product', 'product_name', 'movement_type',
            'quantity', 'unit_cost', 'total_cost', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
