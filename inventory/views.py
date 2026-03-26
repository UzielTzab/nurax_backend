"""
Vistas para la app Inventory.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import InventoryTransaction, InventoryMovement
from .serializers import InventoryTransactionSerializer, InventoryMovementSerializer


class InventoryTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet para transacciones de inventario."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = InventoryTransactionSerializer
    filterset_fields = ['transaction_type']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return InventoryTransaction.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class InventoryMovementViewSet(viewsets.ModelViewSet):
    """ViewSet para movimientos de inventario."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = InventoryMovementSerializer
    filterset_fields = ['movement_type']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return InventoryMovement.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
