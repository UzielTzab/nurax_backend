"""
Views para la app Carts.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema_view, extend_schema
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated as DRFIsAuthenticated
import pusher
from .models import ActiveCart, CartItem
from .serializers import ActiveCartSerializer, CartItemSerializer, CartItemCreateSerializer


# Inicializar cliente Pusher usando settings
_pusher_client = None
def get_pusher_client():
    global _pusher_client
    if _pusher_client is None:
        _pusher_client = pusher.Pusher(
            app_id=getattr(settings, 'PUSHER_APP_ID', None),
            key=getattr(settings, 'PUSHER_KEY', None),
            secret=getattr(settings, 'PUSHER_SECRET', None),
            cluster=getattr(settings, 'PUSHER_CLUSTER', None),
            ssl=True
        )
    return _pusher_client


def _broadcast_cart_updated(session_id: str, active_cart_id: str, device_id: str | None = None):
    """Emitir evento CART_UPDATED al canal privado del carrito."""
    try:
        client = get_pusher_client()
        channel = f"private-cart-{session_id}"
        payload = {'action': 'CART_UPDATED', 'active_cart_id': str(active_cart_id)}
        if device_id:
            payload['device_id'] = device_id
        client.trigger(channel, 'CART_UPDATED', payload)
    except Exception:
        # No fallamos la solicitud por un error en Pusher; sólo registramos silenciosamente.
        pass


@api_view(['POST'])
@permission_classes([DRFIsAuthenticated])
def pusher_auth(request):
    """Endpoint de autenticación para canales privados de Pusher.

    Body esperado: { "socket_id": "..", "channel_name": "private-cart-..." }
    """
    socket_id = request.data.get('socket_id') or request.query_params.get('socket_id')
    channel_name = request.data.get('channel_name') or request.query_params.get('channel_name')
    if not socket_id or not channel_name:
        return Response({'error': 'socket_id y channel_name requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        client = get_pusher_client()
        auth = client.authenticate(channel_name, socket_id)
        return Response(auth)
    except Exception as e:
        return Response({'error': 'Error al autenticar con Pusher'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema_view(
    list=extend_schema(tags=["Carritos"]),
    create=extend_schema(tags=["Carritos"]),
    retrieve=extend_schema(tags=["Carritos"]),
    update=extend_schema(tags=["Carritos"]),
    partial_update=extend_schema(tags=["Carritos"]),
    destroy=extend_schema(tags=["Carritos"]),
    add_item=extend_schema(tags=["Carritos"]),
    remove_item=extend_schema(tags=["Carritos"]),
    clear=extend_schema(tags=["Carritos"]),
    park_cart=extend_schema(tags=["Carritos"]),
    list_parked_carts=extend_schema(tags=["Carritos"]),
    restore_parked_cart=extend_schema(tags=["Carritos"]),
)
class ActiveCartViewSet(viewsets.ModelViewSet):
    """ViewSet para carritos activos."""
    
    serializer_class = ActiveCartSerializer
    permission_classes = [IsAuthenticated]
    queryset = ActiveCart.objects.all()
    
    def get_queryset(self):
        """Filtrar carritos por tienda del usuario."""
        user = self.request.user
        # Asumiendo que el usuario tiene acceso a ciertas tiendas
        return ActiveCart.objects.filter(user=user)
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Agregar item al carrito."""
        cart = self.get_object()
        serializer = CartItemCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Verificar si el producto ya existe en el carrito
            product_id = serializer.validated_data['product'].id
            try:
                cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
                cart_item.quantity += serializer.validated_data['quantity']
                cart_item.save()
            except CartItem.DoesNotExist:
                serializer.save(cart=cart)
            
            # Actualizar total_temp del carrito
            cart.total_temp = sum(item.subtotal for item in cart.items.all())
            cart.save()
            
            # Broadcast via Pusher
            device_id = request.data.get('device_id') if hasattr(request, 'data') else None
            try:
                _broadcast_cart_updated(cart.session_id, cart.id, device_id)
            except Exception:
                pass

            return Response(
                ActiveCartSerializer(cart).data,
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def remove_item(self, request, pk=None):
        """Remover item del carrito."""
        cart = self.get_object()
        item_id = request.data.get('item_id')
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
            
            # Actualizar total_temp
            cart.total_temp = sum(item.subtotal for item in cart.items.all())
            cart.save()
            
            # Broadcast via Pusher
            device_id = request.data.get('device_id') if hasattr(request, 'data') else None
            try:
                _broadcast_cart_updated(cart.session_id, cart.id, device_id)
            except Exception:
                pass

            return Response(
                ActiveCartSerializer(cart).data,
                status=status.HTTP_200_OK
            )
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Item no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        """Limpiar el carrito."""
        cart = self.get_object()
        cart.items.all().delete()
        cart.total_temp = 0
        cart.save()
        
        # Broadcast via Pusher
        device_id = request.data.get('device_id') if hasattr(request, 'data') else None
        try:
            _broadcast_cart_updated(cart.session_id, cart.id, device_id)
        except Exception:
            pass

        return Response(
            {'message': 'Carrito vaciado'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='my-cart')
    def my_cart(self, request):
        """Retorna (o crea) el carrito activo del usuario autenticado.

        GET /api/v1/carts/carts/my-cart/
        """
        user = request.user
        if not user or not user.is_authenticated:
            return Response({'error': 'Autenticación requerida'}, status=status.HTTP_401_UNAUTHORIZED)

        # Intentar obtener el carrito activo del usuario (no aparcado)
        cart = ActiveCart.objects.filter(user=user, is_parked=False).prefetch_related('items__product').first()
        if not cart:
            # Devolver lista vacía para que el frontend pueda asignarla directamente a `cart.value`
            return Response({'success': True, 'data': {'cart': []}}, status=status.HTTP_200_OK)

        # Normalizar salida: devolver solo la lista de items (frontend espera un array)
        items = [
            {
                'id': str(i.id),
                'product': str(i.product_id),
                'product_name': i.product.name if i.product else '',
                'quantity': i.quantity,
                'unit_price_at_time': float(i.unit_price_at_time),
                'subtotal': float(i.subtotal),
            }
            for i in cart.items.all()
        ]

        return Response({'success': True, 'data': {'cart': items, 'session_id': cart.session_id, 'active_cart_id': str(cart.id)}}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='sync-cart')
    def sync_cart(self, request):
        """Sincroniza el carrito enviado por el cliente con el `ActiveCart` del usuario.

        Payload esperado: { cart: [ { id, quantity, sale_price?, price?, store? }, ... ], device_id }
        """
        user = request.user
        if not user or not user.is_authenticated:
            return Response({'error': 'Autenticación requerida'}, status=status.HTTP_401_UNAUTHORIZED)

        payload_cart = request.data.get('cart', []) or []
        device_id = request.data.get('device_id') or request.data.get('session_id')

        if not device_id:
            return Response({'error': 'device_id (session identifier) requerido'}, status=status.HTTP_400_BAD_REQUEST)

        # Determinar tienda: buscar en payload, preferir campo store del primer item, si no, inferir desde el producto
        store_id = request.data.get('store_id') or request.data.get('store')
        if not store_id and len(payload_cart) > 0:
            first = payload_cart[0]
            store_id = first.get('store') or first.get('store_id')

        # Intentar inferir store desde el primer producto si no viene en el payload
        if not store_id and len(payload_cart) > 0:
            try:
                from apps.products.models import Product
                prod_id = payload_cart[0].get('id')
                if prod_id:
                    p = Product.objects.filter(id=prod_id).first()
                    if p:
                        store_id = p.store_id
            except Exception:
                store_id = None

        # Si aún no hay tienda, intentar obtenerla de la membresía del usuario
        if not store_id:
            from apps.accounts.models import StoreMembership
            membership = StoreMembership.objects.filter(user=user).first()
            if membership:
                store_id = membership.store_id

        if not store_id:
            return Response({'error': 'No se pudo determinar la tienda para el carrito'}, status=status.HTTP_400_BAD_REQUEST)

        from apps.accounts.models import Store
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return Response({'error': 'Tienda no encontrada'}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar un ActiveCart existente para este usuario+tienda (compartido entre dispositivos)
        cart_obj = ActiveCart.objects.filter(user=user, store=store, is_parked=False).first()
        if not cart_obj:
            cart_obj = ActiveCart.objects.create(session_id=device_id, user=user, store=store)
        else:
            # Actualizar session_id si no está definido (mantener compartido entre sesiones)
            if not cart_obj.session_id:
                cart_obj.session_id = device_id
                cart_obj.save()

        # Upsert items
        incoming_product_ids = []
        from apps.products.models import Product

        for item in payload_cart:
            prod_id = item.get('id')
            if prod_id is None:
                continue
            try:
                product = Product.objects.get(id=prod_id)
            except Product.DoesNotExist:
                continue

            quantity = int(item.get('quantity', 1)) if item.get('quantity') is not None else 1
            unit_price = item.get('sale_price') or item.get('price') or 0

            cart_item, _ = CartItem.objects.update_or_create(
                cart=cart_obj,
                product=product,
                defaults={
                    'quantity': quantity,
                    'unit_price_at_time': unit_price,
                }
            )
            incoming_product_ids.append(product.id)

        # Eliminar items que no están en el payload
        if incoming_product_ids:
            cart_obj.items.exclude(product_id__in=incoming_product_ids).delete()
        else:
            # Si el payload venía vacío, limpiar el carrito
            cart_obj.items.all().delete()

        # Actualizar total_temp
        cart_obj.total_temp = sum([item.subtotal for item in cart_obj.items.all()])
        cart_obj.save()

        # Broadcast via Pusher
        try:
            _broadcast_cart_updated(cart_obj.session_id, cart_obj.id, device_id)
        except Exception:
            pass

        return Response({'success': True, 'data': {'cart': [
            {
                'id': str(i.id),
                'product': str(i.product_id),
                'product_name': i.product.name if i.product else '',
                'quantity': i.quantity,
                'unit_price_at_time': float(i.unit_price_at_time),
                'subtotal': float(i.subtotal)
            } for i in cart_obj.items.all()
        ], 'session_id': cart_obj.session_id, 'active_cart_id': str(cart_obj.id)}}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='park')
    def park_cart(self, request, pk=None):
        """Aparcar (guardar para después) el carrito activo."""
        cart = self.get_object()
        if cart.is_parked:
            return Response({'error': 'El carrito ya está aparcado'}, status=status.HTTP_400_BAD_REQUEST)

        import uuid
        from django.utils import timezone

        cart.is_parked = True
        cart.parked_at = timezone.now()
        cart.save()

        fresh_cart = ActiveCart.objects.create(
            store=cart.store,
            user=cart.user,
            session_id=str(uuid.uuid4()),
            total_temp=0,
        )

        return Response({
            'success': True,
            'message': 'Carrito aparcado exitosamente',
            'data': {
                'id': str(cart.id),
                'session_id': cart.session_id,
                'parked_at': cart.parked_at,
                'total': float(cart.total_temp),
                'new_active_cart': {
                    'id': str(fresh_cart.id),
                    'session_id': fresh_cart.session_id,
                    'total': float(fresh_cart.total_temp),
                }
            }
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='parked')
    def list_parked_carts(self, request):
        """Listar los carritos aparcados del usuario autenticado."""
        user = request.user
        if not user or not user.is_authenticated:
            return Response({'error': 'Autenticación requerida'}, status=status.HTTP_401_UNAUTHORIZED)

        parked_carts = ActiveCart.objects.filter(user=user, is_parked=True).prefetch_related('items__product')

        data = []
        for cart in parked_carts:
            items_count = cart.items.count()
            data.append({
                'id': str(cart.id),
                'session_id': cart.session_id,
                'store': str(cart.store_id) if cart.store else None,
                'store_name': cart.store.name if cart.store else 'Tienda desconocida',
                'total': float(cart.total_temp),
                'items_count': items_count,
                'parked_at': cart.parked_at,
            })

        return Response({
            'success': True,
            'data': data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='restore')
    def restore_parked_cart(self, request, pk=None):
        """Restaurar un carrito aparcado como carrito activo."""
        cart = self.get_object()
        if not cart.is_parked:
            return Response({'error': 'El carrito no está aparcado'}, status=status.HTTP_400_BAD_REQUEST)

        # Eliminar carrito activo anterior (si existe) para evitar duplicados
        old_active = ActiveCart.objects.filter(
            user=cart.user,
            store=cart.store,
            is_parked=False
        ).exclude(id=cart.id).first()
        if old_active:
            old_active.delete()

        # Restaurar el carrito aparcado como activo
        import uuid
        cart.is_parked = False
        cart.parked_at = None
        cart.session_id = str(uuid.uuid4())  # Generar nuevo session_id para Pusher
        cart.save()

        # Preparar respuesta
        items = [
            {
                'id': str(i.id),
                'product': str(i.product_id),
                'product_name': i.product.name if i.product else '',
                'quantity': i.quantity,
                'unit_price_at_time': float(i.unit_price_at_time),
                'subtotal': float(i.subtotal),
            }
            for i in cart.items.all()
        ]

        return Response({
            'success': True,
            'message': 'Carrito restaurado exitosamente',
            'data': {
                'cart': items,
                'session_id': cart.session_id,
                'active_cart_id': str(cart.id)
            }
        }, status=status.HTTP_200_OK)
