from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, Category, Supplier, Sale, Client, User
from .serializers import *

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class ProductViewSet(viewsets.ModelViewSet):
    queryset         = Product.objects.select_related('category', 'supplier').all()
    serializer_class = ProductSerializer
    filter_backends  = [DjangoFilterBackend]
    filterset_fields = ['category', 'sku']
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        qs = self.get_queryset().filter(stock__lte=10, stock__gt=0)
        return Response(self.get_serializer(qs, many=True).data)
        
    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        qs = self.get_queryset().filter(stock=0)
        return Response(self.get_serializer(qs, many=True).data)

class SaleViewSet(viewsets.ModelViewSet):
    queryset         = Sale.objects.prefetch_related('items').all()
    serializer_class = SaleSerializer
    
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role != 'admin':
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        # Asignar automáticamente el usuario logueado en base al token de la petición
        serializer.save(user=self.request.user)

class ClientViewSet(viewsets.ModelViewSet):
    queryset         = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAdmin]
    
    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        client = self.get_object()
        client.active = not client.active
        client.save()
        return Response({'active': client.active})

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = Category.objects.all()
    serializer_class = CategorySerializer

class SupplierViewSet(viewsets.ModelViewSet):
    queryset         = Supplier.objects.all()
    serializer_class = SupplierSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        # Permitir registro público si alguien quiere crear cuenta.
        # El endpoint 'me' necesita IsAuthenticated.
        if self.action == 'create':
            return [permissions.AllowAny()]
        if self.action == 'me':
            return [permissions.IsAuthenticated()]
        return [IsAdmin()]
        
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
