"""
Serializadores para la app Expenses.
ARCHITECTURE_V2: Caja, gastos y compras a proveedores.
"""
from rest_framework import serializers
from .models import (
    CashShift, CashMovement, Expense, ExpenseCategory,
    PurchaseOrder, PurchaseOrderItem
)


class CashMovementSerializer(serializers.ModelSerializer):
    """Serializer para movimientos de caja."""
    
    class Meta:
        model = CashMovement
        fields = ['id', 'cash_shift', 'movement_type', 'amount', 'reason', 'created_at']
        read_only_fields = ['id', 'created_at']


class CashShiftSerializer(serializers.ModelSerializer):
    """Serializer para turnos de caja."""
    
    movements = CashMovementSerializer(many=True, read_only=True)
    
    class Meta:
        model = CashShift
        fields = [
            'id', 'store', 'opened_by', 'opened_at', 'closed_at',
            'starting_cash', 'is_open', 'movements', 'created_at'
        ]
        read_only_fields = ['id', 'opened_at', 'is_open']


class ExpenseCategorySerializer(serializers.ModelSerializer):
    """Serializer para categorías de gasto."""
    
    class Meta:
        model = ExpenseCategory
        fields = ['id', 'store', 'name']
        read_only_fields = ['id']


class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer para gastos."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'id', 'store', 'category', 'category_name', 'cash_shift',
            'purchase_order', 'amount', 'description', 'payment_method', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """Serializer para items de orden de compra."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id', 'purchase_order', 'product', 'product_name',
            'quantity', 'unit_cost', 'subtotal'
        ]
        read_only_fields = ['id']
    
    def get_subtotal(self, obj):
        return str(obj.subtotal)


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer para órdenes de compra."""
    
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'store', 'supplier', 'supplier_name', 'status',
            'total_cost', 'items', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
