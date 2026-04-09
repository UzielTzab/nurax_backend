"""
Configuración de admin para la app Expenses - ARCHITECTURE_V2.
"""
from django.contrib import admin
from .models import CashShift, CashMovement, ExpenseCategory, Expense, PurchaseOrder, PurchaseOrderItem


class CashMovementInline(admin.TabularInline):
    model = CashMovement
    extra = 1
    readonly_fields = ['id', 'created_at']
    fields = ['movement_type', 'amount', 'reason', 'id', 'created_at']


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    readonly_fields = ['id', 'created_at']
    fields = ['product', 'quantity', 'unit_cost', 'id']


@admin.register(CashShift)
class CashShiftAdmin(admin.ModelAdmin):
    list_display = ['store', 'opened_by', 'opened_at', 'closed_at', 'starting_cash', 'is_open']
    list_filter = ['store', 'opened_at', 'closed_at']
    search_fields = ['store__name', 'opened_by__email']
    readonly_fields = ['id', 'is_open', 'created_at', 'updated_at']
    inlines = [CashMovementInline]
    fieldsets = (
        ('Información', {'fields': ('id', 'store', 'opened_by', 'is_open')}),
        ('Tiempos', {'fields': ('opened_at', 'closed_at')}),
        ('Montos', {'fields': ('starting_cash',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(CashMovement)
class CashMovementAdmin(admin.ModelAdmin):
    list_display = ['cash_shift', 'movement_type', 'amount', 'reason', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['cash_shift__store__name', 'reason']
    readonly_fields = ['id', 'created_at']
    fieldsets = (
        ('Información', {'fields': ('id', 'cash_shift', 'movement_type', 'amount', 'reason')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'store', 'created_at']
    list_filter = ['store', 'created_at']
    search_fields = ['name', 'store__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Información', {'fields': ('id', 'store', 'name')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['store', 'category', 'amount', 'payment_method', 'created_at']
    list_filter = ['category', 'payment_method', 'created_at']
    search_fields = ['store__name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Información', {'fields': ('id', 'store', 'category', 'description')}),
        ('Monto', {'fields': ('amount',)}),
        ('Relaciones', {'fields': ('cash_shift', 'purchase_order')}),
        ('Pago', {'fields': ('payment_method',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['store', 'supplier', 'status', 'total_cost', 'created_at']
    list_filter = ['status', 'store', 'created_at']
    search_fields = ['store__name', 'supplier__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [PurchaseOrderItemInline]
    fieldsets = (
        ('Información', {'fields': ('id', 'store', 'supplier', 'status')}),
        ('Monto', {'fields': ('total_cost',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ['purchase_order', 'product', 'quantity', 'unit_cost', 'created_at']
    list_filter = ['created_at']
    search_fields = ['purchase_order__id', 'product__name']
    readonly_fields = ['id', 'created_at']
    fieldsets = (
        ('Información', {'fields': ('id', 'purchase_order', 'product', 'quantity')}),
        ('Monto', {'fields': ('unit_cost',)}),
        ('Timestamps', {'fields': ('created_at',)}),
    )
