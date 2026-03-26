"""
Configuración de admin para la app Products.
"""
from django.contrib import admin
from .models import Product, Category, Supplier


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'company', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'company']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'stock', 'price', 'get_status']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'sku']
    readonly_fields = ['created_at', 'updated_at', 'get_status']
    
    @admin.display(description='Estado')
    def get_status(self, obj: "Product") -> str:
        """Retorna el estado del producto."""
        return obj.status
