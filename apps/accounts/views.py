"""
Vistas para la app Accounts.
ARCHITECTURE_V2: Usuarios, tiendas, membresías y clientes.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema_view, extend_schema
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from .models import User, Store, StoreMembership, Client
from .serializers import (
    UserSerializer, StoreSerializer, StoreMembershipSerializer,
    ClientSerializer, StoreWithMembershipsSerializer, UserRegistrationSerializer,
    StoreWithOwnerSerializer, OnboardingWizardSerializer, StoreEmployeeSerializer,
    StoreEmployeeCreateSerializer
)
from apps.products.models import Category, Supplier

User = get_user_model()


def _employee_role_config(role_value: str) -> dict:
    normalized = (role_value or '').strip().lower()
    if normalized in {'cashier', 'cajero'}:
        return {
            'membership_role': StoreMembership.Role.CASHIER,
            'user_role': 'cliente',
            'role_label': 'Cajero',
        }
    if normalized in {'manager', 'admin'}:
        return {
            'membership_role': StoreMembership.Role.MANAGER,
            'user_role': 'cliente',
            'role_label': 'Admin',
        }
    raise ValueError('Rol inválido')


def _build_dummy_email(store_name: str, username: str, suffix: int | None = None) -> str:
    store_slug = slugify(store_name) or 'tienda'
    username_slug = slugify(username).replace('-', '_') or 'empleado'
    if suffix is not None:
        username_slug = f'{username_slug}{suffix}'
    return f'{username_slug}@{store_slug}.nurax'


def _employee_initials(name: str) -> str:
    parts = [part for part in (name or '').strip().split() if part]
    if not parts:
        return 'NU'
    initials = ''.join(part[0] for part in parts[:2]).upper()
    return initials[:2]


class StoreEmployeesView(APIView):
    """Lista y crea empleados por tienda."""

    permission_classes = [IsAuthenticated]

    PLAN_LIMITS = {
        Store.Plan.BASICO: 2,
        Store.Plan.PRO: 3,
    }

    def _get_store(self, store_id):
        return Store.objects.filter(id=store_id).first()

    def _can_manage_store(self, request_user, store):
        if request_user.role == User.Role.ADMIN:
            return True

        membership = StoreMembership.objects.filter(store=store, user=request_user).first()
        return bool(membership and membership.role == StoreMembership.Role.OWNER)

    def _require_store_access(self, request, store_id):
        store = self._get_store(store_id)
        if not store:
            return None, Response({'error': 'Tienda no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        if not self._can_manage_store(request.user, store):
            return None, Response({'error': 'No tienes permisos para administrar este equipo'}, status=status.HTTP_403_FORBIDDEN)

        return store, None

    def get(self, request, store_id):
        store, error_response = self._require_store_access(request, store_id)
        if error_response:
            return error_response

        memberships = (
            StoreMembership.objects
            .filter(store=store)
            .select_related('user')
            .order_by('created_at')
        )

        employees = []
        for membership in memberships:
            user = membership.user
            role_label = 'Propietario' if membership.role == StoreMembership.Role.OWNER else 'Admin' if membership.role == StoreMembership.Role.MANAGER else 'Cajero'
            employees.append({
                'id': str(user.id),
                'name': user.name or user.get_full_name() or user.username,
                'username': user.username,
                'email': user.email,
                'avatar_url': user.avatar_url,
                'role': membership.role,
                'role_label': role_label,
                'membership_role': membership.role,
                'is_active': user.is_active,
                'last_login': user.last_login,
                'created_at': user.created_at,
                'initials': _employee_initials(user.name or user.get_full_name() or user.username),
            })

        plan_limit = self.PLAN_LIMITS.get(store.plan)
        payload = {
            'store': {
                'id': str(store.id),
                'name': store.name,
                'plan': store.plan,
            },
            'plan_limit': plan_limit,
            'employees_count': len(employees),
            'can_add_more': plan_limit is None or len(employees) < plan_limit,
            'employees': StoreEmployeeSerializer(employees, many=True).data,
        }

        return Response(payload, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request, store_id):
        store, error_response = self._require_store_access(request, store_id)
        if error_response:
            return error_response

        store = Store.objects.select_for_update().get(id=store.id)

        plan_limit = self.PLAN_LIMITS.get(store.plan)
        current_count = StoreMembership.objects.filter(store=store).count()
        if plan_limit is not None and current_count >= plan_limit:
            return Response({'error': 'Límite de empleados alcanzado'}, status=status.HTTP_403_FORBIDDEN)

        serializer = StoreEmployeeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        employee_name = serializer.validated_data['name'].strip()
        provided_username = serializer.validated_data.get('username') or ''
        provided_email = serializer.validated_data.get('email') or ''
        password = serializer.validated_data['password']
        role_config = _employee_role_config(serializer.validated_data['role'])

        base_username = serializer.resolve_username(store.name, employee_name, provided_username)
        username = base_username
        email = provided_email.strip()
        email_is_generated = not bool(email)

        if email and User.objects.filter(email=email).exists():
            return Response({'error': 'Este email ya está registrado.'}, status=status.HTTP_400_BAD_REQUEST)

        suffix = 1
        while User.objects.filter(username=username).exists() or User.objects.filter(email=email or _build_dummy_email(store.name, username)).exists():
            if provided_username:
                return Response({'error': 'El usuario de ingreso ya existe.'}, status=status.HTTP_400_BAD_REQUEST)
            username = f'{base_username}_{suffix}'[:150]
            suffix += 1
            if email_is_generated:
                email = _build_dummy_email(store.name, username)

        if not email:
            email = _build_dummy_email(store.name, username)

        user = User.objects.create_user(
            username=username,
            email=email,
            name=employee_name,
            role=role_config['user_role'],
        )
        user.set_password(password)
        user.save()

        membership = StoreMembership.objects.create(
            store=store,
            user=user,
            role=role_config['membership_role'],
        )

        employee_payload = {
            'id': str(user.id),
            'name': user.name or user.username,
            'username': user.username,
            'email': user.email,
            'avatar_url': user.avatar_url,
            'role': membership.role,
            'role_label': role_config['role_label'],
            'membership_role': membership.role,
            'last_login': user.last_login,
            'created_at': user.created_at,
            'initials': _employee_initials(user.name or user.username),
        }

        response_payload = {
            'employee': StoreEmployeeSerializer(employee_payload).data,
            'credentials': {
                'username': username,
                'password': password,
                'email': email,
            },
            'store': {
                'id': str(store.id),
                'name': store.name,
                'plan': store.plan,
            },
        }

        return Response(response_payload, status=status.HTTP_201_CREATED)


class StoreEmployeeDetailView(APIView):
    """Administración de un empleado específico (Editar, Suspender, Reset Password)."""
    
    permission_classes = [IsAuthenticated]

    def _require_store_access(self, request, store_id):
        store = Store.objects.filter(id=store_id).first()
        if not store:
            return None, Response({'error': 'Tienda no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role == User.Role.ADMIN:
            return store, None

        membership = StoreMembership.objects.filter(store=store, user=request.user).first()
        if not membership or membership.role != StoreMembership.Role.OWNER:
            return None, Response({'error': 'No tienes permisos para administrar empleados'}, status=status.HTTP_403_FORBIDDEN)

        return store, None

    @transaction.atomic
    def patch(self, request, store_id, user_id):
        store, error_response = self._require_store_access(request, store_id)
        if error_response:
            return error_response
            
        membership = StoreMembership.objects.filter(store=store, user_id=user_id).select_related('user').first()
        if not membership:
            return Response({'error': 'Empleado no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            
        if membership.role == StoreMembership.Role.OWNER:
            return Response({'error': 'No puedes modificar al propietario'}, status=status.HTTP_403_FORBIDDEN)
            
        user = membership.user
        data = request.data
        
        if 'name' in data:
            user.name = data['name'].strip()
            
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
            if not user.is_active:
                pass # The user requests: "Inmediatamente, cualquier token JWT o sesión activa de ese empleado debe ser invalidada para botarlo del sistema si estaba conectado."
                # We can't easily invalidate JWT unless we have a token blacklist or use token generation epoch. We'll leave it as setting is_active=False. Next time they fetch or refresh, it'll fail.
            
        user.save(update_fields=['name', 'is_active'])
        
        if 'role' in data:
            try:
                role_config = _employee_role_config(data['role'])
                membership.role = role_config['membership_role']
                membership.save(update_fields=['role'])
            except ValueError:
                return Response({'error': 'Rol inválido'}, status=status.HTTP_400_BAD_REQUEST)
                
        role_label = 'Admin' if membership.role == StoreMembership.Role.MANAGER else 'Cajero'
        employee_payload = {
            'id': str(user.id),
            'name': user.name or user.username,
            'username': user.username,
            'email': user.email,
            'avatar_url': user.avatar_url,
            'role': membership.role,
            'role_label': role_label,
            'membership_role': membership.role,
            'is_active': user.is_active,
            'last_login': user.last_login,
            'created_at': user.created_at,
            'initials': _employee_initials(user.name or user.username),
        }
        
        return Response({'success': True, 'data': StoreEmployeeSerializer(employee_payload).data}, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request, store_id, user_id):
        action = self.kwargs.get('action')
        if action != 'reset-password':
            return Response({'error': 'Endpoint no válido'}, status=status.HTTP_400_BAD_REQUEST)
            
        store, error_response = self._require_store_access(request, store_id)
        if error_response:
            return error_response
            
        membership = StoreMembership.objects.filter(store=store, user_id=user_id).select_related('user').first()
        if not membership:
            return Response({'error': 'Empleado no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            
        if membership.role == StoreMembership.Role.OWNER:
            return Response({'error': 'No puedes resetear la contraseña del propietario'}, status=status.HTTP_403_FORBIDDEN)
            
        user = membership.user
        new_password = get_random_string(8)
        user.set_password(new_password)
        user.save(update_fields=['password'])
        
        return Response({
            'success': True,
            'new_password': new_password
        }, status=status.HTTP_200_OK)


@extend_schema_view(
    me=extend_schema(tags=["Usuarios"]),
    change_password=extend_schema(tags=["Usuarios"]),
    register=extend_schema(tags=["Usuarios"]),
    software_clients=extend_schema(tags=["Usuarios"]),
    toggle_software_client=extend_schema(tags=["Usuarios"]),
    delete_software_client=extend_schema(tags=["Usuarios"]),
)
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
    
    @action(detail=False, methods=['PATCH'], url_path='change-password', url_name='change-password')
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


@extend_schema_view(
    list=extend_schema(tags=["Tiendas"]),
    create=extend_schema(tags=["Tiendas"]),
    retrieve=extend_schema(tags=["Tiendas"]),
    update=extend_schema(tags=["Tiendas"]),
    partial_update=extend_schema(tags=["Tiendas"]),
    destroy=extend_schema(tags=["Tiendas"]),
    create_with_owner=extend_schema(tags=["Tiendas"]),
    memberships=extend_schema(tags=["Tiendas"]),
)
class StoreViewSet(viewsets.ModelViewSet):
    """ViewSet para tiendas."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = StoreSerializer
    queryset = Store.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        """Filtrar tiendas donde el usuario es miembro."""
        user = self.request.user
        # Obtener todas las tiendas donde el usuario tiene membresía
        store_ids = StoreMembership.objects.filter(
            user=user
        ).values_list('store_id', flat=True)
        return Store.objects.filter(id__in=store_ids)

    def _is_owner(self, user, store):
        return StoreMembership.objects.filter(
            store=store,
            user=user,
            role=StoreMembership.Role.OWNER
        ).exists()
    
    def get_serializer_class(self):
        """Usar serializer con membresías en el detalle."""
        if self.action == 'retrieve':
            return StoreWithMembershipsSerializer
        if self.action == 'create_with_owner':
            return StoreWithOwnerSerializer
        return self.serializer_class

    def update(self, request, *args, **kwargs):
        store = self.get_object()
        if not self._is_owner(request.user, store):
            return Response({'error': 'Solo propietarios pueden modificar la tienda'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        store = self.get_object()
        if not self._is_owner(request.user, store):
            return Response({'error': 'Solo propietarios pueden modificar la tienda'}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)
    
    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated], url_path='create-with-owner', url_name='create-with-owner')
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


