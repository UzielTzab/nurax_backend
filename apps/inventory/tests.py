from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import Store, StoreMembership
from apps.inventory.models import InventoryMovement
from apps.products.models import Category, Product

User = get_user_model()


class InventoryMovementModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='inv_user',
            email='inv@example.com',
            password='testpass123',
        )
        self.store = Store.objects.create(name='Inventory Store')
        StoreMembership.objects.create(
            store=self.store,
            user=self.user,
            role=StoreMembership.Role.OWNER,
        )
        self.category = Category.objects.create(store=self.store, name='Electronics')
        self.product = Product.objects.create(
            store=self.store,
            name='Test Product',
            category=self.category,
            current_stock=100,
            base_cost=Decimal('50.00'),
            sale_price=Decimal('99.99'),
        )
        self.movement = InventoryMovement.objects.create(
            product=self.product,
            user=self.user,
            movement_type=InventoryMovement.MovementType.SALE,
            quantity=-5,
            stock_before=100,
            stock_after=95,
        )

    def test_movement_creation(self):
        self.assertEqual(self.movement.quantity, -5)
        self.assertEqual(self.movement.stock_before, 100)
        self.assertEqual(self.movement.stock_after, 95)

    def test_movement_types(self):
        purchase = InventoryMovement.objects.create(
            product=self.product,
            user=self.user,
            movement_type=InventoryMovement.MovementType.PURCHASE,
            quantity=20,
            stock_before=95,
            stock_after=115,
        )

        self.assertEqual(purchase.movement_type, InventoryMovement.MovementType.PURCHASE)

    def test_movement_str_representation(self):
        self.assertIn(InventoryMovement.MovementType.SALE, str(self.movement))
        self.assertIn('Test Product', str(self.movement))
