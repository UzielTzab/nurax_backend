from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import Client, Store, StoreMembership
from apps.accounts.serializers import StoreWithOwnerSerializer

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            name='Test User',
            role=User.Role.CLIENTE,
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.role, User.Role.CLIENTE)
        self.assertEqual(str(self.user), 'testuser (test@example.com)')

    def test_admin_user_creation(self):
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            name='Admin User',
        )

        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


class StoreModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name='Mi Tienda',
            plan=Store.Plan.PRO,
            default_cash=Decimal('500.00'),
        )

    def test_store_creation(self):
        self.assertEqual(self.store.name, 'Mi Tienda')
        self.assertEqual(self.store.plan, Store.Plan.PRO)
        self.assertEqual(self.store.default_cash, Decimal('500.00'))

    def test_store_str_representation(self):
        self.assertEqual(str(self.store), 'Mi Tienda (pro)')


class StoreMembershipModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='testpass123',
        )
        self.store = Store.objects.create(name='Owner Store')
        self.membership = StoreMembership.objects.create(
            store=self.store,
            user=self.user,
            role=StoreMembership.Role.OWNER,
        )

    def test_membership_creation(self):
        self.assertEqual(self.membership.store, self.store)
        self.assertEqual(self.membership.user, self.user)
        self.assertEqual(self.membership.role, StoreMembership.Role.OWNER)

    def test_membership_str_representation(self):
        self.assertIn('owner', str(self.membership))
        self.assertIn('Owner Store', str(self.membership))


class ClientModelTest(TestCase):
    def setUp(self):
        self.client = Client.objects.create(
            name='John Doe',
            credit_limit=Decimal('1500.00'),
        )

    def test_client_creation(self):
        self.assertEqual(self.client.name, 'John Doe')
        self.assertEqual(self.client.credit_limit, Decimal('1500.00'))
        self.assertTrue(self.client.active)

    def test_client_str_representation(self):
        self.assertEqual(str(self.client), 'John Doe')


class StoreWithOwnerSerializerTest(TestCase):
    def test_create_store_owner_and_membership(self):
        serializer = StoreWithOwnerSerializer(data={
            'store_name': 'Nueva Tienda',
            'store_plan': Store.Plan.BASICO,
            'store_tax_id': 'RFC123',
            'owner_email': 'owner@example.com',
            'owner_name': 'Owner User',
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        result = serializer.save()

        user = result['user']
        store = result['store']
        membership = StoreMembership.objects.get(user=user, store=store)

        self.assertEqual(store.name, 'Nueva Tienda')
        self.assertEqual(user.email, 'owner@example.com')
        self.assertEqual(user.role, User.Role.CLIENTE)
        self.assertTrue(user.check_password('nurax123'))
        self.assertEqual(membership.role, StoreMembership.Role.OWNER)
