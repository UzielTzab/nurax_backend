"""
Serializadores para la app Sales.
ARCHITECTURE_V2: Ventas, items y pagos.
"""
from rest_framework import serializers
from django.db import transaction
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
    customer_phone = serializers.SerializerMethodField()
    balance_due = serializers.SerializerMethodField()
    cashier = serializers.SerializerMethodField()
    
    class Meta:
        model = Sale
        fields = [
            'id', 'transaction_id', 'store', 'cash_shift', 'cashier', 'customer', 'customer_name', 'customer_phone',
            'status', 'sale_type', 'total_amount', 'amount_paid', 'amount_tendered', 'change', 'balance_due',
            'items', 'payments', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'balance_due', 'cashier']
    
    def get_balance_due(self, obj):
        return str(obj.balance_due)

    def get_customer_phone(self, obj):
        return getattr(obj.customer, 'phone', '') if obj.customer else ''
        
    def get_cashier(self, obj):
        if not obj.cash_shift or not obj.cash_shift.opened_by:
            return None
        user = obj.cash_shift.opened_by
        return {
            'id': str(user.id),
            'name': user.first_name or user.name or user.username,
            'username': user.username
        }



class SaleCreateItemSerializer(serializers.Serializer):
    product = serializers.UUIDField(allow_null=True, required=False)
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)

class SaleCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear ventas."""
    
    items = SaleCreateItemSerializer(many=True, write_only=True, required=False)
    id = serializers.UUIDField(read_only=True)
    
    class Meta:
        model = Sale
        fields = [
            'id', 'transaction_id', 'store', 'cash_shift', 'customer', 'status', 'sale_type',
            'total_amount', 'amount_paid', 'amount_tendered', 'change', 'items'
        ]
        
    def validate(self, attrs):
        sale_type = attrs.get('sale_type', Sale.SaleType.CASH)
        customer = attrs.get('customer')
        
        if sale_type in [Sale.SaleType.CREDIT, Sale.SaleType.LAYAWAY]:
            if not customer or customer.name == 'Venta de Mostrador (General)':
                raise serializers.ValidationError(
                    "No se puede otorgar crédito al público general"
                )
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])

        # Crear la venta y los items de forma atómica; si hay product ids, actualizar stock
        with transaction.atomic():
            sale = super().create(validated_data)
            # Determinar amount_tendered: si no se envía, usar amount_paid como valor recibido
            amount_tendered = validated_data.get('amount_tendered')
            if amount_tendered is None:
                amount_tendered = validated_data.get('amount_paid')
            # Calcular change (cambio) solo si amount_tendered está definido
            if amount_tendered is not None:
                try:
                    from decimal import Decimal
                    total = Decimal(str(sale.total_amount))
                    tender = Decimal(str(amount_tendered))
                    change = tender - total if tender > total else Decimal('0')
                except Exception:
                    change = Decimal('0')
                sale.amount_tendered = amount_tendered
                sale.change = change
                sale.save()
            # Calcular y asignar amount_tendered y change si se envían
            amount_tendered = validated_data.get('amount_tendered')
            if amount_tendered is not None:
                try:
                    from decimal import Decimal
                    total = Decimal(str(sale.total_amount))
                    tender = Decimal(str(amount_tendered))
                    change = tender - total if tender > total else Decimal('0')
                except Exception:
                    change = Decimal('0')
                sale.amount_tendered = amount_tendered
                sale.change = change
                sale.save()

            from apps.products.models import Product
            from apps.inventory.models import InventoryMovement

            request = self.context.get('request') if hasattr(self, 'context') else None
            user = getattr(request, 'user', None)

            # Registrar abono inicial si aplica (en crédito o apartado, o incluso contado)
            if sale.amount_paid > 0:
                SalePayment.objects.create(
                    sale=sale,
                    cash_shift=sale.cash_shift,
                    amount=sale.amount_paid,
                    cashier=user if user and user.is_authenticated else None,
                    payment_method=SalePayment.PaymentMethod.CASH
                )

            for item_data in items_data:
                product_id = item_data.get('product')
                qty = int(item_data.get('quantity') or 0)
                unit_price = item_data.get('unit_price')
                unit_cost = 0

                product = None
                if product_id:
                    try:
                        # lock product row to avoid races
                        product = Product.objects.select_for_update().get(id=product_id)
                        unit_cost = product.base_cost or 0
                    except Product.DoesNotExist:
                        product = None

                sale_item = SaleItem.objects.create(
                    sale=sale,
                    product_id=product_id,
                    quantity=qty,
                    unit_price=unit_price,
                    unit_cost=unit_cost
                )

                # Si tenemos product vinculado, decrementar stock y crear InventoryMovement
                if product:
                    stock_before = product.current_stock or 0
                    # Evitar stock negativo: si qty > stock_before, dejar en 0
                    new_stock = max(0, stock_before - qty)
                    product.current_stock = new_stock
                    product.save()

                    InventoryMovement.objects.create(
                        product=product,
                        user=user if user and user.is_authenticated else None,
                        movement_type=InventoryMovement.MovementType.SALE,
                        quantity=qty * -1,
                        stock_before=stock_before,
                        stock_after=product.current_stock
                    )

        return sale
