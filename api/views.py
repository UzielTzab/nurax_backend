from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, CharFilter, NumberFilter, ChoiceFilter
from .models import (
    Product, Category, Supplier, Sale, Client, User, StoreProfile,
    InventoryTransaction, Expense, CashShift, SalePayment, ActiveSessionCart
)
from .serializers import *
from .pagination import ProductPagination, SalesPagination

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

import pusher
from django.conf import settings

def get_pusher_client():
    if not getattr(settings, 'PUSHER_APP_ID', None):
        print("DEBUG: PUSHER_APP_ID no encontrado en settings.")
        return None
    try:
        p = pusher.Pusher(
            app_id=settings.PUSHER_APP_ID,
            key=settings.PUSHER_KEY,
            secret=settings.PUSHER_SECRET,
            cluster=settings.PUSHER_CLUSTER,
            ssl=True
        )
        # print("DEBUG: Pusher client inicializado correctamente.")
        return p
    except Exception as e:
        print(f"Error initializing Pusher: {e}")
        return None


# FilterSet personalizado para productos con filtrado avanzado
class ProductFilterSet(FilterSet):
    """
    FilterSet personalizado para productos que permite filtrar por:
    - category: Categoría del producto (por ID)
    - sku: Código SKU
    - stock_status: Estado del stock (in_stock, low_stock, out_of_stock)
    - min_price: Precio mínimo
    - max_price: Precio máximo
    """
    stock_status = ChoiceFilter(
        method='filter_stock_status',
        choices=[
            ('in_stock', 'En Stock'),
            ('low_stock', 'Stock Bajo'),
            ('out_of_stock', 'Agotado'),
        ]
    )
    min_price = NumberFilter(field_name='price', lookup_expr='gte')
    max_price = NumberFilter(field_name='price', lookup_expr='lte')
    
    class Meta:
        model = Product
        fields = ['category', 'sku', 'stock_status', 'min_price', 'max_price']
    
    def filter_stock_status(self, queryset, name, value):
        if value == 'in_stock':
            return queryset.filter(stock__gt=10)
        elif value == 'low_stock':
            return queryset.filter(stock__lte=10, stock__gt=0)
        elif value == 'out_of_stock':
            return queryset.filter(stock=0)
        return queryset


