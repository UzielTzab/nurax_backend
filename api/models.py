from django.db import models
from django.contrib.auth.models import AbstractUser

# ─── USUARIO (extiende el User de Django) ─────────────────────────────────────
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN   = 'admin',   'Administrador'
        CLIENTE = 'cliente', 'Cliente'
    
    role       = models.CharField(max_length=10, choices=Role.choices, default=Role.CLIENTE)
    name       = models.CharField(max_length=150)
    email      = models.EmailField(unique=True)
    # URL de la foto de perfil almacenada en Cloudinary (solo el string, nunca el archivo)
    avatar_url = models.URLField(max_length=800, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self): return f"{self.name} ({self.email})"


# ─── CLIENTE (empresas que contratan el sistema) ──────────────────────────────
class Client(models.Model):
    class Plan(models.TextChoices):
        BASICO     = 'basico',     'Básico'
        PRO        = 'pro',        'Pro'
        ENTERPRISE = 'enterprise', 'Enterprise'
    
    user        = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    name        = models.CharField(max_length=200)
    email       = models.EmailField(unique=True)
    company     = models.CharField(max_length=200)
    plan        = models.CharField(max_length=15, choices=Plan.choices, default=Plan.BASICO)
    active      = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    avatar_color = models.CharField(max_length=10, default='#06402B')
    
    def __str__(self): return f"{self.company} — {self.name}"


# ─── CATEGORÍA (normalizada desde frontend) ───────────────────────────────────
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self): return self.name


# ─── PROVEEDOR ────────────────────────────────────────────────────────────────
class Supplier(models.Model):
    name        = models.CharField(max_length=200)
    email       = models.EmailField(blank=True)
    phone       = models.CharField(max_length=20, blank=True)
    company     = models.CharField(max_length=200, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    
    def __str__(self): return self.name


# ─── PRODUCTO ─────────────────────────────────────────────────────────────────
class Product(models.Model):
    name        = models.CharField(max_length=250)
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    supplier    = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    sku         = models.CharField(max_length=50, unique=True)
    stock       = models.PositiveIntegerField(default=0)
    price       = models.DecimalField(max_digits=12, decimal_places=2)
    # Almacenamos únicamente la URL de la imagen que nos devuelva Cloudinary en formato string
    image_url   = models.URLField(max_length=800, blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    
    def __str__(self): return f"{self.name} ({self.sku})"
    
    @property
    def status(self):
        if self.stock == 0:   return 'out_of_stock'
        if self.stock <= 10:  return 'low_stock'
        return 'in_stock'


# ─── VENTA ────────────────────────────────────────────────────────────────────
class Sale(models.Model):
    class Status(models.TextChoices):
        COMPLETED = 'completed', 'Completada'
        PENDING   = 'pending',   'Pendiente'
        CANCELLED = 'cancelled', 'Cancelada'
        CREDIT    = 'credit',    'Crédito'
        LAYAWAY   = 'layaway',   'Apartado'
        
    transaction_id = models.CharField(max_length=20, unique=True)
    user           = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status         = models.CharField(max_length=15, choices=Status.choices, default=Status.COMPLETED)
    total          = models.DecimalField(max_digits=12, decimal_places=2)
    created_at     = models.DateTimeField(auto_now_add=True)
    
    def __str__(self): return f"{self.transaction_id} — ${self.total}"


# ─── ÍTEM DE VENTA ────────────────────────────────────────────────────────────
class SaleItem(models.Model):
    sale        = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product     = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=250)     # snapshot por si un producto es eliminado
    quantity    = models.PositiveIntegerField()
    unit_price  = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def subtotal(self): return self.quantity * self.unit_price


# ─── PAGOS / ABONOS A VENTAS (CRÉDITO Y APARTADO) ─────────────────────────────
class SalePayment(models.Model):
    sale       = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='payments')
    amount     = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    user       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self): return f"Abono ${self.amount} a {self.sale.transaction_id}"


# ─── KÁRDEX / MOVIMIENTOS DE INVENTARIO ───────────────────────────────────────
class InventoryTransaction(models.Model):
    class TransactionType(models.TextChoices):
        IN         = 'in',         'Entrada (Compra/Proveedor)'
        OUT        = 'out',        'Salida (Venta/Manual)'
        ADJUSTMENT = 'adjustment', 'Ajuste de Inventario'
        WASTE      = 'waste',      'Merma / Dañado'

    product          = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=15, choices=TransactionType.choices)
    quantity         = models.PositiveIntegerField()
    reason           = models.CharField(max_length=255, blank=True)
    user             = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"{self.transaction_type} - {self.quantity} de {self.product.name}"


# ─── GASTOS / EGRESOS ─────────────────────────────────────────────────────────
class Expense(models.Model):
    class Category(models.TextChoices):
        SERVICIOS   = 'servicios',   'Servicios (Luz, Agua, Internet)'
        NOMINA      = 'nomina',      'Nómina / Sueldos'
        PROVEEDORES = 'proveedores', 'Pago a Proveedores'
        VARIOS      = 'varios',      'Gastos Varios'

    amount      = models.DecimalField(max_digits=12, decimal_places=2)
    category    = models.CharField(max_length=20, choices=Category.choices)
    description = models.CharField(max_length=255)
    # URL del comprobante físico (ticket de la luz, etc)
    receipt_url = models.URLField(max_length=800, blank=True, null=True)
    user        = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date        = models.DateField(auto_now_add=True)

    def __str__(self): return f"{self.category} - ${self.amount}"


# ─── CORTE DE CAJA / TURNOS ───────────────────────────────────────────────────
class CashShift(models.Model):
    user          = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    opened_at     = models.DateTimeField(auto_now_add=True)
    closed_at     = models.DateTimeField(null=True, blank=True)
    starting_cash = models.DecimalField(max_digits=12, decimal_places=2)
    expected_cash = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    actual_cash   = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    difference    = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self): return f"Turno de {self.user.name if self.user else 'N/A'} - {self.opened_at.strftime('%Y-%m-%d')}"


# ─── CONFIGURACIÓN DEL NEGOCIO (singleton: solo un registro en el sistema) ────
class StoreProfile(models.Model):
    store_name       = models.CharField(max_length=200, default='Mi Tienda')
    currency_symbol  = models.CharField(max_length=10, default='$')
    address          = models.CharField(max_length=300, blank=True)
    phone            = models.CharField(max_length=30, blank=True)
    ticket_message   = models.TextField(blank=True)
    # Logo subido a Cloudinary, guardado como URL
    logo_url         = models.URLField(max_length=800, blank=True, null=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración del Negocio'

    def __str__(self): return self.store_name

    @classmethod
    def get_solo(cls):
        """Retorna siempre el único registro, creándolo si no existe."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
