"""
Vistas para la app Sales.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Sale, SaleItem, SalePayment
from .serializers import SaleSerializer, SaleItemSerializer, SalePaymentSerializer


class SaleViewSet(viewsets.ModelViewSet):
    """ViewSet para ventas."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = SaleSerializer
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'total']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Sale.objects.filter(user=self.request.user).with_payments()
    
    @action(detail=False, methods=['get'])
    def pending_payments(self, request):
        """Ventas con pagos pendientes."""
        sales = Sale.objects.filter(
            user=request.user,
            status__in=['credit', 'layaway']
        ).with_payments()
        serializer = self.get_serializer(sales, many=True)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SalePaymentViewSet(viewsets.ModelViewSet):
    """ViewSet para pagos de venta."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = SalePaymentSerializer
    
    def get_queryset(self):
        return SalePayment.objects.filter(sale__user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
