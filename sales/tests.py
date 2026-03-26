"""
Tests para la app Sales.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from sales.models import Sale, SaleItem, SalePayment
from products.models import Product, Category
from decimal import Decimal

User = get_user_model()


class SaleModelTest(TestCase):
    """Tests para el modelo Sale."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='sales_user',
            email='sales@example.com',
            password='testpass123',
            name='Sales User'
        )
        self.sale = Sale.objects.create(
            transaction_id='TXN-001',
            user=self.user,
            status='completed',
            total=Decimal('499.99'),
            customer_name='John Client',
            customer_phone='+1234567890'
        )
    
    def test_sale_creation(self):
        """Verificar creación de venta."""
        self.assertEqual(self.sale.transaction_id, 'TXN-001')
        self.assertEqual(self.sale.status, 'completed')
        self.assertEqual(self.sale.total, Decimal('499.99'))
    
    def test_sale_balance_due_completed(self):
        """Verificar saldo adeudado en venta completada."""
        self.assertEqual(self.sale.balance_due, Decimal('0'))
    
    def test_sale_balance_due_credit(self):
        """Verificar saldo adeudado en venta con crédito."""
        credit_sale = Sale.objects.create(
            transaction_id='TXN-002',
            user=self.user,
            status='credit',
            total=Decimal('1000.00')
        )
        # Sin pagos, balance = total
        self.assertEqual(credit_sale.balance_due, Decimal('1000.00'))
    
    def test_sale_str_representation(self):
        """Verificar representación en string."""
        self.assertIn('TXN-001', str(self.sale))
        self.assertIn('499.99', str(self.sale))
    
    def test_sale_queryset_completed(self):
        """Verificar QuerySet para ventas completadas."""
        completed = Sale.objects.completed()
        self.assertIn(self.sale, completed)
    
    def test_sale_queryset_pending(self):
        """Verificar QuerySet para ventas pendientes."""
        pending_sale = Sale.objects.create(
            transaction_id='TXN-003',
            user=self.user,
            status='pending',
            total=Decimal('200.00')
        )
        pending = Sale.objects.pending()
        self.assertIn(pending_sale, pending)


class SaleItemModelTest(TestCase):
    """Tests para el modelo SaleItem."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='sales_user',
            email='sales@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Laptop')
        self.product = Product.objects.create(
            user=self.user,
            name='Product Test',
            category=self.category,
            sku='SKU-TEST',
            stock=100,
            price=Decimal('99.99')
        )
        self.sale = Sale.objects.create(
            transaction_id='TXN-TEST',
            user=self.user,
            status='completed',
            total=Decimal('299.97')
        )
        self.sale_item = SaleItem.objects.create(
            sale=self.sale,
            product=self.product,
            product_name='Product Test',
            quantity=3,
            unit_price=Decimal('99.99')
        )
    
    def test_sale_item_creation(self):
        """Verificar creación de item de venta."""
        self.assertEqual(self.sale_item.quantity, 3)
        self.assertEqual(self.sale_item.unit_price, Decimal('99.99'))
    
    def test_sale_item_subtotal(self):
        """Verificar cálculo de subtotal."""
        expected = 3 * Decimal('99.99')
        self.assertEqual(self.sale_item.subtotal, expected)
    
    def test_sale_item_str_representation(self):
        """Verificar representación en string."""
        self.assertIn('Product Test', str(self.sale_item))
        self.assertIn('3', str(self.sale_item))


class SalePaymentModelTest(TestCase):
    """Tests para el modelo SalePayment."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='sales_user',
            email='sales@example.com',
            password='testpass123'
        )
        self.sale = Sale.objects.create(
            transaction_id='TXN-PAYMENT',
            user=self.user,
            status='credit',
            total=Decimal('1000.00')
        )
        self.payment = SalePayment.objects.create(
            sale=self.sale,
            amount=Decimal('500.00'),
            user=self.user
        )
    
    def test_payment_creation(self):
        """Verificar creación de pago."""
        self.assertEqual(self.payment.amount, Decimal('500.00'))
        self.assertEqual(self.payment.sale, self.sale)
    
    def test_payment_str_representation(self):
        """Verificar representación en string."""
        self.assertIn('500.00', str(self.payment))
        self.assertIn('TXN-PAYMENT', str(self.payment))
    
    def test_sale_balance_with_payments(self):
        """Verificar saldo con pagos."""
        self.assertEqual(self.sale.balance_due, Decimal('500.00'))
    
    def test_multiple_payments(self):
        """Verificar múltiples pagos."""
        SalePayment.objects.create(
            sale=self.sale,
            amount=Decimal('300.00'),
            user=self.user
        )
        SalePayment.objects.create(
            sale=self.sale,
            amount=Decimal('200.00'),
            user=self.user
        )
        # 1000 - (500 + 300 + 200) = 0
        self.assertEqual(self.sale.balance_due, Decimal('0'))
