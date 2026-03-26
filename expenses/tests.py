"""
Tests para la app Expenses.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from expenses.models import Expense, CashShift
from decimal import Decimal

User = get_user_model()


class ExpenseModelTest(TestCase):
    """Tests para el modelo Expense."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='exp_user',
            email='exp@example.com',
            password='testpass123'
        )
        self.expense = Expense.objects.create(
            amount=Decimal('150.00'),
            category='servicios',
            description='Pago de internet',
            user=self.user
        )
    
    def test_expense_creation(self):
        """Verificar creación de gasto."""
        self.assertEqual(self.expense.amount, Decimal('150.00'))
        self.assertEqual(self.expense.category, 'servicios')
    
    def test_expense_categories(self):
        """Verificar categorías de gasto."""
        categories = [choice[0] for choice in Expense.Category.choices]
        self.assertIn('servicios', categories)
        self.assertIn('nomina', categories)
        self.assertIn('proveedores', categories)
    
    def test_expense_str_representation(self):
        """Verificar representación en string."""
        self.assertIn('servicios', str(self.expense))
        self.assertIn('150.00', str(self.expense))
    
    def test_expense_queryset_by_category(self):
        """Verificar QuerySet por categoría."""
        expenses = Expense.objects.by_category('servicios')
        self.assertIn(self.expense, expenses)


class CashShiftModelTest(TestCase):
    """Tests para el modelo CashShift."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='cash_user',
            email='cash@example.com',
            password='testpass123'
        )
        self.shift = CashShift.objects.create(
            user=self.user,
            starting_cash=Decimal('1000.00'),
            expected_cash=Decimal('1500.00')
        )
    
    def test_cash_shift_creation(self):
        """Verificar creación de turno de caja."""
        self.assertEqual(self.shift.starting_cash, Decimal('1000.00'))
        self.assertIsNone(self.shift.closed_at)
    
    def test_cash_shift_open_status(self):
        """Verificar que el turno está abierto."""
        self.assertIsNone(self.shift.closed_at)
    
    def test_cash_shift_str_representation(self):
        """Verificar representación en string."""
        self.assertIn('Abierto', str(self.shift))
    
    def test_cash_shift_queryset_open(self):
        """Verificar QuerySet para turnos abiertos."""
        open_shifts = CashShift.objects.open()
        self.assertIn(self.shift, open_shifts)
    
    def test_cash_shift_queryset_closed(self):
        """Verificar QuerySet para turnos cerrados."""
        from django.utils import timezone
        self.shift.closed_at = timezone.now()
        self.shift.save()
        
        closed_shifts = CashShift.objects.closed()
        self.assertIn(self.shift, closed_shifts)
    
    def test_cash_shift_closing(self):
        """Verificar cierre de turno."""
        from django.utils import timezone
        self.shift.closed_at = timezone.now()
        self.shift.actual_cash = Decimal('1500.00')
        self.shift.difference = Decimal('0.00')
        self.shift.save()
        
        self.assertIsNotNone(self.shift.closed_at)
        self.assertEqual(self.shift.actual_cash, Decimal('1500.00'))
