from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import Store
from apps.expenses.models import CashShift, Expense, ExpenseCategory

User = get_user_model()


class ExpenseModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Expense Store')
        self.category = ExpenseCategory.objects.create(
            store=self.store,
            name='Servicios',
        )
        self.expense = Expense.objects.create(
            store=self.store,
            category=self.category,
            amount=Decimal('150.00'),
            description='Pago de internet',
            payment_method=Expense.PaymentMethod.CASH,
        )

    def test_expense_creation(self):
        self.assertEqual(self.expense.amount, Decimal('150.00'))
        self.assertEqual(self.expense.category, self.category)
        self.assertEqual(self.expense.store, self.store)

    def test_expense_str_representation(self):
        self.assertIn('Servicios', str(self.expense))
        self.assertIn('150.00', str(self.expense))

    def test_expense_queryset_by_category(self):
        expenses = Expense.objects.by_category(self.category)
        self.assertIn(self.expense, expenses)


class CashShiftModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='cash_user',
            email='cash@example.com',
            password='testpass123',
        )
        self.store = Store.objects.create(name='Cash Store')
        self.shift = CashShift.objects.create(
            store=self.store,
            opened_by=self.user,
            starting_cash=Decimal('1000.00'),
            expected_cash=Decimal('1500.00'),
        )

    def test_cash_shift_creation(self):
        self.assertEqual(self.shift.starting_cash, Decimal('1000.00'))
        self.assertEqual(self.shift.opened_by, self.user)
        self.assertIsNone(self.shift.closed_at)

    def test_cash_shift_open_status(self):
        self.assertTrue(self.shift.is_open)

    def test_cash_shift_str_representation(self):
        self.assertIn('Abierto', str(self.shift))

    def test_cash_shift_queryset_open(self):
        open_shifts = CashShift.objects.open()
        self.assertIn(self.shift, open_shifts)

    def test_cash_shift_queryset_closed(self):
        self.shift.closed_at = timezone.now()
        self.shift.save(update_fields=['closed_at'])

        closed_shifts = CashShift.objects.closed()
        self.assertIn(self.shift, closed_shifts)

    def test_cash_shift_closing(self):
        self.shift.closed_at = timezone.now()
        self.shift.actual_cash = Decimal('1500.00')
        self.shift.difference = Decimal('0.00')
        self.shift.save(update_fields=['closed_at', 'actual_cash', 'difference'])

        self.assertFalse(self.shift.is_open)
        self.assertEqual(self.shift.actual_cash, Decimal('1500.00'))
