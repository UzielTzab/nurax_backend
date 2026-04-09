"""
Vistas para la app Products.
ARCHITECTURE_V2: Catálogo, categorías, proveedores y códigos.
"""
import uuid
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Product, Category, Supplier, ProductPackaging, ProductCode
from .serializers import (
    ProductSerializer, CategorySerializer, SupplierSerializer,
    ProductPackagingSerializer, ProductCodeSerializer, ProductSimpleSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet para categorías de una tienda."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    
    def get_queryset(self):
        """Obtener categorías de la tienda especificada."""
        store_id = self.request.query_params.get('store_id')
        if store_id:
            return Category.objects.filter(store_id=store_id)
        return Category.objects.none()
    
    def perform_create(self, serializer):
        """Asignar tienda al crear categoría."""
        store_id = self.request.data.get('store')
        if store_id:
            serializer.save()


class SupplierViewSet(viewsets.ModelViewSet):
    """ViewSet para proveedores de una tienda."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = SupplierSerializer
    queryset = Supplier.objects.all()
    
    def get_queryset(self):
        """Obtener proveedores de la tienda especificada."""
        store_id = self.request.query_params.get('store_id')
        if store_id:
            return Supplier.objects.filter(store_id=store_id)
        return Supplier.objects.none()


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de productos."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filterset_fields = ['store', 'category', 'supplier']
    search_fields = ['name']
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
            return Product.objects.filter(store_id=requested_store_id)

        store_ids = memberships.values_list('store_id', flat=True)
        return Product.objects.filter(store_id__in=store_ids)

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
        normalized = self._normalize_payload(request.data)
        serializer = self.get_serializer(data=normalized)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        normalized = self._normalize_payload(request.data)
        serializer = self.get_serializer(instance, data=normalized, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
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

