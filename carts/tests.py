"""
Tests para la app Carts.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from accounts.models import Store
from products.models import Product, Category, Supplier
from .models import ActiveCart, CartItem

User = get_user_model()


class ActiveCartTestCase(TestCase):
    """Tests para el carrito activo."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name='Test Store',
            plan='pro'
        )
    
    def test_create_active_cart(self):
        """Test de crear un carrito activo."""
        cart = ActiveCart.objects.create(
            store=self.store,
            user=self.user,
            session_id='test-session-123'
        )
        self.assertEqual(cart.session_id, 'test-session-123')
        self.assertEqual(cart.total_temp, 0)


class CartItemTestCase(TestCase):
    """Tests para items del carrito."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.store = Store.objects.create(name='Test Store')
        self.category = Category.objects.create(
            store=self.store,
            name='Electronics'
        )
        self.product = Product.objects.create(
            store=self.store,
            category=self.category,
            name='Test Product',
            base_cost=10.00,
            sale_price=20.00,
            current_stock=100
        )
        self.cart = ActiveCart.objects.create(
            store=self.store,
            user=self.user,
            session_id='test-session'
        )
    
    def test_create_cart_item(self):
        """Test de crear un item en el carrito."""
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=5,
            unit_price_at_time=20.00
        )
        self.assertEqual(item.quantity, 5)
        self.assertEqual(item.subtotal, 100.00)
