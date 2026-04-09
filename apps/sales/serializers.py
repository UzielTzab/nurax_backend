"""
Serializadores para la app Sales.
ARCHITECTURE_V2: Ventas, items y pagos.
"""
from rest_framework import serializers
from .models import Sale, SaleItem, SalePayment


class SaleItemSerializer(serializers.ModelSerializer):
    """Serializer para items de venta."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.SerializerMethodField()
    profit = serializers.SerializerMethodField()
    
    class Meta:
        model = SaleItem
        fields = [
            'id', 'sale', 'product', 'product_name', 'quantity',
            'unit_price', 'unit_cost', 'subtotal', 'profit'
        ]
        read_only_fields = ['id', 'sale']
    
    def get_subtotal(self, obj):
        return str(obj.subtotal)
    
    def get_profit(self, obj):
        return str(obj.profit)


class SalePaymentSerializer(serializers.ModelSerializer):
    """Serializer para pagos de venta."""
    
    class Meta:
        model = SalePayment
        fields = ['id', 'sale', 'cash_shift', 'amount', 'created_at']
        read_only_fields = ['id', 'created_at']


class SaleSerializer(serializers.ModelSerializer):
    """Serializer para ventas."""
    
    items = SaleItemSerializer(many=True, read_only=True)
    payments = SalePaymentSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True, allow_null=True)
    balance_due = serializers.SerializerMethodField()
    
    class Meta:
        model = Sale
        fields = [
            'id', 'store', 'cash_shift', 'customer', 'customer_name',
            'status', 'total_amount', 'amount_paid', 'balance_due',
            'items', 'payments', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'balance_due']
    
    def get_balance_due(self, obj):
        return str(obj.balance_due)


class SaleCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear ventas."""
    
    class Meta:
        model = Sale
        fields = [
            'store', 'cash_shift', 'customer', 'status',
            'total_amount', 'amount_paid'
        ]
