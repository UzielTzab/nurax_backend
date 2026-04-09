"""
Vistas para la app Accounts.
ARCHITECTURE_V2: Usuarios, tiendas, membresías y clientes.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import User, Store, StoreMembership, Client
from .serializers import (
    UserSerializer, StoreSerializer, StoreMembershipSerializer,
    ClientSerializer, StoreWithMembershipsSerializer, UserRegistrationSerializer,
    StoreWithOwnerSerializer, OnboardingWizardSerializer
)
from apps.products.models import Category, Supplier

User = get_user_model()


class UserViewSet(viewsets.GenericViewSet):
    """ViewSet para usuarios (lectura, actualización, registro y cambio de contraseña)."""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['GET', 'PATCH'])
    def me(self, request):
        """Obtiene o actualiza el perfil del usuario actual."""
        user = request.user
        
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['PATCH'])
    def change_password(self, request):
        """Cambia la contraseña del usuario actual."""
        user = request.user
        
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        # Validar que todos los campos estén presentes
        if not current_password or not new_password or not confirm_password:
            return Response(
                {'error': 'current_password, new_password y confirm_password son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que la contraseña actual sea correcta
        if not user.check_password(current_password):
            return Response(
                {'error': 'La contraseña actual es incorrecta'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verificar que las contraseñas nuevas coincidan
        if new_password != confirm_password:
            return Response(
                {'error': 'Las contraseñas nuevas no coinciden'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cambiar la contraseña
        user.set_password(new_password)
        user.save()
        
        return Response({'message': 'Contraseña actualizada correctamente'})
    
    @action(detail=False, methods=['POST'], permission_classes=[AllowAny])
    def register(self, request):
        """Registra un nuevo usuario.
        
        POST /v1/accounts/users/register/
        {
            "email": "user@example.com",
            "username": "username",
            "name": "User Name",
            "password": "password123",
            "password_confirm": "password123"
        }
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {'id': user.id, 'email': user.email, 'username': user.username},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def software_clients(self, request):
        """Lista clientes del software (usuarios con rol owner en al menos una tienda)."""
        if request.user.role != User.Role.ADMIN:
            return Response({'error': 'Solo administradores pueden listar clientes del software'}, status=status.HTTP_403_FORBIDDEN)

        memberships = (
            StoreMembership.objects
            .filter(role=StoreMembership.Role.OWNER)
            .select_related('user', 'store')
            .order_by('-created_at')
        )

        seen_users = set()
        results = []
        for membership in memberships:
            if membership.user_id in seen_users:
                continue
            seen_users.add(membership.user_id)
            results.append({
                'id': str(membership.user.id),
                'name': membership.user.name or membership.user.username,
                'email': membership.user.email,
                'role': membership.role,
                'is_active': membership.user.is_active,
                'created_at': membership.user.created_at,
                'store_id': str(membership.store.id),
                'store_name': membership.store.name,
                'store_plan': membership.store.plan,
            })

        return Response({'count': len(results), 'results': results}, status=status.HTTP_200_OK)

    def toggle_software_client(self, request, user_id=None):
        """Activa/desactiva la cuenta de un cliente del software."""
        if request.user.role != User.Role.ADMIN:
            return Response({'error': 'Solo administradores pueden cambiar el estado'}, status=status.HTTP_403_FORBIDDEN)

        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        has_owner_membership = StoreMembership.objects.filter(
            user=user,
            role=StoreMembership.Role.OWNER
        ).exists()
        if not has_owner_membership:
            return Response({'error': 'El usuario no es un cliente del software (owner)'}, status=status.HTTP_400_BAD_REQUEST)

        requested_state = request.data.get('is_active')
        if requested_state is None:
            user.is_active = not user.is_active
        else:
            user.is_active = bool(requested_state)
        user.save(update_fields=['is_active'])

        return Response({'id': str(user.id), 'is_active': user.is_active}, status=status.HTTP_200_OK)

    @transaction.atomic
    def delete_software_client(self, request, user_id=None):
        """Elimina una cuenta de cliente del software (hard delete)."""
        if request.user.role != User.Role.ADMIN:
            return Response({'error': 'Solo administradores pueden eliminar clientes del software'}, status=status.HTTP_403_FORBIDDEN)

        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response(status=status.HTTP_204_NO_CONTENT)

        has_owner_membership = StoreMembership.objects.filter(
            user=user,
            role=StoreMembership.Role.OWNER
        ).exists()
        if not has_owner_membership:
            return Response({'error': 'El usuario no es un cliente del software (owner)'}, status=status.HTTP_400_BAD_REQUEST)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StoreViewSet(viewsets.ModelViewSet):
    """ViewSet para tiendas."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = StoreSerializer
    queryset = Store.objects.all()
    
    def get_queryset(self):
        """Filtrar tiendas donde el usuario es miembro."""
        user = self.request.user
        # Obtener todas las tiendas donde el usuario tiene membresía
        store_ids = StoreMembership.objects.filter(
            user=user
        ).values_list('store_id', flat=True)
        return Store.objects.filter(id__in=store_ids)
    
    def get_serializer_class(self):
        """Usar serializer con membresías en el detalle."""
        if self.action == 'retrieve':
            return StoreWithMembershipsSerializer
        if self.action == 'create_with_owner':
            return StoreWithOwnerSerializer
        return self.serializer_class
    
    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def create_with_owner(self, request):
        """Crear una tienda con su propietario en una transacción atómica.
        
        POST /v1/accounts/stores/create-with-owner/
        {
            "store_name": "Tienda XYZ",
            "store_plan": "pro",
            "store_tax_id": "J-12345678-9",
            "owner_email": "owner@example.com",
            "owner_name": "Juan Pérez"
        }
        
        Respuesta (201):
        {
            "store": {...},
            "user": {...},
            "credentials": {
                "email": "owner@example.com",
                "password": "nurax123",
                "username": "owner"
            }
        }
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['GET'])
    def memberships(self, request, pk=None):
        """Obtener membresías de una tienda."""
        store = self.get_object()
        memberships = StoreMembership.objects.filter(store=store)
        serializer = StoreMembershipSerializer(memberships, many=True)
        return Response(serializer.data)


