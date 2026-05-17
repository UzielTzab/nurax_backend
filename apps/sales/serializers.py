from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from .models import Sale, SaleItem, SalePayment


class SaleItemSerializer(serializers.ModelSerializer):
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

    def get_subtotal(self, sale_item):
        return str(sale_item.subtotal)

    def get_profit(self, sale_item):
        return str(sale_item.profit)


class SalePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalePayment
        fields = ['id', 'sale', 'cash_shift', 'amount', 'created_at']
        read_only_fields = ['id', 'created_at']


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    payments = SalePaymentSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True, allow_null=True)
    customer_phone = serializers.SerializerMethodField()
    balance_due = serializers.SerializerMethodField()
    cashier = serializers.SerializerMethodField()

    class Meta:
        model = Sale
        fields = [
            'id', 'transaction_id', 'store', 'cash_shift', 'cashier',
            'customer', 'customer_name', 'customer_phone', 'status',
            'sale_type', 'total_amount', 'amount_paid', 'amount_tendered',
            'change', 'balance_due', 'items', 'payments', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'balance_due', 'cashier']

    def get_balance_due(self, sale):
        return str(sale.balance_due)

    def get_customer_phone(self, sale):
        return getattr(sale.customer, 'phone', '') if sale.customer else ''

    def get_cashier(self, sale):
        if not sale.cash_shift or not sale.cash_shift.opened_by:
            return None

        user = sale.cash_shift.opened_by
        return {
            'id': str(user.id),
            'name': user.first_name or user.name or user.username,
            'username': user.username,
        }


class SaleCreateItemSerializer(serializers.Serializer):
    product = serializers.UUIDField(allow_null=True, required=False)
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)


class SaleCreateSerializer(serializers.ModelSerializer):
    items = SaleCreateItemSerializer(many=True, write_only=True, required=False)
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id', 'transaction_id', 'store', 'cash_shift', 'customer',
            'status', 'sale_type', 'total_amount', 'amount_paid',
            'amount_tendered', 'change', 'items'
        ]

    def validate(self, sale_data):
        sale_type = sale_data.get('sale_type', Sale.SaleType.CASH)
        customer = sale_data.get('customer')

        if sale_type in [Sale.SaleType.CREDIT, Sale.SaleType.LAYAWAY]:
            if not customer or customer.name == 'Venta de Mostrador (General)':
                raise serializers.ValidationError(
                    "No se puede otorgar credito al publico general"
                )
        return sale_data

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])

        with transaction.atomic():
            sale = super().create(validated_data)
            self._set_tendered_amount(sale, validated_data)

            from apps.inventory.models import InventoryMovement
            from apps.products.models import Product

            request = self.context.get('request') if hasattr(self, 'context') else None
            user = getattr(request, 'user', None)
            authenticated_user = user if user and user.is_authenticated else None

            if sale.amount_paid > 0:
                SalePayment.objects.create(
                    sale=sale,
                    cash_shift=sale.cash_shift,
                    amount=sale.amount_paid,
                    cashier=authenticated_user,
                    payment_method=SalePayment.PaymentMethod.CASH,
                )

            for item_data in items_data:
                self._create_sale_item(sale, item_data, Product, InventoryMovement, authenticated_user)

        return sale

    def _set_tendered_amount(self, sale, sale_data):
        amount_tendered = sale_data.get('amount_tendered') or sale_data.get('amount_paid')
        if amount_tendered is None:
            return

        total_amount = Decimal(str(sale.total_amount))
        tendered_amount = Decimal(str(amount_tendered))
        sale.amount_tendered = amount_tendered
        sale.change = tendered_amount - total_amount if tendered_amount > total_amount else Decimal('0')
        sale.save(update_fields=['amount_tendered', 'change'])

    def _create_sale_item(self, sale, item_data, product_model, movement_model, user):
        product_id = item_data.get('product')
        quantity = int(item_data.get('quantity') or 0)
        unit_price = item_data.get('unit_price')

        product = None
        unit_cost = Decimal('0')
        if product_id:
            try:
                product = product_model.objects.select_for_update().get(id=product_id)
                unit_cost = product.base_cost or Decimal('0')
            except product_model.DoesNotExist:
                product = None

        SaleItem.objects.create(
            sale=sale,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            unit_cost=unit_cost,
        )

        if not product:
            return

        stock_before = product.current_stock or 0
        stock_after = max(0, stock_before - quantity)
        product.current_stock = stock_after
        product.save(update_fields=['current_stock'])

        movement_model.objects.create(
            product=product,
            user=user,
            movement_type=movement_model.MovementType.SALE,
            quantity=quantity * -1,
            stock_before=stock_before,
            stock_after=stock_after,
        )
