"""
Configuración de admin para la app Inventory - ARCHITECTURE_V2.
"""
from django.contrib import admin
from .models import InventoryMovement


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'stock_before', 'stock_after', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['product__name', 'user__email']
    readonly_fields = ['id', 'created_at']
    fieldsets = (
        ('Información', {'fields': ('id', 'product', 'user', 'movement_type', 'quantity')}),
        ('Stock', {'fields': ('stock_before', 'stock_after')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )
    
    def has_add_permission(self, request):
        """Prevenir creación manual - solo auto-creación."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevenir eliminación - auditoría inmutable."""
        return False