class OnboardingWizardView(APIView):
    """Wizard v2 - crea tienda + categorias + proveedor en un solo request."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OnboardingWizardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = request.user

        niche_categories = {
            'ELECTRONICA': ['Cables', 'Cargadores', 'Audio', 'Accesorios', 'Smartphones', 'Computadoras'],
            'ABARROTES': ['Bebidas', 'Snacks', 'Abarrotes', 'Lacteos', 'Limpieza', 'Higiene'],
            'FARMACIA': ['Medicamentos', 'Cuidado personal', 'Suplementos', 'Higiene', 'Bebe', 'Primeros auxilios'],
            'FERRETERIA': ['Herramientas', 'Tornilleria', 'Electricidad', 'Pintura', 'Plomeria', 'Seguridad'],
        }

        with transaction.atomic():
            membership = (
                StoreMembership.objects
                .select_related('store')
                .filter(user=user)
                .order_by('-created_at')
                .first()
            )

            if membership:
                store = membership.store
            else:
                store = Store.objects.create(
                    name=data['tienda']['nombre'],
                    plan=Store.Plan.BASICO,
                    tax_id=data['tienda'].get('identificador_fiscal', '')
                )
                StoreMembership.objects.create(
                    store=store,
                    user=user,
                    role=StoreMembership.Role.OWNER
                )

            store.name = data['tienda']['nombre']
            store.tax_id = data['tienda'].get('identificador_fiscal', '')
            store.niche = data['tienda']['nicho']
            store.default_cash = data['configuracion']['fondo_inicial_defecto']
            store.is_first_setup_completed = True
            store.save(update_fields=['name', 'tax_id', 'niche', 'default_cash', 'is_first_setup_completed'])

            created_categories = 0
            for category_name in niche_categories.get(store.niche, []):
                _, created = Category.objects.get_or_create(
                    store=store,
                    name=category_name
                )
                if created:
                    created_categories += 1

            supplier = None
            supplier_data = data.get('proveedor_inicial', {})
            if supplier_data.get('incluir') and supplier_data.get('nombre'):
                supplier, _ = Supplier.objects.get_or_create(
                    store=store,
                    name=supplier_data['nombre'],
                    defaults={
                        'contact_info': supplier_data.get('telefono', '')
                    }
                )

        response_payload = {
            'success': True,
            'message': 'Wizard completado exitosamente',
            'store': StoreSerializer(store).data,
            'categories_created': created_categories,
            'supplier_id': str(supplier.id) if supplier else None
        }

        return Response(response_payload, status=status.HTTP_200_OK)


class StoreMembershipViewSet(viewsets.ModelViewSet):
    """ViewSet para membresías de tienda."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = StoreMembershipSerializer
    queryset = StoreMembership.objects.all()
    
    def get_queryset(self):
        """Filtrar membresías donde el usuario es propietario o gerente."""
        user = self.request.user
        # El usuario solo puede ver membresías de tiendas donde es propietario
        owner_stores = StoreMembership.objects.filter(
            user=user,
            role=StoreMembership.Role.OWNER
        ).values_list('store_id', flat=True)
        return StoreMembership.objects.filter(store_id__in=owner_stores)
    
    @transaction.atomic
    def perform_create(self, serializer):
        """Crear membresía (solo propietarios pueden hacerlo)."""
        # Validar que el creador sea propietario de la tienda
        store = serializer.validated_data['store']
        user = self.request.user
        
        is_owner = StoreMembership.objects.filter(
            store=store,
            user=user,
            role=StoreMembership.Role.OWNER
        ).exists()
        
        if not is_owner:
            raise PermissionError("Solo los propietarios pueden agregar miembros")
        
        serializer.save()


class ClientViewSet(viewsets.ModelViewSet):
    """ViewSet para clientes."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = ClientSerializer
    queryset = Client.objects.all()
    
    def get_queryset(self):
        """Los clientes están asociados a tiendas, no filtrados por usuario."""
        # En la arquitectura V2, los clientes no tienen referencia a usuario
        # solo a tienda (implícita). Por ahora retornamos todos.
        return Client.objects.all()

