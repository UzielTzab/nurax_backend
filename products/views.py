"""
Vistas para la app Products.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product, Category, Supplier
from .serializers import ProductSerializer, CategorySerializer, SupplierSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet para categorías."""
    
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SupplierViewSet(viewsets.ModelViewSet):
    """ViewSet para proveedores."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = SupplierSerializer
    
    def get_queryset(self):
        return Supplier.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de productos."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    filterset_fields = ['category', 'supplier']
    search_fields = ['name', 'sku']
    ordering_fields = ['name', 'created_at', 'stock']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Solo mostrar productos del usuario autenticado."""
        return Product.objects.filter(user=self.request.user).with_related()
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Productos con stock bajo (< 10 unidades)."""
        products = self.get_queryset().low_stock(threshold=10)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """Productos sin stock."""
        products = self.get_queryset().out_of_stock()
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        """Asignar usuario al crear producto."""
        serializer.save(user=self.request.user)
