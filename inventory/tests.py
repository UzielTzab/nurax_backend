"""
Tests para la app Inventory.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from inventory.models import InventoryTransaction, InventoryMovement
from products.models import Product, Category
from expenses.models import CashShift
from decimal import Decimal

User = get_user_model()


class InventoryTransactionModelTest(TestCase):
    """Tests para el modelo InventoryTransaction."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='inv_user',
            email='inv@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            user=self.user,
            name='Test Product',
            category=self.category,
            sku='INV-SKU-001',
            stock=100,
            price=Decimal('99.99')
        )
        self.transaction = InventoryTransaction.objects.create(
            product=self.product,
            transaction_type='in',
            quantity=50,
            reason='Stock initial',
            user=self.user
        )
    
    def test_transaction_creation(self):
        """Verificar creación de transacción."""
        self.assertEqual(self.transaction.quantity, 50)
        self.assertEqual(self.transaction.transaction_type, 'in')
    
    def test_transaction_str_representation(self):
        """Verificar representación en string."""
        self.assertIn('in', str(self.transaction))
        self.assertIn('50', str(self.transaction))
    
    def test_transaction_queryset_entries(self):
        """Verificar QuerySet para entradas."""
        entries = InventoryTransaction.objects.entries()
        self.assertIn(self.transaction, entries)
    
    def test_transaction_queryset_exits(self):
        """Verificar QuerySet para salidas."""
        exit_tx = InventoryTransaction.objects.create(
            product=self.product,
            transaction_type='out',
            quantity=10,
            user=self.user
        )
        exits = InventoryTransaction.objects.exits()
        self.assertIn(exit_tx, exits)


class InventoryMovementModelTest(TestCase):
    """Tests para el modelo InventoryMovement."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='inv_user',
            email='inv@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            user=self.user,
            name='Test Product',
            category=self.category,
            sku='INV-SKU-002',
            stock=100,
            price=Decimal('99.99')
        )
        self.cash_shift = CashShift.objects.create(
            user=self.user,
            starting_cash=Decimal('1000.00')
        )
        self.movement = InventoryMovement.objects.create(
            product=self.product,
            movement_type='sale',
            quantity=5,
            unit_cost=Decimal('50.00'),
            total_cost=Decimal('250.00'),
            cash_shift=self.cash_shift,
            user=self.user
        )
    
    def test_movement_creation(self):
        """Verificar creación de movimiento."""
        self.assertEqual(self.movement.quantity, 5)
        self.assertEqual(self.movement.total_cost, Decimal('250.00'))
    
    def test_movement_types(self):
        """Verificar tipos de movimiento."""
        self.assertEqual(self.movement.movement_type, 'sale')
        
        restock = InventoryMovement.objects.create(
            product=self.product,
            movement_type='restock',
            quantity=20,
            cash_shift=self.cash_shift,
            user=self.user
        )
        self.assertEqual(restock.movement_type, 'restock')
    
    def test_movement_str_representation(self):
        """Verificar representación en string."""
        self.assertIn('sale', str(self.movement))
        self.assertIn('5', str(self.movement))
