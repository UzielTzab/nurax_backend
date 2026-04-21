"""
Vistas para la app Expenses.
ARCHITECTURE_V2: Caja, gastos y compras a proveedores.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from drf_spectacular.utils import extend_schema_view, extend_schema
from django.db import transaction
from .models import (
    Expense, CashShift, CashMovement, ExpenseCategory,
    PurchaseOrder, PurchaseOrderItem
)
from .serializers import (
    ExpenseSerializer, CashShiftSerializer, CashMovementSerializer,
    ExpenseCategorySerializer, PurchaseOrderSerializer, PurchaseOrderItemSerializer
)


@extend_schema_view(
    list=extend_schema(tags=["Turnos de Caja"]),
    create=extend_schema(tags=["Turnos de Caja"]),
    retrieve=extend_schema(tags=["Turnos de Caja"]),
    update=extend_schema(tags=["Turnos de Caja"]),
    partial_update=extend_schema(tags=["Turnos de Caja"]),
    destroy=extend_schema(tags=["Turnos de Caja"]),
    open=extend_schema(tags=["Turnos de Caja"]),
    current_open=extend_schema(tags=["Turnos de Caja"]),
    close=extend_schema(tags=["Turnos de Caja"]),
)
class CashShiftViewSet(viewsets.ModelViewSet):
    """ViewSet para turnos de caja."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = CashShiftSerializer
    queryset = CashShift.objects.all()
    filterset_fields = ['store', 'opened_by']
    ordering_fields = ['opened_at', 'closed_at']
    ordering = ['-opened_at']
    
    def get_queryset(self):
        """Obtener turnos de cajas de tiendas del usuario."""
        from apps.accounts.models import StoreMembership
        stores = StoreMembership.objects.filter(
            user=self.request.user
        ).values_list('store_id', flat=True)
        return CashShift.objects.filter(store_id__in=stores)

    def perform_create(self, serializer):
        """Crear turno validando membresía y evitando doble turno abierto por tienda."""
        from apps.accounts.models import StoreMembership

        store = serializer.validated_data.get('store')
        if store is None:
            raise ValidationError({'store': 'store es requerido'})

        is_admin = getattr(self.request.user, 'role', None) == 'admin'
        is_member = StoreMembership.objects.filter(user=self.request.user, store=store).exists()

        if not is_admin and not is_member:
            raise PermissionDenied('No tienes acceso a esta tienda.')

        has_open_shift = CashShift.objects.filter(store=store, closed_at__isnull=True).exists()
        if has_open_shift:
            raise ValidationError({'detail': 'Ya existe un turno abierto para esta tienda.'})

        serializer.save(opened_by=self.request.user)

    @action(detail=False, methods=['post'], url_path='open')
    def open(self, request):
        """Compatibilidad legacy: permite abrir turno vía /cash-shifts/open/."""
        from apps.accounts.models import StoreMembership

        payload = request.data.copy()
        store_id = payload.get('store')

        # Para clientes legacy que solo envían starting_cash, inferimos tienda por membresía.
        if not store_id:
            membership = StoreMembership.objects.filter(user=request.user).select_related('store').first()
            if membership:
                store_id = str(membership.store_id)
                payload['store'] = store_id

        if not store_id:
            return Response(
                {'error': 'store es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['get'])
    def current_open(self, request):
        """Turno abierto actual de la tienda."""
        store_id = request.query_params.get('store_id')
        if not store_id:
            return Response(
                {'error': 'store_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        shift = CashShift.objects.filter(
            store_id=store_id,
            closed_at__isnull=True
        ).first()
        
        if shift:
            serializer = self.get_serializer(shift)
            return Response(serializer.data)
        
        return Response(
            {'error': 'No hay turno abierto'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Cerrar un turno de caja."""
        shift = self.get_object()
        
        if shift.closed_at:
            return Response(
                {'error': 'El turno ya está cerrado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.utils import timezone
        shift.closed_at = timezone.now()
        shift.save()
        
        serializer = self.get_serializer(shift)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(tags=["Movimientos de Caja"]),
    create=extend_schema(tags=["Movimientos de Caja"]),
    retrieve=extend_schema(tags=["Movimientos de Caja"]),
    update=extend_schema(tags=["Movimientos de Caja"]),
    partial_update=extend_schema(tags=["Movimientos de Caja"]),
    destroy=extend_schema(tags=["Movimientos de Caja"]),
)
class CashMovementViewSet(viewsets.ModelViewSet):
    """ViewSet para movimientos de caja."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = CashMovementSerializer
    queryset = CashMovement.objects.all()
    filterset_fields = ['cash_shift', 'movement_type']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Obtener movimientos de tiendas del usuario."""
        from apps.accounts.models import StoreMembership
        stores = StoreMembership.objects.filter(
            user=self.request.user
        ).values_list('store_id', flat=True)
        return CashMovement.objects.filter(cash_shift__store_id__in=stores)


@extend_schema_view(
    list=extend_schema(tags=["Categorías de Gasto"]),
    create=extend_schema(tags=["Categorías de Gasto"]),
    retrieve=extend_schema(tags=["Categorías de Gasto"]),
    update=extend_schema(tags=["Categorías de Gasto"]),
    partial_update=extend_schema(tags=["Categorías de Gasto"]),
    destroy=extend_schema(tags=["Categorías de Gasto"]),
)
class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet para categorías de gasto."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = ExpenseCategorySerializer
    queryset = ExpenseCategory.objects.all()
    
    def get_queryset(self):
        """Obtener categorías de tiendas del usuario."""
        from apps.accounts.models import StoreMembership
        stores = StoreMembership.objects.filter(
            user=self.request.user
        ).values_list('store_id', flat=True)
        return ExpenseCategory.objects.filter(store_id__in=stores)


@extend_schema_view(
    list=extend_schema(tags=["Gastos"]),
    create=extend_schema(tags=["Gastos"]),
    retrieve=extend_schema(tags=["Gastos"]),
    update=extend_schema(tags=["Gastos"]),
    partial_update=extend_schema(tags=["Gastos"]),
    destroy=extend_schema(tags=["Gastos"]),
)
class ExpenseViewSet(viewsets.ModelViewSet):
    """ViewSet para gastos operativos."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = ExpenseSerializer
    queryset = Expense.objects.all()
    filterset_fields = ['store', 'category', 'payment_method']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Obtener gastos de tiendas del usuario."""
        from apps.accounts.models import StoreMembership
        stores = StoreMembership.objects.filter(
            user=self.request.user
        ).values_list('store_id', flat=True)
        return Expense.objects.filter(store_id__in=stores)


@extend_schema_view(
    list=extend_schema(tags=["Órdenes de Compra"]),
    create=extend_schema(tags=["Órdenes de Compra"]),
    retrieve=extend_schema(tags=["Órdenes de Compra"]),
    update=extend_schema(tags=["Órdenes de Compra"]),
    partial_update=extend_schema(tags=["Órdenes de Compra"]),
    destroy=extend_schema(tags=["Órdenes de Compra"]),
    mark_received=extend_schema(tags=["Órdenes de Compra"]),
)
class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """ViewSet para órdenes de compra."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = PurchaseOrderSerializer
    queryset = PurchaseOrder.objects.all()
    filterset_fields = ['store', 'supplier', 'status']
    ordering_fields = ['created_at', 'total_cost']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Obtener órdenes de tiendas del usuario."""
        from apps.accounts.models import StoreMembership
        stores = StoreMembership.objects.filter(
            user=self.request.user
        ).values_list('store_id', flat=True)
        return PurchaseOrder.objects.filter(store_id__in=stores)
    
    @action(detail=True, methods=['post'])
    def mark_received(self, request, pk=None):
        """Marcar orden como recibida."""
        order = self.get_object()
        
        if order.status == PurchaseOrder.Status.RECEIVED:
            return Response(
                {'error': 'La orden ya está marcada como recibida'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            order.status = PurchaseOrder.Status.RECEIVED
            order.save()
            
            # Actualizar inventario de los productos
            from apps.inventory.models import InventoryMovement
            for item in order.items.all():
                stock_before = item.product.current_stock
                item.product.current_stock += item.quantity
                item.product.save()
                
                InventoryMovement.objects.create(
                    product=item.product,
                    user=request.user,
                    movement_type=InventoryMovement.MovementType.PURCHASE,
                    quantity=item.quantity,
                    stock_before=stock_before,
                    stock_after=item.product.current_stock
                )
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)

