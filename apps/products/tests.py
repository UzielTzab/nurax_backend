from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal
from apps.products.models import Product, Category, Supplier, ProductCode, ProductVariation
from apps.accounts.models import Store

User = get_user_model()

class CategoryModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store')
        self.category = Category.objects.create(store=self.store, name='Laptop')
    
    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Laptop')
        self.assertEqual(self.category.store, self.store)
    
    def test_category_str_representation(self):
        self.assertEqual(str(self.category), 'Laptop')


class SupplierModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store')
        self.supplier = Supplier.objects.create(
            store=self.store,
            name='Tech Supplier Inc',
            email='contact@techsupplier.com',
            phone='+1234567890'
        )
    
    def test_supplier_creation(self):
        self.assertEqual(self.supplier.name, 'Tech Supplier Inc')
        self.assertEqual(self.supplier.email, 'contact@techsupplier.com')
        self.assertEqual(self.supplier.store, self.store)
    
    def test_supplier_str_representation(self):
        self.assertIn('Tech Supplier Inc', str(self.supplier))


class ProductModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store')
        self.category = Category.objects.create(store=self.store, name='Laptop')
        self.supplier = Supplier.objects.create(
            store=self.store,
            name='Tech Supplier',
            email='supplier@example.com'
        )
        self.product = Product.objects.create(
            store=self.store,
            name='MacBook Pro 14',
            category=self.category,
            supplier=self.supplier,
            current_stock=50,
            base_cost=Decimal('1000.00'),
            sale_price=Decimal('1299.99')
        )
        self.product_code = ProductCode.objects.create(
            product=self.product,
            code='SKU-001',
            code_type=ProductCode.CodeType.UPC
        )
        self.product_variation = ProductVariation.objects.create(
            product=self.product,
            variation_type=ProductVariation.VariationType.COLOR,
            variation_value='Space Gray'
        )
    
    def test_product_creation(self):
        self.assertEqual(self.product.name, 'MacBook Pro 14')
        self.assertEqual(self.product.current_stock, 50)
        self.assertEqual(self.product.base_cost, Decimal('1000.00'))
        self.assertEqual(self.product.sale_price, Decimal('1299.99'))
        self.assertEqual(self.product.store, self.store)
    
    def test_product_str_representation(self):
        self.assertEqual(str(self.product), 'MacBook Pro 14')
    
    def test_product_code_creation(self):
        self.assertEqual(self.product_code.code, 'SKU-001')
        self.assertEqual(self.product_code.code_type, ProductCode.CodeType.UPC)
        self.assertEqual(str(self.product_code), 'MacBook Pro 14 - upc: SKU-001')
        
    def test_product_variation_creation(self):
        self.assertEqual(self.product_variation.variation_type, ProductVariation.VariationType.COLOR)
        self.assertEqual(self.product_variation.variation_value, 'Space Gray')
        self.assertEqual(str(self.product_variation), 'MacBook Pro 14 - color: Space Gray')


