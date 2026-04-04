"""
Modelos para la app Accounts - Autenticación, usuarios y tiendas.
ARCHITECTURE_V2: Sistema multi-tienda con membresía y roles.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class User(AbstractUser):
    """Usuario del sistema."""
    
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        CLIENTE = 'cliente', 'Cliente'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, help_text="Email único del usuario")
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENTE,
        help_text="Rol del usuario en el sistema"
    )
    avatar_url = models.URLField(blank=True, null=True, help_text="URL de avatar del usuario")
    name = models.CharField(max_length=200, blank=True, help_text="Nombre completo")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        db_table = 'user'
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        indexes = [
            models.Index(fields=['email']),
        ]
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self) -> str:
        return f"{self.username} ({self.email})"


class Store(models.Model):
    """Tienda/Empresa que utiliza Nurax."""
    
    class Plan(models.TextChoices):
        BASICO = 'basico', 'Básico'
        PRO = 'pro', 'Pro'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, help_text="Nombre de la tienda (Ej: Electrónica Nurax)")
    plan = models.CharField(
        max_length=15,
        choices=Plan.choices,
        default=Plan.BASICO
    )
    tax_id = models.CharField(max_length=50, blank=True, help_text="RIF/NIT")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'store'
        verbose_name = "Tienda"
        verbose_name_plural = "Tiendas"
        indexes = [
            models.Index(fields=['active']),
        ]
    
    def __str__(self) -> str:
        return f"{self.name} ({self.plan})"


class StoreMembership(models.Model):
    """Membresía de usuario a tienda con rol."""
    
    class Role(models.TextChoices):
        OWNER = 'owner', 'Propietario'
        MANAGER = 'manager', 'Gerente'
        CASHIER = 'cashier', 'Cajero'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='store_memberships')
    role = models.CharField(
        max_length=15,
        choices=Role.choices,
        help_text="Rol en la tienda"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'store_membership'
        unique_together = [['store', 'user']]
        verbose_name = "Membresía de tienda"
        verbose_name_plural = "Membresías de tienda"
    
    def __str__(self) -> str:
        return f"{self.user.username} - {self.store.name} ({self.role})"


class Client(models.Model):
    """Cliente que compra en la tienda."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, help_text="Nombre del cliente")
    credit_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Límite de crédito"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'client'
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
    
    def __str__(self) -> str:
        return self.name
