from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, Category, Supplier, Sale, Client, User, StoreProfile
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

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        sale = self.get_object()
        
        # 1. Validar que la venta no esté ya cancelada
        if sale.status == Sale.Status.CANCELLED:
            return Response(
                {'detail': 'Esta venta ya se encuentra cancelada.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 2. Restaurar el stock de cada producto vendido
        for item in sale.items.all():
            if item.product:
                # Opcional: Podrías usar F() expressions de Django para evitar carrera de datos, 
                # pero para esta escala, sumarlo directo funciona excelente.
                item.product.stock += item.quantity
                item.product.save()
                
        # 3. Cambiar el estado de la venta y guardar
        sale.status = Sale.Status.CANCELLED
        sale.save()
        
        return Response({'status': 'Venta cancelada exitosamente y stock restaurado'})

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
        if self.action == 'create':
            return [permissions.AllowAny()]
        if self.action in ('me', 'upload_avatar'):
            return [permissions.IsAuthenticated()]
        return [IsAdmin()]

    def get_queryset(self):
        qs = User.objects.all().order_by('-date_joined')
        # Filtrar por rol si se pasa ?role=cliente o ?role=admin
        role = self.request.query_params.get('role')
        if role:
            qs = qs.filter(role=role)
        return qs
        
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdmin])
    def toggle_active(self, request, pk=None):
        """Activa o desactiva la cuenta de un usuario. Solo admin."""
        user = self.get_object()
        if user == request.user:
            return Response(
                {'detail': 'No puedes desactivar tu propia cuenta de administrador.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        return Response({'is_active': user.is_active})

    @action(detail=False, methods=['patch'], permission_classes=[permissions.IsAuthenticated],
            url_path='me/avatar')
    def upload_avatar(self, request):
        """
        PATCH /api/users/me/avatar/
        Recibe multipart/form-data con la clave 'avatar_file' (un archivo de imagen).
        Sube la imagen a Cloudinary y guarda la URL en el perfil del usuario logueado.
        """
        file_obj = request.FILES.get('avatar_file')
        
        if not file_obj:
            return Response(
                {'detail': 'No se recibió ningún archivo. Usa la clave "avatar_file".'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        import cloudinary.uploader
        result = cloudinary.uploader.upload(
            file_obj,
            folder='avatars',
            transformation=[{'width': 400, 'height': 400, 'crop': 'fill', 'gravity': 'face'}]
        )
        request.user.avatar_url = result.get('secure_url')
        request.user.save(update_fields=['avatar_url'])
        return Response({'avatar_url': request.user.avatar_url})


class StoreProfileViewSet(viewsets.ViewSet):
    """
    Singleton: solo hay UN perfil de negocio en todo el sistema.
    GET  /api/store/  → lee la configuración actual
    PATCH /api/store/ → guarda cambios (multipart si hay logo, json si no)
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        profile = StoreProfile.get_solo()
        serializer = StoreProfileSerializer(profile)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        profile = StoreProfile.get_solo()
        serializer = StoreProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
