"""
Admin para la app Carts - ARCHITECTURE_V2.
"""
from django.contrib import admin
from .models import ActiveCart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    readonly_fields = ['id', 'created_at']
    fields = ['product', 'quantity', 'unit_price_at_time', 'id']


@admin.register(ActiveCart)
class ActiveCartAdmin(admin.ModelAdmin):
    list_display = ['store', 'user', 'session_id', 'total_temp', 'updated_at']
    list_filter = ['store', 'created_at']
    search_fields = ['session_id', 'user__email', 'store__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [CartItemInline]
    fieldsets = (
        ('Información', {'fields': ('id', 'store', 'user', 'session_id')}),
        ('Montos', {'fields': ('total_temp',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'unit_price_at_time', 'created_at']
    list_filter = ['cart__store', 'created_at']
    search_fields = ['product__name', 'cart__session_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Información', {'fields': ('id', 'cart', 'product', 'quantity')}),
        ('Precio', {'fields': ('unit_price_at_time',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
