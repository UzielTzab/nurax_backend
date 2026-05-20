"""
Vistas para la app Sales.
Arquitectura Final: Ventas, items y pagos.
"""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema_view, extend_schema
from django.db import transaction
from django.db.models import Sum, Avg, Count, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
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
    accounts_receivable=extend_schema(tags=["Ventas"]),
)
class SaleViewSet(viewsets.ModelViewSet):
    """ViewSet para ventas."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = SaleSerializer
    queryset = Sale.objects.all()
    filter_backends = [DjangoFilterBackend, SaleSearchFilter, OrderingFilter]
    filterset_fields = ['store', 'status', 'cash_shift', 'sale_type']
    search_fields = ['id', 'sale_number', 'transaction_id', 'customer__name', 'items__product__name']
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

    @action(detail=False, methods=['get'], url_path='accounts_receivable')
    def accounts_receivable(self, request):
        """Ventas de credito/apartado para la vista de cuentas por cobrar."""
        include_completed = str(
            request.query_params.get('include_completed', 'false')
        ).lower() in ['1', 'true', 'yes', 'si']

        statuses = [Sale.Status.PARTIAL, Sale.Status.PAID] if include_completed else [Sale.Status.PARTIAL]
        sales = self.get_queryset().filter(
            sale_type__in=[Sale.SaleType.CREDIT, Sale.SaleType.LAYAWAY],
            status__in=statuses,
        )
        sales = self.filter_queryset(sales)

        page = self.paginate_queryset(sales)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

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


class DashboardReportView(APIView):
    """
    Endpoint dedicado para los KPIs del Dashboard.
    Calcula ventas totales, ticket promedio, cuentas por cobrar y top productos.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rango = request.query_params.get('rango', 'hoy')
        
        # Filtro de tienda
        from apps.accounts.models import StoreMembership
        stores = StoreMembership.objects.filter(
            user=request.user
        ).values_list('store_id', flat=True)

        sales_qs = Sale.objects.filter(store_id__in=stores).exclude(status=Sale.Status.CANCELLED)
        
        # Filtrado por fecha considerando la zona horaria del sistema local
        now = timezone.localtime(timezone.now())
        if rango == 'hoy':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            sales_qs = sales_qs.filter(created_at__gte=start_date)
        elif rango == 'semana':
            start_date = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            sales_qs = sales_qs.filter(created_at__gte=start_date)
        elif rango == 'mes':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            sales_qs = sales_qs.filter(created_at__gte=start_date)

        # Agregaciones (Database level)
        kpis = sales_qs.aggregate(
            ventas_totales=Sum('total_amount'),
            ticket_promedio=Avg('total_amount'),
            ventas_completadas=Count('id')
        )
        
        # Cuentas por cobrar
        cuentas_qs = sales_qs.filter(sale_type__in=[Sale.SaleType.CREDIT, Sale.SaleType.LAYAWAY], status=Sale.Status.PARTIAL)
        deuda = cuentas_qs.aggregate(
            total_deuda=Sum(F('total_amount') - F('amount_paid'))
        )
        
        # Top 3 Productos
        items_qs = SaleItem.objects.filter(sale__in=sales_qs)
        top_productos = list(
            items_qs.values(nombre=F('product__name'))
            .annotate(cantidad=Sum('quantity'))
            .order_by('-cantidad')[:3]
        )

        # Datos para gráfico
        grafico_qs = sales_qs.annotate(
            fecha=TruncDate('created_at', tzinfo=timezone.get_current_timezone())
        ).values('fecha').annotate(
            total=Sum('total_amount')
        ).order_by('fecha')
        
        ventas_grafico = [
            {"fecha": item['fecha'].strftime('%Y-%m-%d') if item['fecha'] else "", "total": float(item['total'] or 0)}
            for item in grafico_qs
        ]

        return Response({
            "rango": rango,
            "kpis": {
                "ventas_totales": float(kpis['ventas_totales'] or 0),
                "ticket_promedio": float(kpis['ticket_promedio'] or 0),
                "cuentas_por_cobrar": float(deuda['total_deuda'] or 0),
                "ventas_completadas": kpis['ventas_completadas'] or 0
            },
            "top_productos": top_productos,
            "ventas_grafico": ventas_grafico
        })
