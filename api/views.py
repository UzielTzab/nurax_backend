from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Product, Category, Supplier, Sale, Client, User, StoreProfile,
    InventoryTransaction, Expense, CashShift, SalePayment
)
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

    def perform_destroy(self, instance):
        # Borrar imagen de Cloudinary para no dejar basura en la nube
        if instance.image_url:
            import cloudinary.uploader
            try:
                # Extraer el public_id de la URL.
                # Ejemplo URL: https://res.cloudinary.com/xyz/image/upload/v1234/products/abc.png
                parts = instance.image_url.split('/upload/')
                if len(parts) == 2:
                    path = parts[1]
                    # Quitar la versión ("v1234/") si existe
                    if '/' in path and path.split('/')[0].startswith('v') and path.split('/')[0][1:].isdigit():
                        path = path.split('/', 1)[1]
                    # Quitar la extensión (.png, .jpg) para obtener el public_id
                    public_id = path.rsplit('.', 1)[0]
                    cloudinary.uploader.destroy(public_id)
            except Exception as e:
                print(f"Error borrando imagen de Cloudinary: {e}")
                
        # Finalmente, borrar el registro de la base de datos local
        instance.delete()

class SaleViewSet(viewsets.ModelViewSet):
    queryset         = Sale.objects.prefetch_related('items').all()
    serializer_class = SaleSerializer
    
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role != 'admin':
            qs = qs.filter(user=self.request.user)
        return qs

    def create(self, request, *args, **kwargs):
        active_shift = CashShift.objects.filter(user=request.user, closed_at__isnull=True).first()
        if not active_shift:
            return Response(
                {'detail': 'Debes abrir un turno (caja) antes de poder registrar una venta.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

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
                
                InventoryTransaction.objects.create(
                    product=item.product,
                    transaction_type=InventoryTransaction.TransactionType.IN,
                    quantity=item.quantity,
                    reason=f'Cancelación Venta {sale.transaction_id}',
                    user=request.user
                )
                
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


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by('-date')
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CashShiftViewSet(viewsets.ModelViewSet):
    queryset = CashShift.objects.all().order_by('-opened_at')
    serializer_class = CashShiftSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role != 'admin':
            qs = qs.filter(user=self.request.user)
        return qs

    @action(detail=False, methods=['post'])
    def open(self, request):
        active = CashShift.objects.filter(user=request.user, closed_at__isnull=True).first()
        if active:
            return Response({'detail': 'Ya tienes un turno abierto.'}, status=status.HTTP_400_BAD_REQUEST)
        
        starting_cash = request.data.get('starting_cash')
        if starting_cash is None:
            return Response({'detail': 'Se requiere amount inicial (starting_cash).'}, status=status.HTTP_400_BAD_REQUEST)

        shift = CashShift.objects.create(user=request.user, starting_cash=starting_cash)
        return Response(self.get_serializer(shift).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        shift = self.get_object()
        if shift.closed_at:
            return Response({'detail': 'Este turno ya está cerrado.'}, status=status.HTTP_400_BAD_REQUEST)
        if shift.user != request.user and request.user.role != 'admin':
            return Response({'detail': 'No puedes cerrar el turno de otro usuario.'}, status=status.HTTP_403_FORBIDDEN)

        # En un sistema real, aquí calcularíamos el expected_cash sumando las ventas en efectivo del día
        # Para mantenerlo simple, recibimos expected y actual desde el frontend y la diferencia.
        from django.utils import timezone
        
        shift.closed_at = timezone.now()
        shift.expected_cash = request.data.get('expected_cash', shift.starting_cash)
        shift.actual_cash = request.data.get('actual_cash', shift.expected_cash)
        # diff: actual - expected. Si es negativo, faltó dinero. Si es positivo, sobró.
        try:
            shift.difference = float(shift.actual_cash) - float(shift.expected_cash)
        except (ValueError, TypeError):
            shift.difference = 0

        shift.save()
        return Response(self.get_serializer(shift).data)


class InventoryTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryTransaction.objects.all().order_by('-created_at')
    serializer_class = InventoryTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        product_id = self.request.query_params.get('product')
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs

    @action(detail=False, methods=['post'])
    def manual_adjustment(self, request):
        product_id = request.data.get('product')
        quantity = request.data.get('quantity')
        transaction_type = request.data.get('transaction_type')
        reason = request.data.get('reason', 'Ajuste manual')

        if not all([product_id, quantity, transaction_type]):
            return Response({'detail': 'product, quantity y transaction_type son requeridos.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Producto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            quantity = int(quantity)
        except ValueError:
            return Response({'detail': 'Cantidad debe ser un número entero.'}, status=status.HTTP_400_BAD_REQUEST)

        # Aplicar el cambio al stock
        if transaction_type in ['in', 'adjustment']: # Asumimos 'adjustment' puede ser entrada. En app real, adjustment sería a stock absoluto, pero aquí podemos sumar/restar con signo. O 'in' / 'out'.
            # Para simplificar, si el tipo es OUT o WASTE restamos
            if transaction_type in ['out', 'waste']:
                return Response({'detail': 'Usa números negativos o tipos in/out correspondientes. Configurado para lógica específica.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Lógica mejorada:
        if transaction_type in ['out', 'waste']:
            new_stock = product.stock - quantity
        else: # in, adjustment
            # Si el usuario mandó negativo en adjustment, se respeta la lógica
            if transaction_type == 'adjustment' and quantity < 0:
                new_stock = product.stock + quantity
                quantity = abs(quantity)
                transaction_type = 'out' # convertimos a out para que se entienda el kárdex
            else:
                new_stock = product.stock + quantity

        if new_stock < 0:
            return Response({'detail': 'El stock final no puede ser negativo.'}, status=status.HTTP_400_BAD_REQUEST)

        product.stock = new_stock
        product.save()

        txn = InventoryTransaction.objects.create(
            product=product,
            transaction_type=transaction_type,
            quantity=quantity,
            reason=reason,
            user=request.user
        )
        return Response(InventoryTransactionSerializer(txn).data, status=status.HTTP_201_CREATED)


class SalePaymentViewSet(viewsets.ModelViewSet):
    queryset = SalePayment.objects.all().order_by('-created_at')
    serializer_class = SalePaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        sale_id = request.data.get('sale')
        amount = request.data.get('amount')
        
        if not sale_id or not amount:
             return Response({'detail': 'sale y amount son requeridos.'}, status=status.HTTP_400_BAD_REQUEST)
             
        # Optional: update sale status to completed if total amount paid >= sale.total
        # For now just record the payment
        return super().create(request, *args, **kwargs)
