"""
Vistas para la app Sales.
ARCHITECTURE_V2: Ventas, items y pagos.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Sale, SaleItem, SalePayment
from .serializers import SaleSerializer, SaleItemSerializer, SalePaymentSerializer, SaleCreateSerializer


class SaleViewSet(viewsets.ModelViewSet):
    """ViewSet para ventas."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = SaleSerializer
    queryset = Sale.objects.all()
    filterset_fields = ['store', 'status', 'cash_shift']
    search_fields = ['id']
    ordering_fields = ['created_at', 'total_amount', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Obtener ventas de tiendas donde el usuario es miembro."""
        from accounts.models import StoreMembership
        stores = StoreMembership.objects.filter(
            user=self.request.user
        ).values_list('store_id', flat=True)
        return Sale.objects.filter(store_id__in=stores)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SaleCreateSerializer
        return self.serializer_class
    
    @action(detail=False, methods=['get'])
    def pending_payments(self, request):
        """Ventas con pagos pendientes (crédito)."""
        sales = self.get_queryset().filter(status__in=['partial'])
        serializer = self.get_serializer(sales, many=True)
        return Response(serializer.data)
    
    @transaction.atomic
    def perform_create(self, serializer):
        """Crear venta."""
        serializer.save()


class SaleItemViewSet(viewsets.ModelViewSet):
    """ViewSet para items de venta."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = SaleItemSerializer
    queryset = SaleItem.objects.all()
    
    def get_queryset(self):
        """Obtener items de ventas del usuario."""
        from accounts.models import StoreMembership
        stores = StoreMembership.objects.filter(
            user=self.request.user
        ).values_list('store_id', flat=True)
        return SaleItem.objects.filter(sale__store_id__in=stores)


class SalePaymentViewSet(viewsets.ModelViewSet):
    """ViewSet para pagos de venta."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = SalePaymentSerializer
    queryset = SalePayment.objects.all()
    
    def get_queryset(self):
        """Obtener pagos de ventas del usuario."""
        from accounts.models import StoreMembership
        stores = StoreMembership.objects.filter(
            user=self.request.user
        ).values_list('store_id', flat=True)
        return SalePayment.objects.filter(sale__store_id__in=stores)
    
    @transaction.atomic
    def perform_create(self, serializer):
        """Crear pago y actualizar estado de venta."""
        payment = serializer.save()
        sale = payment.sale
        sale.amount_paid += payment.amount
        
        # Actualizar estado si se pagó completamente
        if sale.amount_paid >= sale.total_amount:
            sale.status = Sale.Status.PAID
        elif sale.amount_paid > 0:
            sale.status = Sale.Status.PARTIAL
        
        sale.save()
