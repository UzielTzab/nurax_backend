"""
Views para la app Carts.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import ActiveCart, CartItem
from .serializers import ActiveCartSerializer, CartItemSerializer, CartItemCreateSerializer


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
        
        return Response(
            {'message': 'Carrito vaciado'},
            status=status.HTTP_200_OK
        )
