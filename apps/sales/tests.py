from decimal import Decimal

from django.test import TestCase

from apps.accounts.models import Client, Store
from apps.products.models import Category, Product
from apps.sales.models import Sale, SaleItem, SalePayment


class SaleModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Sales Store')
        self.customer = Client.objects.create(name='John Client')
        self.sale = Sale.objects.create(
            transaction_id='TXN-001',
            store=self.store,
            customer=self.customer,
            status=Sale.Status.PAID,
            sale_type=Sale.SaleType.CASH,
            total_amount=Decimal('499.99'),
            amount_paid=Decimal('499.99'),
        )

    def test_sale_creation(self):
        self.assertEqual(self.sale.transaction_id, 'TXN-001')
        self.assertEqual(self.sale.status, Sale.Status.PAID)
        self.assertEqual(self.sale.total_amount, Decimal('499.99'))

    def test_sale_balance_due_paid(self):
        self.assertEqual(self.sale.balance_due, Decimal('0.00'))

    def test_sale_balance_due_credit(self):
        credit_sale = Sale.objects.create(
            transaction_id='TXN-002',
            store=self.store,
            customer=self.customer,
            status=Sale.Status.PARTIAL,
            sale_type=Sale.SaleType.CREDIT,
            total_amount=Decimal('1000.00'),
            amount_paid=Decimal('250.00'),
        )

        self.assertEqual(credit_sale.balance_due, Decimal('750.00'))

    def test_sale_str_representation(self):
        self.assertIn('Venta', str(self.sale))
        self.assertIn('499.99', str(self.sale))


class SaleItemModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Item Store')
        self.category = Category.objects.create(store=self.store, name='Laptop')
        self.product = Product.objects.create(
            store=self.store,
            name='Product Test',
            category=self.category,
            current_stock=100,
            base_cost=Decimal('60.00'),
            sale_price=Decimal('99.99'),
        )
        self.sale = Sale.objects.create(
            transaction_id='TXN-TEST',
            store=self.store,
            status=Sale.Status.PAID,
            total_amount=Decimal('299.97'),
            amount_paid=Decimal('299.97'),
        )
        self.sale_item = SaleItem.objects.create(
            sale=self.sale,
            product=self.product,
            quantity=3,
            unit_price=Decimal('99.99'),
            unit_cost=Decimal('60.00'),
        )

    def test_sale_item_creation(self):
        self.assertEqual(self.sale_item.quantity, 3)
        self.assertEqual(self.sale_item.unit_price, Decimal('99.99'))
        self.assertEqual(self.sale_item.unit_cost, Decimal('60.00'))

    def test_sale_item_subtotal(self):
        self.assertEqual(self.sale_item.subtotal, Decimal('299.97'))

    def test_sale_item_profit(self):
        self.assertEqual(self.sale_item.profit, Decimal('119.97'))

    def test_sale_item_str_representation(self):
        self.assertIn('Product Test', str(self.sale_item))
        self.assertIn('3', str(self.sale_item))


class SalePaymentModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Payment Store')
        self.sale = Sale.objects.create(
            transaction_id='TXN-PAYMENT',
            store=self.store,
            status=Sale.Status.PARTIAL,
            sale_type=Sale.SaleType.CREDIT,
            total_amount=Decimal('1000.00'),
            amount_paid=Decimal('500.00'),
        )
        self.payment = SalePayment.objects.create(
            sale=self.sale,
            amount=Decimal('500.00'),
            payment_method=SalePayment.PaymentMethod.CASH,
        )

    def test_payment_creation(self):
        self.assertEqual(self.payment.amount, Decimal('500.00'))
        self.assertEqual(self.payment.sale, self.sale)

    def test_payment_str_representation(self):
        self.assertIn('500.00', str(self.payment))

    def test_sale_balance_with_payment_state(self):
        self.assertEqual(self.sale.balance_due, Decimal('500.00'))
