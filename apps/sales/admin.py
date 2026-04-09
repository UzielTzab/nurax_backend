"""
Configuración de admin para la app Sales - ARCHITECTURE_V2.
"""
from django.contrib import admin
from .models import Sale, SaleItem, SalePayment


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    readonly_fields = ['id', 'created_at']
    fields = ['product', 'quantity', 'unit_price', 'unit_cost', 'id', 'created_at']


class SalePaymentInline(admin.TabularInline):
    model = SalePayment
    extra = 1
    readonly_fields = ['id', 'created_at']
    fields = ['cash_shift', 'amount', 'id', 'created_at']


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'store', 'status', 'total_amount', 'amount_paid', 'created_at']
    list_filter = ['status', 'store', 'created_at']
    search_fields = ['store__name', 'customer__name']
    readonly_fields = ['id', 'balance_due', 'created_at', 'updated_at']
    inlines = [SaleItemInline, SalePaymentInline]
    fieldsets = (
        ('Información', {'fields': ('id', 'store', 'customer', 'cash_shift', 'status')}),
        ('Montos', {'fields': ('total_amount', 'amount_paid', 'balance_due')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['sale', 'product', 'quantity', 'unit_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['sale__id', 'product__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Información', {'fields': ('id', 'sale', 'product', 'quantity')}),
        ('Precios', {'fields': ('unit_price', 'unit_cost')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(SalePayment)
class SalePaymentAdmin(admin.ModelAdmin):
    list_display = ['sale', 'amount', 'cash_shift', 'created_at']
    list_filter = ['created_at', 'cash_shift']
    search_fields = ['sale__id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Información', {'fields': ('id', 'sale', 'cash_shift', 'amount')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
