"""
Configuración de admin para la app Products - ARCHITECTURE_V2.
"""
from django.contrib import admin
from .models import Category, Supplier, Product, ProductPackaging, ProductCode


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'store', 'created_at']
    list_filter = ['store', 'created_at']
    search_fields = ['name', 'store__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Información', {'fields': ('id', 'store', 'name')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'store', 'contact_info', 'created_at']
    list_filter = ['store', 'created_at']
    search_fields = ['name', 'store__name', 'contact_info']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Información', {'fields': ('id', 'store', 'name', 'contact_info')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'store', 'category', 'current_stock', 'base_cost', 'sale_price']
    list_filter = ['store', 'category', 'created_at']
    search_fields = ['name', 'store__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Información', {'fields': ('id', 'store', 'category', 'name', 'supplier')}),
        ('Precios', {'fields': ('base_cost', 'sale_price')}),
        ('Inventario', {'fields': ('current_stock',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(ProductPackaging)
class ProductPackagingAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'quantity_per_unit', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'product__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Información', {'fields': ('id', 'product', 'name', 'quantity_per_unit')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(ProductCode)
class ProductCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'product', 'code_type', 'created_at']
    list_filter = ['code_type', 'created_at']
    search_fields = ['code', 'product__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Información', {'fields': ('id', 'product', 'code', 'code_type')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
