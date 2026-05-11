"""
Vistas para la app Sales.
ARCHITECTURE_V2: Ventas, items y pagos.
"""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema
from django.db import transaction
from .models import Sale, SaleItem, SalePayment
from .serializers import SaleSerializer, SaleItemSerializer, SalePaymentSerializer, SaleCreateSerializer


class SaleSearchFilter(SearchFilter):
    """Normaliza IDs visibles como #NX-A4C054 antes de buscar en Sale.id."""

    def get_search_terms(self, request):
        terms = super().get_search_terms(request)
        normalized_terms = []

        for term in terms:
            cleaned = term.strip()
            cleaned_without_hash = cleaned[1:] if cleaned.startswith('#') else cleaned

            if cleaned_without_hash.upper().startswith('NX-'):
                normalized_terms.append(cleaned_without_hash[3:])
            else:
                normalized_terms.append(cleaned)

        return normalized_terms


@extend_schema_view(
    list=extend_schema(tags=["Ventas"]),
    create=extend_schema(tags=["Ventas"]),
    retrieve=extend_schema(tags=["Ventas"]),
    update=extend_schema(tags=["Ventas"]),
    partial_update=extend_schema(tags=["Ventas"]),
    destroy=extend_schema(tags=["Ventas"]),
    pending_payments=extend_schema(tags=["Ventas"]),
)
class SaleViewSet(viewsets.ModelViewSet):
    """ViewSet para ventas."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = SaleSerializer
    queryset = Sale.objects.all()
    filter_backends = [DjangoFilterBackend, SaleSearchFilter, OrderingFilter]
    filterset_fields = ['store', 'status', 'cash_shift']
    search_fields = ['id', 'transaction_id', 'items__product__name']
    ordering_fields = ['created_at', 'total_amount', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Obtener ventas de tiendas donde el usuario es miembro."""
        from apps.accounts.models import StoreMembership
        stores = StoreMembership.objects.filter(
            user=self.request.user
        ).values_list('store_id', flat=True)
        return Sale.objects.filter(store_id__in=stores).distinct()
    
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

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancelar una venta completada y retornar productos al inventario."""
        sale = self.get_object()
        
        # Validación de RBAC (Role-Based Access Control)
        user = request.user
        role = getattr(user, 'role', 'cliente')
        
        # Verificar rol en StoreMembership si no es admin global
        if role != 'admin':
            from apps.accounts.models import StoreMembership
            membership = StoreMembership.objects.filter(user=user, store=sale.store).first()
            if not membership or membership.role == StoreMembership.Role.CASHIER:
                return Response(
                    {'error': 'No tienes permisos para cancelar ventas. Contacta al administrador.'},
                    status=status.HTTP_403_FORBIDDEN
                )
                
        if sale.status == Sale.Status.CANCELLED:
            return Response(
                {'error': 'La venta ya está cancelada.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        with transaction.atomic():
            sale.status = Sale.Status.CANCELLED
            sale.save()
            
            # Retornar productos al inventario
            from apps.inventory.models import InventoryMovement
            for item in sale.items.all():
                if item.product:
                    stock_before = item.product.current_stock or 0
                    item.product.current_stock = stock_before + item.quantity
                    item.product.save()
                    
                    InventoryMovement.objects.create(
                        product=item.product,
                        user=user,
                        movement_type=InventoryMovement.MovementType.ADJUSTMENT, # o RETURN
                        quantity=item.quantity,
                        stock_before=stock_before,
                        stock_after=item.product.current_stock
                    )
                    
        return Response({'status': 'cancelled'})


@extend_schema_view(
    list=extend_schema(tags=["Items de Venta"]),
    create=extend_schema(tags=["Items de Venta"]),
    retrieve=extend_schema(tags=["Items de Venta"]),
    update=extend_schema(tags=["Items de Venta"]),
    partial_update=extend_schema(tags=["Items de Venta"]),
    destroy=extend_schema(tags=["Items de Venta"]),
)
class SaleItemViewSet(viewsets.ModelViewSet):
    """ViewSet para items de venta."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = SaleItemSerializer
    queryset = SaleItem.objects.all()
    
    def get_queryset(self):
        """Obtener items de ventas del usuario."""
        from apps.accounts.models import StoreMembership
        stores = StoreMembership.objects.filter(
            user=self.request.user
        ).values_list('store_id', flat=True)
        return SaleItem.objects.filter(sale__store_id__in=stores)


@extend_schema_view(
    list=extend_schema(tags=["Pagos"]),
    create=extend_schema(tags=["Pagos"]),
    retrieve=extend_schema(tags=["Pagos"]),
    update=extend_schema(tags=["Pagos"]),
    partial_update=extend_schema(tags=["Pagos"]),
    destroy=extend_schema(tags=["Pagos"]),
)
class SalePaymentViewSet(viewsets.ModelViewSet):
    """ViewSet para pagos de venta."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = SalePaymentSerializer
    queryset = SalePayment.objects.all()
    
    def get_queryset(self):
        """Obtener pagos de ventas del usuario."""
        from apps.accounts.models import StoreMembership
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

