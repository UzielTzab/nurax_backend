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



class SaleCreateItemSerializer(serializers.Serializer):
    product = serializers.IntegerField(allow_null=True, required=False)
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)

class SaleCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear ventas."""
    
    items = SaleCreateItemSerializer(many=True, write_only=True, required=False)
    id = serializers.UUIDField(read_only=True)
    
    class Meta:
        model = Sale
        fields = [
            'id', 'store', 'cash_shift', 'customer', 'status',
            'total_amount', 'amount_paid', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        sale = super().create(validated_data)
        
        from apps.products.models import Product
        
        for item_data in items_data:
            # Si el frontend envía 'product' nulo, se puede omitir o manejar. 
            product_id = item_data.get('product')
            unit_cost = 0
            if product_id:
                try:
                    product = Product.objects.get(id=product_id)
                    unit_cost = product.base_cost or 0
                except Product.DoesNotExist:
                    pass
                    
            SaleItem.objects.create(
                sale=sale,
                product_id=product_id,
                quantity=item_data.get('quantity'),
                unit_price=item_data.get('unit_price'),
                unit_cost=unit_cost
            )
            
        return sale
