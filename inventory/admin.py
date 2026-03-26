"""
Configuración de admin para la app Inventory.
"""
from django.contrib import admin
from .models import InventoryTransaction, InventoryMovement


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ['product', 'transaction_type', 'quantity', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['product__name']


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'total_cost', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['product__name']
