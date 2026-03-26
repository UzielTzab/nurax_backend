"""
Configuración de admin para la app Sales.
"""
from django.contrib import admin
from .models import Sale, SaleItem, SalePayment


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1


class SalePaymentInline(admin.TabularInline):
    model = SalePayment
    extra = 1


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['transaction_id', 'customer_name']
    inlines = [SaleItemInline, SalePaymentInline]


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'quantity', 'unit_price', 'sale']
    search_fields = ['product_name']


@admin.register(SalePayment)
class SalePaymentAdmin(admin.ModelAdmin):
    list_display = ['sale', 'amount', 'created_at']
    list_filter = ['created_at']
    search_fields = ['sale__transaction_id']
