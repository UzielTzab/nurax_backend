"""
Tests para la app Products.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from products.models import Product, Category, Supplier
from decimal import Decimal

User = get_user_model()


class CategoryModelTest(TestCase):
    """Tests para el modelo Category."""
    
    def setUp(self):
        self.category = Category.objects.create(name='Laptop')
    
    def test_category_creation(self):
        """Verificar creación de categoría."""
        self.assertEqual(self.category.name, 'Laptop')
    
    def test_category_unique_name(self):
        """Verificar que el nombre de categoría es único."""
        with self.assertRaises(Exception):
            Category.objects.create(name='Laptop')
    
    def test_category_str_representation(self):
        """Verificar representación en string."""
        self.assertEqual(str(self.category), 'Laptop')


class SupplierModelTest(TestCase):
    """Tests para el modelo Supplier."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='supplier_user',
            email='supplier@example.com',
            password='testpass123',
            name='Supplier User'
        )
        self.supplier = Supplier.objects.create(
            user=self.user,
            name='Tech Supplier Inc',
            email='contact@techsupplier.com',
            phone='+1234567890',
            company='Tech Supplier LLC'
        )
    
    def test_supplier_creation(self):
        """Verificar creación de proveedor."""
        self.assertEqual(self.supplier.name, 'Tech Supplier Inc')
        self.assertEqual(self.supplier.email, 'contact@techsupplier.com')
    
    def test_supplier_str_representation(self):
        """Verificar representación en string."""
        self.assertIn('Tech Supplier Inc', str(self.supplier))


class ProductModelTest(TestCase):
    """Tests para el modelo Product."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='product_user',
            email='product@example.com',
            password='testpass123',
            name='Product User'
        )
        self.category = Category.objects.create(name='Laptop')
        self.supplier = Supplier.objects.create(
            user=self.user,
            name='Tech Supplier',
            email='supplier@example.com'
        )
        self.product = Product.objects.create(
            user=self.user,
            name='MacBook Pro 14',
            category=self.category,
            supplier=self.supplier,
            sku='SKU-001',
            stock=50,
            price=Decimal('1299.99')
        )
    
    def test_product_creation(self):
        """Verificar creación de producto."""
        self.assertEqual(self.product.name, 'MacBook Pro 14')
        self.assertEqual(self.product.sku, 'SKU-001')
        self.assertEqual(self.product.stock, 50)
    
    def test_product_status_in_stock(self):
        """Verificar estado cuando hay stock."""
        self.assertEqual(self.product.status, 'in_stock')
    
    def test_product_status_low_stock(self):
        """Verificar estado cuando stock es bajo."""
        self.product.stock = 8
        self.assertEqual(self.product.status, 'low_stock')
    
    def test_product_status_out_of_stock(self):
        """Verificar estado cuando no hay stock."""
        self.product.stock = 0
        self.assertEqual(self.product.status, 'out_of_stock')
    
    def test_product_str_representation(self):
        """Verificar representación en string."""
        expected = 'MacBook Pro 14 (SKU: SKU-001)'
        self.assertEqual(str(self.product), expected)
    
    def test_product_queryset_in_stock(self):
        """Verificar QuerySet para productos en stock."""
        products = Product.objects.in_stock()
        self.assertIn(self.product, products)
    
    def test_product_with_related_optimization(self):
        """Verificar optimización de queries con select_related."""
        products = Product.objects.with_related()
        self.assertEqual(products.count(), 1)
    
    def test_product_invalid_sku_length(self):
        """Verificar validación de SKU."""
        product = Product(
            user=self.user,
            name='Invalid Product',
            category=self.category,
            sku='SK',  # Muy corto
            stock=10,
            price=Decimal('100.00')
        )
        with self.assertRaises(ValidationError):
            product.full_clean()
