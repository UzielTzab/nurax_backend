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


class ClientViewSetTest(TestCase):
    """Tests para el ClientViewSet - creación automática de usuario."""
    
    def setUp(self):
        """Crear un usuario admin para hacer requests."""
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            name='Admin'
        )
    
    def test_client_creation_creates_user_automatically(self):
        """Verificar que crear un cliente crea automáticamente su usuario."""
        initial_user_count = User.objects.count()
        initial_client_count = Client.objects.count()
        
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken
        
        # Crear token para el admin
        refresh = RefreshToken.for_user(self.admin_user)
        api_client = APIClient()
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Crear cliente vía API (usar ruta correcta con v1)
        response = api_client.post('/api/v1/accounts/clients/', {
            'name': 'Juan García',
            'email': 'juan@example.com',
            'company': 'García Inc',
            'plan': 'basico'
        }, format='json')
        
        # Verificar respuesta
        self.assertEqual(response.status_code, 201, f"Error: {response.data}")
        
        # Verificar que se crearon ambos
        self.assertEqual(User.objects.count(), initial_user_count + 1)
        self.assertEqual(Client.objects.count(), initial_client_count + 1)
        
        # Verificar que el usuario se creó correctamente
        new_user = User.objects.get(email='juan@example.com')
        self.assertEqual(new_user.name, 'Juan García')
        self.assertEqual(new_user.username, 'juan@example.com')
        self.assertEqual(new_user.role, 'cliente')
        
        # Verificar que la contraseña es 'nurax123'
        self.assertTrue(new_user.check_password('nurax123'))
        
        # Verificar que el cliente está asociado al usuario
        client = Client.objects.get(email='juan@example.com')
        self.assertEqual(client.user, new_user)
    
    def test_client_user_cannot_have_duplicate_email(self):
        """Verificar que no se puede crear cliente con email duplicado."""
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken
        
        # Crear usuario existente
        User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            password='pass123',
            name='Existing User'
        )
        
        # Intentar crear cliente con ese email
        refresh = RefreshToken.for_user(self.admin_user)
        api_client = APIClient()
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = api_client.post('/api/v1/accounts/clients/', {
            'name': 'Another User',
            'email': 'existing@example.com',
            'company': 'Some Company',
            'plan': 'basico'
        }, format='json')
        
        # Debe fallar
        self.assertEqual(response.status_code, 400)
    
    def test_client_email_unique_in_client_table(self):
        """Verificar que el email es único en la tabla de clientes."""
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken
        
        # Crear primer cliente
        Client.objects.create(
            name='First Client',
            email='duplicate@example.com',
            company='Company 1'
        )
        
        # Intentar crear otro cliente con mismo email
        refresh = RefreshToken.for_user(self.admin_user)
        api_client = APIClient()
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = api_client.post('/api/v1/accounts/clients/', {
            'name': 'Second Client',
            'email': 'duplicate@example.com',
            'company': 'Company 2',
            'plan': 'basico'
        }, format='json')
        
        # Debe fallar
        self.assertEqual(response.status_code, 400)
