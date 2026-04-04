"""
Vistas para la app Products.
ARCHITECTURE_V2: Catálogo, categorías, proveedores y códigos.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
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
    
    def get_queryset(self):
        """Filtrar productos por tienda."""
        store_id = self.request.query_params.get('store_id')
        if store_id:
            return Product.objects.filter(store_id=store_id)
        return Product.objects.none()
    
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
