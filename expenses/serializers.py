"""
Serializadores para la app Expenses.
"""
from rest_framework import serializers
from .models import Expense, CashShift


class ExpenseSerializer(serializers.ModelSerializer):
    """Serializador para gastos."""
    
    class Meta:
        model = Expense
        fields = ['id', 'amount', 'category', 'description', 'receipt_url', 'supplier', 'date']
        read_only_fields = ['id', 'date']


class CashShiftSerializer(serializers.ModelSerializer):
    """Serializador para turnos de caja."""
    
    class Meta:
        model = CashShift
        fields = [
            'id', 'opened_at', 'closed_at', 'starting_cash',
            'expected_cash', 'actual_cash', 'difference', 'notes'
        ]
        read_only_fields = ['id', 'opened_at']
