"""
Modelos para la app Accounts - Usuarios, clientes y perfiles.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Usuario del sistema."""
    
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        CLIENTE = 'cliente', 'Cliente'
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CLIENTE,
        help_text="Rol del usuario en el sistema"
    )
    name = models.CharField(max_length=150, help_text="Nombre completo")
    email = models.EmailField(unique=True, help_text="Email único del usuario")
    avatar_url = models.URLField(
        max_length=800,
        blank=True,
        null=True,
        help_text="URL de avatar en Cloudinary"
    )
    
    class Meta:
        db_table = 'user'
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self) -> str:
        return f"{self.name} ({self.email})"


class Client(models.Model):
    """Empresa/Cliente que contrata el servicio."""
    
    class Plan(models.TextChoices):
        BASICO = 'basico', 'Básico'
        PRO = 'pro', 'Pro'
    
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Usuario asociado al cliente"
    )
    name = models.CharField(max_length=200, help_text="Nombre del cliente")
    email = models.EmailField(unique=True, help_text="Email del cliente")
    company = models.CharField(max_length=200, help_text="Nombre de la empresa")
    plan = models.CharField(
        max_length=15,
        choices=Plan.choices,
        default=Plan.BASICO
    )
    active = models.BooleanField(default=True, help_text="Cliente activo")
    created_at = models.DateTimeField(auto_now_add=True)
    avatar_color = models.CharField(max_length=10, default='#06402B')
    
    class Meta:
        db_table = 'client'
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['active']),
        ]
    
    def __str__(self) -> str:
        return f"{self.company} — {self.name}"


class StoreProfile(models.Model):
    """Configuración de tienda por usuario."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='store_profile'
    )
    company_name = models.CharField(max_length=200, blank=True)
    company_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    logo_url = models.URLField(max_length=800, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'store_profile'
        verbose_name = "Perfil de Tienda"
        verbose_name_plural = "Perfiles de Tienda"
    
    def __str__(self) -> str:
        return f"Perfil de {self.user.name}"


class ActiveSessionCart(models.Model):
    """Carrito activo de sesión."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'active_session_cart'
        verbose_name = "Carrito de Sesión Activa"
    
    def __str__(self) -> str:
        return f"Carrito de {self.user.name}"
