"""
Configuración de admin para la app Accounts.
"""
from django.contrib import admin
from .models import User, Client, StoreProfile, ActiveSessionCart


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['email', 'name']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['email', 'company', 'plan', 'active']
    list_filter = ['plan', 'active']
    search_fields = ['email', 'company']


@admin.register(StoreProfile)
class StoreProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'company_email']
    search_fields = ['company_name']


@admin.register(ActiveSessionCart)
class ActiveSessionCartAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_id', 'created_at']
    search_fields = ['user__email']