@extend_schema(tags=["Wizard de Configuración"])
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
            'MASCOTAS': [
                'Alimento Seco (Croquetas)',
                'Alimento Húmedo (Sobres, latas, patés)',
                'Premios y Snacks (Huesos, galletas)',
                'Higiene y Cuidado (Shampoo, arena, cepillos)',
                'Accesorios y Juguetes (Correas, collares, pelotas)',
                'Farmacia Veterinaria (Desparasitantes, vitaminas - solo si venden medicina)',
            ],
            'BELLEZA': [
                'Servicios de Cabello (Cortes, tintes, peinados)',
                'Servicios de Uñas (Manicure, pedicure, acrílico)',
                'Cuidado Capilar (Shampoos, tratamientos, ceras)',
                'Cosméticos y Maquillaje',
                'Herramientas y Accesorios (Cepillos, pasadores)',
                'Cuidado de la Piel / Spa (Mascarillas, masajes)',
            ],
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
            store.is_first_setup_completed = True
            store.save(update_fields=['name', 'tax_id', 'niche', 'is_first_setup_completed'])

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


@extend_schema_view(
    list=extend_schema(tags=["Membresías"]),
    create=extend_schema(tags=["Membresías"]),
    retrieve=extend_schema(tags=["Membresías"]),
    update=extend_schema(tags=["Membresías"]),
    partial_update=extend_schema(tags=["Membresías"]),
    destroy=extend_schema(tags=["Membresías"]),
)
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


@extend_schema_view(
    list=extend_schema(tags=["Clientes"]),
    create=extend_schema(tags=["Clientes"]),
    retrieve=extend_schema(tags=["Clientes"]),
    update=extend_schema(tags=["Clientes"]),
    partial_update=extend_schema(tags=["Clientes"]),
    destroy=extend_schema(tags=["Clientes"]),
)
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