class ProductViewSet(viewsets.ModelViewSet):
    queryset         = Product.objects.select_related('category', 'supplier').all()
    serializer_class = ProductSerializer
    filter_backends  = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class  = ProductFilterSet
    search_fields    = ['name', 'sku']
    ordering_fields  = ['price', 'stock', 'name', 'created_at']
    ordering          = ['-created_at']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role != 'admin':
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        client = get_pusher_client()
        if client:
            client.trigger(f"pos-user-{self.request.user.id}", "INVENTORY_UPDATED", {'message': 'update'})
            
    def perform_update(self, serializer):
        serializer.save()
        client = get_pusher_client()
        if client:
            client.trigger(f"pos-user-{self.request.user.id}", "INVENTORY_UPDATED", {'message': 'update'})
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        qs = self.get_queryset().filter(stock__lte=10, stock__gt=0)
        return Response(self.get_serializer(qs, many=True).data)
        
    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        qs = self.get_queryset().filter(stock=0)
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=False, methods=['post'])
    def scan(self, request):
        """
        Endpoint que recibe un código de barras (sku) desde el escáner móvil.
        Emite un evento a Pusher y retorna el producto.
        """
        sku = request.data.get('sku')
        if not sku:
            return Response({'detail': 'Se requiere el sku del producto para escanear.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Buscamos el producto por SKU. (Dependiendo de tu BD si usas un campo 'barcode' distinto, cámbialo aquí)
            product = self.get_queryset().filter(sku=sku).first()
            if not product:
                return Response({'detail': f'Producto con SKU {sku} no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(product)
            product_data = serializer.data

            # Magia del Tiempo Real: Enviar evento al canal único del usuario
            client = get_pusher_client()
            if client:
                # Usamos un canal público ofuscado (usando user ID y quizá algún hash).
                # Para un MVP, el canal del usuario suele bastar
                channel_name = f"pos-user-{request.user.id}"
                event_name = "PRODUCT_SCANNED"
                
                # Emitimos
                client.trigger(channel_name, event_name, {
                    'product': product_data
                })

            return Response({
                'detail': 'Producto escaneado y enviado al POS en tiempo real',
                'product': product_data
            })
            
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        
        # Emitir evento a Pusher de eliminación
        client = get_pusher_client()
        if client:
            client.trigger(f"pos-user-{self.request.user.id}", "INVENTORY_UPDATED", {'message': 'update'})

    @action(detail=False, methods=['post'], url_path='sync-cart')
    def sync_cart(self, request):
        """
        Recibe el estado completo del carrito desde el frontend y lo difunde a través de Pusher
        al resto de sesiones del usuario. También persiste el carrito en la base de datos.
        """
        cart_data = request.data.get('cart', [])
        device_id = request.data.get('device_id', 'unknown')
        
        # Persistencia en BD
        cart_session, created = ActiveSessionCart.objects.get_or_create(user=request.user)
        cart_session.cart_data = cart_data
        cart_session.save()
        
        # Disparar evento a Pusher
        client = get_pusher_client()
        if client:
            channel_name = f"pos-user-{request.user.id}"
            client.trigger(channel_name, "CART_UPDATED", {
                'cart': cart_data,
                'device_id': device_id
            })
            
        return Response({"detail": "Carrito sincronizado vía Pusher"})
        
    @action(detail=False, methods=['get'], url_path='my-cart')
    def my_cart(self, request):
        """
        Devuelve el estado guardado del carrito para la sesión del usuario.
        """
        cart_session, created = ActiveSessionCart.objects.get_or_create(user=request.user)
        return Response({'cart': cart_session.cart_data})

    @action(detail=False, methods=['post'], url_path='register-restock')
    def register_restock(self, request):
        """
        POST /api/products/register-restock/
        {
            "product_id": 1,
            "quantity": 4,
            "unit_cost": 50,
            "supplier_id": 1,
            "expense_category": "Inventario",
            "notes": "Compra a proveedor mayorista"
        }
        """
        from .serializers import RestockSerializer
        from .models import InventoryMovement
        from django.db import transaction
        
        serializer = RestockSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # 1. Obtener el producto
                product_id = serializer.validated_data['product_id']
                product = Product.objects.get(id=product_id, user=request.user)
                
                quantity = serializer.validated_data['quantity']
                unit_cost = serializer.validated_data['unit_cost']
                total_cost = quantity * unit_cost
                
                # 2. Obtener la caja abierta del usuario
                from .models import CashShift
                try:
                    current_shift = CashShift.objects.get(user=request.user, closed_at__isnull=True)
                except CashShift.DoesNotExist:
                    return Response({
                        'error': 'No hay una caja abierta actualmente. Abre una caja primero.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # 3. Crear el GASTO automáticamente
                expense = Expense.objects.create(
                    user=request.user,
                    category='inventario',
                    description=f"Restock: {product.name} ({quantity} unidades @ ${unit_cost})",
                    amount=total_cost,
                    cash_shift=current_shift,
                    supplier_id=serializer.validated_data.get('supplier_id')
                )
                
                # 4. Crear movimiento de inventario
                movement = InventoryMovement.objects.create(
                    product=product,
                    movement_type='restock',
                    quantity=quantity,
                    unit_cost=unit_cost,
                    total_cost=total_cost,
                    expense=expense,
                    cash_shift=current_shift,
                    user=request.user,
                    notes=serializer.validated_data.get('notes', '')
                )
                
                # 5. Actualizar stock del producto
                product.stock += quantity
                product.save()
                
                # 6. Emitir evento a Pusher
                client = get_pusher_client()
                if client:
                    client.trigger(f"pos-user-{request.user.id}", "INVENTORY_UPDATED", {
                        'message': 'restock',
                        'product_id': product.id
                    })
                
                # 7. Responder con confirmación
                return Response({
                    'success': True,
                    'message': f'Restock registrado: +{quantity} {product.name}',
                    'expense_id': expense.id,
                    'expense_amount': float(total_cost),
                    'new_stock': product.stock,
                    'movement_id': movement.id
                }, status=status.HTTP_201_CREATED)
        
        except Product.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SaleViewSet(viewsets.ModelViewSet):
    queryset         = Sale.objects.prefetch_related('items').all()
    serializer_class = SaleSerializer
    pagination_class = SalesPagination
    filter_backends  = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields    = ['transaction_id']
    ordering_fields  = ['created_at', 'total']
    ordering         = ['-created_at']  # Por defecto, las más recientes primero
    
    @action(detail=False, methods=['get'])
    def accounts_receivable(self, request):
        from django.db.models import Q
        qs = super().get_queryset()
        if self.request.user.role != 'admin':
            qs = qs.filter(user=self.request.user)
        
        # Filtro de estados: incluir LAYAWAY y CREDIT siempre
        # Si se pasa include_completed=true, también incluir COMPLETED
        statuses = [Sale.Status.LAYAWAY, Sale.Status.CREDIT]
        include_completed = request.query_params.get('include_completed', 'false').lower() == 'true'
        if include_completed:
            statuses.append(Sale.Status.COMPLETED)
        
        qs = qs.filter(status__in=statuses)
        
        search = request.query_params.get('search', None)
        if search:
            qs = qs.filter(
                Q(customer_name__icontains=search) | 
                Q(transaction_id__icontains=search) | 
                Q(customer_phone__icontains=search)
            )
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

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
        response = super().create(request, *args, **kwargs)
        
        # Magia Pusher: Sincronización en tiempo real de inventario y ventas
        if response.status_code == status.HTTP_201_CREATED:
            from django.utils import timezone
            
            client = get_pusher_client()
            if client:
                # Obtener la venta que acaba de crearse
                sale_id = response.data.get('id')
                sale = Sale.objects.prefetch_related('items').get(id=sale_id)
                user_id = request.user.id
                channel = f"pos-user-{user_id}"
                timestamp = timezone.now().isoformat()
                device_id = request.data.get('device_id', 'unknown')  # Extraer device_id del frontend
                
                # 1. Enviar evento INVENTORY_UPDATED por cada producto vendido
                for item in sale.items.all():
                    if item.product:
                        client.trigger(channel, "INVENTORY_UPDATED", {
                            'message': 'update',
                            'sale_id': sale.id,
                            'product_id': item.product.id,
                            'new_stock': item.product.stock,
                            'timestamp': timestamp,
                            'device_id': device_id  # Incluir device_id para identificar origen
                        })
                
                # 2. Enviar evento SALES_COMPLETED para confirmar la venta
                client.trigger(channel, "SALES_COMPLETED", {
                    'transaction_id': sale.transaction_id,
                    'total': float(sale.total),
                    'items_count': sale.items.count(),
                    'timestamp': timestamp,
                    'device_id': device_id  # Incluir device_id para identificar origen
                })
                
                print(f"DEBUG: Eventos Pusher enviados para venta {sale.transaction_id} al canal {channel}")
            else:
                print("DEBUG: Pusher client no inicializado en create sale.")
                
        return response

    def perform_create(self, serializer):
        # Asignar automáticamente el usuario logueado en base al token de la petición
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        from django.utils import timezone
        
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
        
        # Magia Pusher: Notificar sincronización en tiempo real de cancelación
        client = get_pusher_client()
        if client:
            channel = f"pos-user-{request.user.id}"
            timestamp = timezone.now().isoformat()
            device_id = 'server-action'  # Indicar que es una acción desde el servidor
            
            # Enviar evento INVENTORY_UPDATED por cada producto restaurado
            for item in sale.items.all():
                if item.product:
                    client.trigger(channel, "INVENTORY_UPDATED", {
                        'message': 'update',
                        'sale_id': sale.id,
                        'product_id': item.product.id,
                        'new_stock': item.product.stock,
                        'timestamp': timestamp,
                        'device_id': device_id
                    })
            
            # Enviar evento de cancelación de venta
            client.trigger(channel, "SALES_CANCELLED", {
                'transaction_id': sale.transaction_id,
                'timestamp': timestamp,
                'device_id': device_id
            })
            
            print(f"DEBUG: Eventos Pusher enviados por cancelación de venta {sale.transaction_id}")
        else:
            print("DEBUG: Pusher client no inicializado en cancel sale.")
        
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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role != 'admin':
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        if self.action in ('me', 'upload_avatar', 'change_password', 'update_profile'):
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
        # Asegurar que el usuario tenga StoreProfile para que el frontend
        # pueda decidir si mostrar el wizard de onboarding.
        from .models import StoreProfile
        StoreProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], permission_classes=[permissions.IsAuthenticated],
            url_path='me/profile')
    def update_profile(self, request):
        """
        PATCH /api/users/me/profile/
        Actualiza nombre y email del usuario autenticado.
        Requiere:
        - name: nombre del usuario (opcional)
        - email: email del usuario (opcional)
        """
        user = request.user
        name = request.data.get('name')
        email = request.data.get('email')
        
        if name is not None:
            user.name = name
        if email is not None:
            user.email = email
        
        user.save(update_fields=['name', 'email'])
        
        serializer = self.get_serializer(user)
        return Response({
            'detail': 'Perfil actualizado exitosamente.',
            'success': True,
            'user': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], permission_classes=[permissions.IsAuthenticated],
            url_path='me/change-password')
    def change_password(self, request):
        """
        PATCH /api/users/me/change-password/
        Permite cambiar la contraseña validando la contraseña actual.
        Requiere:
        - current_password: contraseña actual del usuario
        - new_password: nueva contraseña
        - confirm_password: confirmación de la nueva contraseña
        """
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar que la contraseña actual sea correcta
        current_password = serializer.validated_data.get('current_password')
        if not user.check_password(current_password):
            return Response(
                {'detail': 'La contraseña actual es incorrecta.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cambiar la contraseña
        new_password = serializer.validated_data.get('new_password')
        user.set_password(new_password)
        user.save(update_fields=['password'])
        
        return Response({
            'detail': 'Contraseña cambiada exitosamente.',
            'success': True
        }, status=status.HTTP_200_OK)

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
    Configuración del negocio por usuario.
    GET  /api/store/  → lee la configuración del usuario conectado
    PATCH /api/store/ → guarda cambios (multipart si hay logo, json si no)
    POST /api/store/onboarding-complete/ → marca onboarding como completado
    """
    permission_classes = [permissions.IsAuthenticated]


    def list(self, request):
        profile, created = StoreProfile.objects.get_or_create(user=request.user)
        serializer = StoreProfileSerializer(profile)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        profile, created = StoreProfile.objects.get_or_create(user=request.user)
        serializer = StoreProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='onboarding-complete')
    def onboarding_complete(self, request):
        """
        POST /api/store/onboarding-complete/
        {
            "store_name": "Mi Tienda",
            "ticket_name": "Recibo",
            "address": "Av. Reforma 123...",      (opcional)
            "phone": "+52 55 9876 5432",           (opcional)
            "ticket_message": "¡Gracias por su compra!"  (opcional)
        }
        """
        from .serializers import OnboardingCompleteSerializer
        
        serializer = OnboardingCompleteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            profile, created = StoreProfile.objects.get_or_create(user=request.user)
            profile.store_name = serializer.validated_data['store_name']
            profile.ticket_name = serializer.validated_data['ticket_name']
            profile.address = serializer.validated_data.get('address', '')
            profile.phone = serializer.validated_data.get('phone', '')
            profile.ticket_message = serializer.validated_data.get('ticket_message', '')
            profile.is_first_setup_completed = True
            profile.save()
            
            # Emitir evento Pusher
            try:
                client = get_pusher_client()
                if client:
                    client.trigger(f'pos-user-{request.user.id}', 'ONBOARDING_COMPLETED', {
                        'store_name': profile.store_name,
                        'timestamp': str(profile.updated_at)
                    })
            except:
                pass  # Pusher es opcional
            
            updated_serializer = StoreProfileSerializer(profile)
            return Response({
                'success': True,
                'message': 'Onboarding completado exitosamente',
                'data': updated_serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by('-date')
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role != 'admin':
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'], url_path='bulk-import')
    def bulk_import(self, request):
        """
        POST /api/products/bulk-import/
        {
            "products": [
                {"name": "Producto 1", "sku": "SKU001", "stock": 10, "price": 99.99, "category_name": "Electrónica", "supplier_name": "Proveedor 1"},
                ...
            ]
        }
        """
        from .serializers import BulkImportSerializer
        from django.db import transaction
        
        serializer = BulkImportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            products_data = serializer.validated_data['products']
            created_products = []
            errors = []
            
            with transaction.atomic():
                for idx, product_data in enumerate(products_data):
                    try:
                        # 1. Obtener o crear categoría
                        category = None
                        if product_data.get('category_name'):
                            category, _ = Category.objects.get_or_create(
                                name=product_data['category_name']
                            )
                        
                        # 2. Obtener o crear proveedor
                        supplier = None
                        if product_data.get('supplier_name'):
                            supplier, _ = Supplier.objects.get_or_create(
                                user=request.user,
                                name=product_data['supplier_name']
                            )
                        
                        # 3. Crear producto
                        product = Product.objects.create(
                            user=request.user,
                            name=product_data['name'],
                            sku=product_data['sku'],
                            category=category,
                            supplier=supplier,
                            stock=product_data.get('stock', 0),
                            price=product_data.get('price', 0)
                        )
                        created_products.append(product.id)
                    except Exception as e:
                        errors.append({
                            'row': idx + 1,
                            'sku': product_data.get('sku', ''),
                            'error': str(e)
                        })
            
            return Response({
                'success': True,
                'message': f'{len(created_products)} productos importados exitosamente',
                'created_count': len(created_products),
                'errors': errors,
                'created_ids': created_products
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


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

        from django.utils import timezone
        from django.db.models import Sum
        
        # 1. Calcular total de ventas (COMPLETED + PAID) - filtrar por fecha del turno
        sales_total = Sale.objects.filter(
            user=shift.user,
            created_at__gte=shift.opened_at,
            status__in=['completed', 'paid']
        ).aggregate(total=Sum('total'))['total'] or 0
        
        # 2. Calcular total de gastos
        expenses_total = Expense.objects.filter(
            cash_shift=shift
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # 3. Dinero esperado = Dinero inicial + Ventas - Gastos
        expected_cash = float(shift.starting_cash) + float(sales_total) - float(expenses_total)
        
        # 4. Dinero físico en caja
        actual_cash = request.data.get('actual_cash', expected_cash)
        
        # 5. Calcular diferencia
        try:
            difference = float(actual_cash) - float(expected_cash)
        except (ValueError, TypeError):
            difference = 0

        shift.closed_at = timezone.now()
        shift.expected_cash = expected_cash
        shift.actual_cash = actual_cash
        shift.difference = difference
        shift.save()
        
        return Response({
            'id': shift.id,
            'user': shift.user.id,
            'user_name': shift.user.name,
            'opened_at': shift.opened_at,
            'closed_at': shift.closed_at,
            'starting_cash': float(shift.starting_cash),
            'sales_total': float(sales_total),
            'expenses_total': float(expenses_total),
            'expected_cash': float(expected_cash),
            'actual_cash': float(actual_cash),
            'difference': float(difference),
            'difference_type': 'surplus' if difference > 0 else 'shortage' if difference < 0 else 'balanced'
        })


class InventoryTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryTransaction.objects.all().order_by('-created_at')
    serializer_class = InventoryTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role != 'admin':
            qs = qs.filter(user=self.request.user)
        
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
            if request.user.role == 'admin':
                product = Product.objects.get(id=product_id)
            else:
                product = Product.objects.get(id=product_id, user=request.user)
        except Product.DoesNotExist:
            return Response({'detail': 'Producto no encontrado o no tienes permisos.'}, status=status.HTTP_404_NOT_FOUND)

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
        
        # Magia Pusher: Avisamos movimiento manual de inventario
        client = get_pusher_client()
        if client:
            client.trigger(f"pos-user-{request.user.id}", "INVENTORY_UPDATED", {
                'message': 'update'
            })
            
        return Response(InventoryTransactionSerializer(txn).data, status=status.HTTP_201_CREATED)


class SalePaymentViewSet(viewsets.ModelViewSet):
    queryset = SalePayment.objects.all().order_by('-created_at')
    serializer_class = SalePaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role != 'admin':
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        sale_id = self.request.data.get('sale')
        serializer.save(user=self.request.user, sale_id=sale_id)

    def create(self, request, *args, **kwargs):
        sale_id = request.data.get('sale')
        amount = request.data.get('amount')
        
        if not sale_id or not amount:
             return Response({'detail': 'sale y amount son requeridos.'}, status=status.HTTP_400_BAD_REQUEST)
             
        response = super().create(request, *args, **kwargs)
        
        # update sale status to completed if total amount paid >= sale.total
        try:
            sale = Sale.objects.get(id=sale_id)
            if sale.balance_due <= 0 and sale.status in [Sale.Status.LAYAWAY, Sale.Status.CREDIT]:
                sale.status = Sale.Status.COMPLETED
                sale.save(update_fields=['status'])
        except Sale.DoesNotExist:
            pass
            
        return response
