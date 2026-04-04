"""
Configuración de admin para la app Accounts - ARCHITECTURE_V2.
"""
from django.contrib import admin
from .models import User, Store, StoreMembership, Client


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_active']
    list_filter = ['is_active', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Información Personal', {'fields': ('id', 'email', 'first_name', 'last_name')}),
        ('Credenciales', {'fields': ('password',)}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan', 'active', 'created_at']
    list_filter = ['plan', 'active', 'created_at']
    search_fields = ['name', 'tax_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Información', {'fields': ('id', 'name', 'plan', 'tax_id', 'active')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(StoreMembership)
class StoreMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'store', 'role', 'created_at']
    list_filter = ['role', 'store', 'created_at']
    search_fields = ['user__email', 'store__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Relación', {'fields': ('id', 'store', 'user', 'role')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'credit_limit', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Información', {'fields': ('id', 'name', 'credit_limit')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
