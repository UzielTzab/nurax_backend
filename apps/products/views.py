"""
Vistas para la app Products.
ARCHITECTURE_V2: Catálogo, categorías, proveedores y códigos.
"""
import uuid
from django.db import transaction as db_transaction
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from drf_spectacular.utils import extend_schema_view, extend_schema
from .models import Product, Category, Supplier, ProductPackaging, ProductCode
from .serializers import (
    ProductSerializer, CategorySerializer, SupplierSerializer,
    ProductPackagingSerializer, ProductCodeSerializer, ProductSimpleSerializer
)


@extend_schema_view(
    list=extend_schema(tags=["Categorías"]),
    create=extend_schema(tags=["Categorías"]),
    retrieve=extend_schema(tags=["Categorías"]),
    update=extend_schema(tags=["Categorías"]),
    partial_update=extend_schema(tags=["Categorías"]),
    destroy=extend_schema(tags=["Categorías"]),
)
class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet para categorías de una tienda."""

    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_queryset(self):
        """Obtener categorías filtradas por tienda.
        
        Si viene store_id como query param, filtra por esa tienda.
        Si no viene, filtra por todas las tiendas del usuario autenticado.
        """
        from apps.accounts.models import StoreMembership

        store_id = self.request.query_params.get('store_id')
        if store_id:
            return Category.objects.filter(store_id=store_id)

        # Fallback: todas las tiendas del usuario
        store_ids = StoreMembership.objects.filter(
            user=self.request.user
        ).values_list('store_id', flat=True)
        return Category.objects.filter(store_id__in=store_ids)

    def perform_create(self, serializer):
        """Asignar tienda al crear categoría."""
        store_id = self.request.data.get('store')
        if store_id:
            serializer.save()


@extend_schema_view(
    list=extend_schema(tags=["Proveedores"]),
    create=extend_schema(tags=["Proveedores"]),
    retrieve=extend_schema(tags=["Proveedores"]),
    update=extend_schema(tags=["Proveedores"]),
    partial_update=extend_schema(tags=["Proveedores"]),
    destroy=extend_schema(tags=["Proveedores"]),
)
class SupplierViewSet(viewsets.ModelViewSet):
    """ViewSet para proveedores de una tienda."""

    permission_classes = [IsAuthenticated]
    serializer_class = SupplierSerializer
    queryset = Supplier.objects.all()

    def get_queryset(self):
        """Obtener proveedores filtrados por tienda.

        Si viene store_id como query param, filtra por esa tienda.
        Si no viene, filtra por todas las tiendas del usuario autenticado.
        Este comportamiento es simétrico al de ProductViewSet.
        """
        from apps.accounts.models import StoreMembership

        store_id = self.request.query_params.get('store_id')
        if store_id:
            return Supplier.objects.filter(store_id=store_id)

        # Fallback: todas las tiendas donde el usuario tiene membresía
        store_ids = StoreMembership.objects.filter(
            user=self.request.user
        ).values_list('store_id', flat=True)
        return Supplier.objects.filter(store_id__in=store_ids).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """Crear proveedor asignando automáticamente la tienda del usuario."""
        from apps.accounts.models import StoreMembership

        payload = request.data.copy()
        store_id = payload.get('store')

        # Si no se envía store, inferir la tienda por membresía del usuario
        if not store_id:
            membership = StoreMembership.objects.filter(user=request.user).select_related('store').first()
            if membership:
                store_id = str(membership.store_id)
                payload['store'] = store_id

        if not store_id:
            return Response(
                {'error': 'No se encontró una tienda asociada al usuario'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@extend_schema_view(
    list=extend_schema(tags=["Productos"]),
    create=extend_schema(tags=["Productos"]),
    retrieve=extend_schema(tags=["Productos"]),
    update=extend_schema(tags=["Productos"]),
    partial_update=extend_schema(tags=["Productos"]),
    destroy=extend_schema(tags=["Productos"]),
    low_stock=extend_schema(tags=["Productos"]),
    out_of_stock=extend_schema(tags=["Productos"]),
    movements=extend_schema(tags=["Productos"]),
)
class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de productos."""

    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filterset_fields = ['store', 'category', 'supplier']
    # Permitimos buscar por nombre y por códigos asociados (ean13, upc, etc.)
    search_fields = ['name', 'codes__code']
    ordering_fields = ['name', 'created_at', 'current_stock', 'sale_price']
    ordering = ['-created_at']

    @staticmethod
    def _is_valid_uuid(value):
        if value in (None, '', 'null', 'undefined'):
            return False
        try:
            uuid.UUID(str(value))
            return True
        except (ValueError, TypeError, AttributeError):
            return False

    def _normalize_payload(self, data):
        """Normaliza payload legacy para crear/editar productos sin errores por campos antiguos."""
        payload = data.copy()

        # Legacy frontend puede enviar "stock" en lugar de "current_stock".
        if payload.get('current_stock') in (None, '') and payload.get('stock') not in (None, ''):
            payload['current_stock'] = payload.get('stock')

        # "sku" no existe en el modelo Product V2 (se maneja en ProductCode).
        payload.pop('sku', None)

        # category/supplier deben ser UUID en V2. Si llegan como legacy int/string inválido, omitir.
        category = payload.get('category')
        if category in (None, '', 'null', 'undefined') or not self._is_valid_uuid(category):
            payload.pop('category', None)

        supplier = payload.get('supplier')
        if supplier in (None, '', 'null', 'undefined') or not self._is_valid_uuid(supplier):
            payload.pop('supplier', None)

        # Limpiar campo legacy si vino junto al payload.
        payload.pop('stock', None)
        return payload

    def get_queryset(self):
        """Filtrar productos por membresías del usuario (y opcionalmente por store_id)."""
        from apps.accounts.models import StoreMembership

        requested_store_id = self.request.query_params.get('store_id')
        memberships = StoreMembership.objects.filter(user=self.request.user)

        if requested_store_id:
            is_member = memberships.filter(store_id=requested_store_id).exists()
            is_admin = getattr(self.request.user, 'role', None) == 'admin'
            if not is_admin and not is_member:
                return Product.objects.none()
            return Product.objects.filter(store_id=requested_store_id).select_related(
                'category', 'supplier'
            ).prefetch_related('packagings', 'codes')

        store_ids = memberships.values_list('store_id', flat=True)
        return Product.objects.filter(store_id__in=store_ids).select_related(
            'category', 'supplier'
        ).prefetch_related('packagings', 'codes')

    def perform_create(self, serializer):
        """Asignar tienda automáticamente y validar acceso del usuario."""
        from apps.accounts.models import StoreMembership

        store = serializer.validated_data.get('store')
        memberships = StoreMembership.objects.filter(user=self.request.user)
        is_admin = getattr(self.request.user, 'role', None) == 'admin'

        if store is None:
            membership = memberships.select_related('store').first()
            if not membership:
                raise ValidationError({'store': 'No tienes una tienda asociada para crear productos.'})
            serializer.save(store=membership.store)
            return

        is_member = memberships.filter(store=store).exists()
        if not is_admin and not is_member:
            raise PermissionDenied('No tienes acceso a esta tienda.')

        serializer.save()

    def create(self, request, *args, **kwargs):
        # Combinar request.data (texto) + request.FILES (archivos) en un QueryDict mutable
        # para que el serializer reciba image_file directamente.
        data = request.data.copy()
        if 'image_file' in request.FILES:
            data['image_file'] = request.FILES['image_file']
        normalized = self._normalize_payload(data)
        serializer = self.get_serializer(data=normalized)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """
        Actualiza el producto. Si current_stock cambió, registra un INVENTORY_MOVEMENT
        de tipo ADJUSTMENT dentro de la misma transacción de base de datos.

        Regla crítica: el UPDATE en PRODUCTO y el INSERT en INVENTORY_MOVEMENT ocurren
        juntos o ninguno (transacción atómica).
        """
        from apps.inventory.models import InventoryMovement

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        if 'image_file' in request.FILES:
            data['image_file'] = request.FILES['image_file']
        normalized = self._normalize_payload(data)

        # Capturar stock previo ANTES de guardar
        stock_before = instance.current_stock
        new_stock_raw = normalized.get('current_stock')

        with db_transaction.atomic():
            serializer = self.get_serializer(instance, data=normalized, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            updated_instance = serializer.instance

            # Si el payload incluía current_stock y cambió → crear ADJUSTMENT
            if new_stock_raw is not None:
                try:
                    stock_after = int(new_stock_raw)
                except (TypeError, ValueError):
                    stock_after = stock_before

                if stock_after != stock_before:
                    delta = stock_after - stock_before
                    InventoryMovement.objects.create(
                        product=updated_instance,
                        user=request.user,
                        movement_type=InventoryMovement.MovementType.ADJUSTMENT,
                        quantity=delta,
                        stock_before=stock_before,
                        stock_after=stock_after,
                    )

        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """Elimina múltiples productos por sus IDs."""
        ids = request.data.get('ids', [])
        if not ids or not isinstance(ids, list):
            return Response(
                {'error': 'Se requiere una lista de IDs válida.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        qs = self.get_queryset().filter(id__in=ids)
        deleted_count, _ = qs.delete()
        return Response(
            {'deleted': deleted_count},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Productos con stock bajo (< 10 unidades)."""
        threshold = int(request.query_params.get('threshold', 10))
        products = self.get_queryset().filter(current_stock__lt=threshold)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """Productos sin stock."""
        products = self.get_queryset().filter(current_stock=0)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='movements')
    def movements(self, request, pk=None):
        """
        Retorna los últimos 20 movimientos de inventario del producto.
        GET /api/v1/products/products/{id}/movements/
        """
        from apps.inventory.models import InventoryMovement
        from apps.inventory.serializers import InventoryMovementSerializer

        product = self.get_object()
        qs = InventoryMovement.objects.filter(
            product=product
        ).select_related('user').order_by('-created_at')[:20]
        serializer = InventoryMovementSerializer(qs, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(tags=["Empaques de Producto"]),
    create=extend_schema(tags=["Empaques de Producto"]),
    retrieve=extend_schema(tags=["Empaques de Producto"]),
    update=extend_schema(tags=["Empaques de Producto"]),
    partial_update=extend_schema(tags=["Empaques de Producto"]),
    destroy=extend_schema(tags=["Empaques de Producto"]),
)
class ProductPackagingViewSet(viewsets.ModelViewSet):
    """ViewSet para empaques de producto."""

    permission_classes = [IsAuthenticated]
    serializer_class = ProductPackagingSerializer
    queryset = ProductPackaging.objects.all()

    def get_queryset(self):
        """Obtener empaques de un producto específico."""
        product_id = self.request.query_params.get('product_id')
        if product_id:
            return ProductPackaging.objects.filter(product_id=product_id)
        return ProductPackaging.objects.none()


@extend_schema_view(
    list=extend_schema(tags=["Códigos de Producto"]),
    create=extend_schema(tags=["Códigos de Producto"]),
    retrieve=extend_schema(tags=["Códigos de Producto"]),
    update=extend_schema(tags=["Códigos de Producto"]),
    partial_update=extend_schema(tags=["Códigos de Producto"]),
    destroy=extend_schema(tags=["Códigos de Producto"]),
)
class ProductCodeViewSet(viewsets.ModelViewSet):
    """ViewSet para códigos de producto (QR, EAN13, etc)."""

    permission_classes = [IsAuthenticated]
    serializer_class = ProductCodeSerializer
    queryset = ProductCode.objects.all()

    def get_queryset(self):
        """Obtener códigos de un producto específico."""
        product_id = self.request.query_params.get('product_id')
        if product_id:
            return ProductCode.objects.filter(product_id=product_id)
        return ProductCode.objects.none()
