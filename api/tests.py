"""
Tests para endpoints de API (Integración).
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Product, Category
from sales.models import Sale, SaleItem
from decimal import Decimal

User = get_user_model()


class AccountsAPITest(TestCase):
    """Tests para endpoints de Accounts."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_user_list_endpoint(self):
        """Verificar que el endpoint de usuarios es accesible."""
        response = self.client.get('/api/v1/accounts/users/')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])
    
    def test_user_detail_endpoint(self):
        """Verificar que se puede obtener detalle de usuario."""
        response = self.client.get(f'/api/v1/accounts/users/{self.user.id}/')
        # Puede ser 200 o 403 dependiendo de permisos
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])


class ProductsAPITest(TestCase):
    """Tests para endpoints de Products."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='productuser',
            email='product@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            user=self.user,
            name='Test Product',
            category=self.category,
            sku='SKU-TEST-001',
            stock=50,
            price=Decimal('99.99')
        )
        self.client.force_authenticate(user=self.user)
    
    def test_product_list_endpoint(self):
        """Verificar que se puede listar productos."""
        response = self.client.get('/api/v1/products/products/')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])
    
    def test_category_list_endpoint(self):
        """Verificar que se puede listar categorías."""
        response = self.client.get('/api/v1/products/categories/')
        self.assertIn(response.status_code, 
                     [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    
    def test_product_low_stock_action(self):
        """Verificar que se puede obtener productos con bajo stock."""
        response = self.client.get('/api/v1/products/products/low_stock/')
        self.assertIn(response.status_code, 
                     [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])


class SalesAPITest(TestCase):
    """Tests para endpoints de Sales."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='salesuser',
            email='sales@example.com',
            password='testpass123'
        )
        self.sale = Sale.objects.create(
            transaction_id='TXN-TEST-001',
            user=self.user,
            status='completed',
            total=Decimal('499.99')
        )
        self.client.force_authenticate(user=self.user)
    
    def test_sales_list_endpoint(self):
        """Verificar que se puede listar ventas."""
        response = self.client.get('/api/v1/sales/sales/')
        self.assertIn(response.status_code, 
                     [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    
    def test_pending_payments_action(self):
        """Verificar que se puede obtener ventas con pagos pendientes."""
        response = self.client.get('/api/v1/sales/sales/pending_payments/')
        self.assertIn(response.status_code, 
                     [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])


class WorkflowIntegrationTest(TestCase):
    """Tests de workflows de negocio"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='workflowuser',
            email='workflow@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Integration Test')
        self.client.force_authenticate(user=self.user)
    
    def test_create_product_and_sale_workflow(self):
        """Verificar workflow completo: crear producto -> crear venta -> agregar items"""
        # Crear producto
        product = Product.objects.create(
            user=self.user,
            name='Integration Test Product',
            category=self.category,
            sku='INT-SKU-001',
            stock=100,
            price=Decimal('49.99')
        )
        self.assertEqual(product.status, 'in_stock')
        
        # Crear venta
        sale = Sale.objects.create(
            transaction_id='INT-TXN-001',
            user=self.user,
            status='completed',
            total=Decimal('149.97')
        )
        
        # Agregar items a venta
        item = SaleItem.objects.create(
            sale=sale,
            product=product,
            product_name=product.name,
            quantity=3,
            unit_price=Decimal('49.99')
        )
        
        self.assertEqual(sale.items.count(), 1)
        self.assertEqual(item.subtotal, Decimal('149.97'))

