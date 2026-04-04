"""
Modelos para la app Carts - Carrito de compras en tiempo real con WebSockets.
ARCHITECTURE_V2: Carrito activo y sincronización en tiempo real.
"""
from django.db import models
import uuid


class ActiveCart(models.Model):
    """Carrito activo en tiempo real (se sincroniza por Pusher/WebSockets)."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(
        'accounts.Store',
        on_delete=models.CASCADE,
        related_name='active_carts'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='active_carts',
        help_text="Usuario que está llenando el carrito"
    )
    session_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="Identificador único para Pusher/WebSocket"
    )
    total_temp = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total temporal del carrito"
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'active_cart'
        verbose_name = "Carrito Activo"
        verbose_name_plural = "Carritos Activos"
        indexes = [
            models.Index(fields=['store']),
            models.Index(fields=['user']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self) -> str:
        return f"Carrito {self.session_id} - Total: ${self.total_temp}"


class CartItem(models.Model):
    """Item dentro de un carrito activo."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(
        ActiveCart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(help_text="Cantidad en el carrito")
    unit_price_at_time = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Precio unitario al momento de agregar"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_item'
        verbose_name = "Item del Carrito"
        verbose_name_plural = "Items del Carrito"
        unique_together = [['cart', 'product']]
    
    @property
    def subtotal(self):
        """Subtotal de este item."""
        return self.quantity * self.unit_price_at_time
    
    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity} en carrito {self.cart.session_id}"
