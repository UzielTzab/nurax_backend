"""
Configuración de admin para la app Expenses.
"""
from django.contrib import admin
from .models import Expense, CashShift


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['category', 'amount', 'description', 'date']
    list_filter = ['category', 'date']
    search_fields = ['description']


@admin.register(CashShift)
class CashShiftAdmin(admin.ModelAdmin):
    list_display = ['user', 'opened_at', 'closed_at', 'starting_cash', 'actual_cash']
    list_filter = ['opened_at']
    search_fields = ['user__email']
