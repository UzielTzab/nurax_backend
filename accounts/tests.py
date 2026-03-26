"""
Tests para la app Accounts.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import Client, StoreProfile, ActiveSessionCart

User = get_user_model()


class UserModelTest(TestCase):
    """Tests para el modelo User."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            name='Test User',
            role='cliente'
        )
    
    def test_user_creation(self):
        """Verificar que se crea un usuario correctamente."""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.role, 'cliente')
        self.assertEqual(str(self.user), 'Test User (test@example.com)')
    
    def test_user_is_authenticated(self):
        """Verificar que el usuario es auténtico."""
        self.assertTrue(self.user.is_active)
    
    def test_admin_user_creation(self):
        """Verificar creación de usuario admin."""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            name='Admin User'
        )
        self.assertEqual(admin.role, 'cliente')
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


class ClientModelTest(TestCase):
    """Tests para el modelo Client."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )
        self.client_obj = Client.objects.create(
            user=self.user,
            name='John Doe',
            email='client@example.com',
            company='Tech Corp',
            plan='basico'
        )
    
    def test_client_creation(self):
        """Verificar que se crea cliente correctamente."""
        self.assertEqual(self.client_obj.company, 'Tech Corp')
        self.assertEqual(self.client_obj.plan, 'basico')
        self.assertTrue(self.client_obj.active)
    
    def test_client_str_representation(self):
        """Verificar representación en string."""
        expected = 'Tech Corp — John Doe'
        self.assertEqual(str(self.client_obj), expected)


class StoreProfileModelTest(TestCase):
    """Tests para el modelo StoreProfile."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='storeuser',
            email='store@example.com',
            password='testpass123',
            name='Store Owner'
        )
        self.profile = StoreProfile.objects.create(
            user=self.user,
            company_name='Mi Tienda',
            company_email='tienda@example.com',
            phone='+1234567890'
        )
    
    def test_store_profile_creation(self):
        """Verificar creación de perfil de tienda."""
        self.assertEqual(self.profile.company_name, 'Mi Tienda')
        self.assertEqual(self.profile.phone, '+1234567890')
    
    def test_one_to_one_relationship(self):
        """Verificar relación one-to-one con User."""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.user.store_profile, self.profile)


class ActiveSessionCartModelTest(TestCase):
    """Tests para el modelo ActiveSessionCart."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='cartuser',
            email='cart@example.com',
            password='testpass123',
            name='Cart User'
        )
        self.cart = ActiveSessionCart.objects.create(
            user=self.user,
            session_id='test-session-123'
        )
    
    def test_cart_creation(self):
        """Verificar creación de carrito."""
        self.assertEqual(self.cart.session_id, 'test-session-123')
        self.assertEqual(self.cart.user, self.user)
    
    def test_cart_str_representation(self):
        """Verificar representación en string."""
        self.assertIn(self.user.name, str(self.cart))
