"""
Vistas para la app Inventory.
ARCHITECTURE_V2: Movimientos de inventario (Kárdex).
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import InventoryMovement
from .serializers import InventoryMovementSerializer


class InventoryMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para movimientos de inventario (Kárdex) - Solo lectura."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = InventoryMovementSerializer
    queryset = InventoryMovement.objects.all()
    filterset_fields = ['product', 'movement_type', 'created_at']
    search_fields = ['product__name']
    ordering_fields = ['created_at', 'product']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Obtener movimientos de inventario de tiendas del usuario."""
        from accounts.models import StoreMembership
        stores = StoreMembership.objects.filter(
            user=self.request.user
        ).values_list('store_id', flat=True)
        return InventoryMovement.objects.filter(
            product__store_id__in=stores
        ).select_related('product', 'user')
