import uuid
from django.db import transaction as db_transaction
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from drf_spectacular.utils import extend_schema_view, extend_schema
from django_filters import FilterSet, CharFilter, ChoiceFilter

from .models import (
    Product, Category, Supplier, ProductPackaging, ProductCode, ProductVariation
)
from .serializers import (
    ProductSerializer, CategorySerializer, SupplierSerializer,
    ProductPackagingSerializer, ProductCodeSerializer, ProductSimpleSerializer,
    ProductVariationSerializer
)


class ProductFilterSet(FilterSet):
    stock_status = ChoiceFilter(
        method='filter_stock_status',
        choices=[
            ('low_stock', 'Stock bajo (<5)'),
            ('out_of_stock', 'Sin stock (0)'),
        ]
    )
    
    def filter_stock_status(self, queryset, name, value):
        if value == 'low_stock':
            return queryset.filter(current_stock__gt=0, current_stock__lt=5)
        elif value == 'out_of_stock':
            return queryset.filter(current_stock=0)
        return queryset
    
    class Meta:
        model = Product
        fields = ['store', 'category', 'supplier', 'stock_status']


@extend_schema_view(
    list=extend_schema(tags=["Categorías"]),
    create=extend_schema(tags=["Categorías"]),
    retrieve=extend_schema(tags=["Categorías"]),
    update=extend_schema(tags=["Categorías"]),
    partial_update=extend_schema(tags=["Categorías"]),
    destroy=extend_schema(tags=["Categorías"]),
)
class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_queryset(self):
        from apps.accounts.models import StoreMembership

        store_id = self.request.query_params.get('store_id')
        if store_id:
            return Category.objects.filter(store_id=store_id)

        store_ids = StoreMembership.objects.filter(
            user=self.request.user
        ).values_list('store_id', flat=True)
        return Category.objects.filter(store_id__in=store_ids)

    def perform_create(self, serializer):
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
    permission_classes = [IsAuthenticated]
    serializer_class = SupplierSerializer
    queryset = Supplier.objects.all()

    def get_queryset(self):
        from apps.accounts.models import StoreMembership

        store_id = self.request.query_params.get('store_id')
        if store_id:
            return Supplier.objects.filter(store_id=store_id)

        store_ids = StoreMembership.objects.filter(
            user=self.request.user
        ).values_list('store_id', flat=True)
        return Supplier.objects.filter(store_id__in=store_ids).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        from apps.accounts.models import StoreMembership

        payload = request.data.copy()
        store_id = payload.get('store')

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
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filterset_class = ProductFilterSet
    search_fields = ['name', 'codes__code']
    ordering_fields = ['name', 'created_at', 'current_stock', 'sale_price']
    ordering = ['-created_at']

    def get_queryset(self):
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
            ).prefetch_related('packagings', 'codes', 'variations')

        store_ids = memberships.values_list('store_id', flat=True)
        return Product.objects.filter(store_id__in=store_ids).select_related(
            'category', 'supplier'
        ).prefetch_related('packagings', 'codes', 'variations')

    def perform_create(self, serializer):
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
        data = request.data.copy()
        if 'image_file' in request.FILES:
            data['image_file'] = request.FILES['image_file']

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        from apps.inventory.models import InventoryMovement

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        if 'image_file' in request.FILES:
            data['image_file'] = request.FILES['image_file']

        stock_before = instance.current_stock
        new_stock_raw = data.get('current_stock')

        with db_transaction.atomic():
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            updated_instance = serializer.instance

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
        product_ids = request.data.get('ids', [])
        if not product_ids or not isinstance(product_ids, list):
            return Response(
                {'error': 'Se requiere una lista de IDs válida.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.get_queryset().filter(id__in=product_ids)
        deleted_count, _ = queryset.delete()
        return Response(
            {'deleted': deleted_count},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path='quick-create')
    def quick_create(self, request):
        from apps.accounts.models import StoreMembership, Store
        from .serializers import ProductQuickCreateSerializer

        serializer = ProductQuickCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        store_id = request.data.get('store')
        memberships = StoreMembership.objects.filter(user=request.user)
        is_admin = getattr(request.user, 'role', None) == 'admin'

        if store_id is None:
            membership = memberships.select_related('store').first()
            if not membership:
                raise ValidationError({'store': 'No tienes una tienda asociada para crear productos.'})
            store = membership.store
        else:
            is_member = memberships.filter(store_id=store_id).exists()
            if not is_admin and not is_member:
                raise PermissionDenied('No tienes acceso a esta tienda.')
            try:
                store = Store.objects.get(id=store_id)
            except Store.DoesNotExist:
                raise ValidationError({'store': 'Tienda no encontrada.'})

        product = serializer.save(
            store=store,
            status=Product.Status.DRAFT,
            base_cost=0,
            current_stock=0
        )
        response_serializer = self.get_serializer(product)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        threshold = int(request.query_params.get('threshold', 10))
        products = self.get_queryset().filter(current_stock__lt=threshold)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        products = self.get_queryset().filter(current_stock=0)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='movements')
    def movements(self, request, pk=None):
        from apps.inventory.models import InventoryMovement
        from apps.inventory.serializers import InventoryMovementSerializer

        product = self.get_object()
        queryset = InventoryMovement.objects.filter(
            product=product
        ).select_related('user').order_by('-created_at')[:20]
        serializer = InventoryMovementSerializer(queryset, many=True)
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
    permission_classes = [IsAuthenticated]
    serializer_class = ProductPackagingSerializer
    queryset = ProductPackaging.objects.all()

    def get_queryset(self):
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
    permission_classes = [IsAuthenticated]
    serializer_class = ProductCodeSerializer
    queryset = ProductCode.objects.all()

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        if product_id:
            return ProductCode.objects.filter(product_id=product_id)
        return ProductCode.objects.none()


@extend_schema_view(
    list=extend_schema(tags=["Variaciones de Producto"]),
    create=extend_schema(tags=["Variaciones de Producto"]),
    retrieve=extend_schema(tags=["Variaciones de Producto"]),
    update=extend_schema(tags=["Variaciones de Producto"]),
    partial_update=extend_schema(tags=["Variaciones de Producto"]),
    destroy=extend_schema(tags=["Variaciones de Producto"]),
)
class ProductVariationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductVariationSerializer
    queryset = ProductVariation.objects.all()

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        if product_id:
            return ProductVariation.objects.filter(product_id=product_id)
        return ProductVariation.objects.none()
