"""
Serializadores para la app Sales.
"""
from rest_framework import serializers
from .models import Sale, SaleItem, SalePayment


class SaleItemSerializer(serializers.ModelSerializer):
    """Serializador para items de venta."""
    
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = SaleItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['id', 'subtotal']
    
    def get_subtotal(self, obj):
        return str(obj.subtotal)


class SalePaymentSerializer(serializers.ModelSerializer):
    """Serializador para pagos de venta."""
    
    class Meta:
        model = SalePayment
        fields = ['id', 'amount', 'created_at', 'user']
        read_only_fields = ['id', 'created_at']


class SaleSerializer(serializers.ModelSerializer):
    """Serializador para ventas."""
    
    items = SaleItemSerializer(many=True, read_only=True)
    balance_due = serializers.SerializerMethodField()
    
    class Meta:
        model = Sale
        fields = [
            'id', 'transaction_id', 'status', 'total', 'amount_paid',
            'customer_name', 'customer_phone', 'items', 'balance_due',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'balance_due']
    
    def get_balance_due(self, obj):
        return str(obj.balance_due)
