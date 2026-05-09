"""
Serializadores para la app Accounts.
ARCHITECTURE_V2: Usuarios, tiendas y membresías.
"""
import cloudinary.uploader
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from .models import User, Store, StoreMembership, Client

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer para usuarios - retorna campos esperados por frontend."""
    avatar_file = serializers.ImageField(write_only=True, required=False)
    store_profile = serializers.SerializerMethodField()
    
    # Método para obtener 'name' como combinación de first_name y last_name
    def get_name(self, obj):
        """Retorna nombre completo (first_name + last_name o 'name' field)."""
        if obj.name:
            return obj.name
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name if full_name else obj.username
    
    # Método para combinar en guardar
    def to_representation(self, instance):
        """Customizza la representación para el frontend."""
        data = super().to_representation(instance)
        # Usar el campo 'name' si existe, sino combinar first_name y last_name
        if not data.get('name'):
            data['name'] = f"{instance.first_name} {instance.last_name}".strip() or instance.username
        return data
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'name',
            'role',
            'avatar_url',
            'avatar_file',
            'store_profile',
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'avatar_url': {'read_only': True},
        }

    def get_store_profile(self, obj):
        """Retorna la tienda activa basada en la membresia del usuario."""
        membership = (
            StoreMembership.objects
            .select_related('store')
            .filter(user=obj)
            .order_by('-created_at')
            .first()
        )
        if not membership:
            return None

        store = membership.store
        return {
            'id': str(store.id),
            'name': store.name,
            'membership_role': membership.role,
            'plan': store.plan,
            'tax_id': store.tax_id,
            'active': store.active,
            'niche': store.niche,
            'is_first_setup_completed': store.is_first_setup_completed,
            'default_cash': str(store.default_cash),
            'currency_symbol': store.currency_symbol,
            'address': store.address,
            'phone': store.phone,
            'country_code': store.country_code,
            'ticket_message': store.ticket_message,
            'logo_url': store.logo_url,
        }

    def update(self, instance, validated_data):
        """Sube avatar a Cloudinary cuando llega avatar_file y persiste avatar_url."""
        avatar_file = validated_data.pop('avatar_file', None)
        if avatar_file:
            try:
                upload_data = cloudinary.uploader.upload(
                    avatar_file,
                    folder='avatars',
                    transformation=[{'width': 400, 'height': 400, 'crop': 'fill', 'gravity': 'face'}]
                )
                validated_data['avatar_url'] = upload_data.get('secure_url')
            except Exception as exc:
                raise serializers.ValidationError({'avatar_file': f'Error al subir imagen: {exc}'})

        return super().update(instance, validated_data)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para crear nuevos usuarios (registro/admin creation)."""
    
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, required=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'name', 'password', 'password_confirm', 'role']
    
    def validate(self, data):
        """Validar que las contraseñas coincidan."""
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'Las contraseñas no coinciden.'})
        
        # Validar email único
        if User.objects.filter(email=data.get('email')).exists():
            raise serializers.ValidationError({'email': 'Este email ya está registrado.'})
        
        return data
    
    def create(self, validated_data):
        """Crear nuevo usuario con contraseña."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class StoreSerializer(serializers.ModelSerializer):
    """Serializer para tiendas."""

    logo_file = serializers.ImageField(write_only=True, required=False)
    
    class Meta:
        model = Store
        fields = [
            'id',
            'name',
            'plan',
            'tax_id',
            'niche',
            'currency_symbol',
            'address',
            'phone',
            'country_code',
            'ticket_message',
            'logo_url',
            'logo_file',
            'active',
            'is_first_setup_completed',
            'default_cash',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_logo_file(self, value):
        max_size = 2 * 1024 * 1024
        valid_types = {'image/png', 'image/jpeg', 'image/webp'}

        if value.size > max_size:
            raise serializers.ValidationError('El logo no debe superar 2 MB.')

        content_type = getattr(value, 'content_type', '')
        if content_type and content_type not in valid_types:
            raise serializers.ValidationError('Formato de logo invalido (PNG, JPG o WebP).')

        return value

    def update(self, instance, validated_data):
        logo_file = validated_data.pop('logo_file', None)

        if logo_file:
            try:
                upload_data = cloudinary.uploader.upload(
                    logo_file,
                    folder='store-logos'
                )
                validated_data['logo_url'] = upload_data.get('secure_url')
            except Exception as exc:
                raise serializers.ValidationError({'logo_file': f'Error al subir imagen: {exc}'})

        return super().update(instance, validated_data)


class StoreMembershipSerializer(serializers.ModelSerializer):
    """Serializer para membresías de tienda."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    
    class Meta:
        model = StoreMembership
        fields = ['id', 'store', 'store_name', 'user', 'user_email', 'user_name', 'role', 'created_at']
        read_only_fields = ['id', 'created_at']


class StoreEmployeeSerializer(serializers.Serializer):
    """Serializer para listar empleados de una tienda."""

    id = serializers.CharField()
    name = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    avatar_url = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    role = serializers.CharField()
    role_label = serializers.CharField()
    membership_role = serializers.CharField()
    is_active = serializers.BooleanField(required=False, default=True)
    last_login = serializers.DateTimeField(allow_null=True, required=False)
    created_at = serializers.DateTimeField()
    initials = serializers.CharField()


class StoreEmployeeCreateSerializer(serializers.Serializer):
    """Serializer para crear empleados de tienda."""

    name = serializers.CharField(max_length=200)
    username = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(min_length=8)
    role = serializers.CharField()

    def validate_role(self, value):
        normalized = (value or '').strip().lower()
        allowed = {'cashier', 'cajero', 'manager', 'admin'}
        if normalized not in allowed:
            raise serializers.ValidationError('Rol inválido.')
        return normalized

    def validate(self, data):
        name = (data.get('name') or '').strip()
        if not name:
            raise serializers.ValidationError({'name': 'El nombre es obligatorio.'})

        if not data.get('password'):
            raise serializers.ValidationError({'password': 'La contraseña es obligatoria.'})

        return data

    def resolve_username(self, store_name: str, employee_name: str, provided_username: str | None = None) -> str:
        if provided_username:
            return slugify(provided_username).replace('-', '_')[:150]

        store_slug = slugify(store_name).replace('-', '_') or 'tienda'
        employee_slug = slugify(employee_name).replace('-', '_') or 'empleado'
        return f'{store_slug}_{employee_slug}'[:150]



class ClientSerializer(serializers.ModelSerializer):
    """Serializer para clientes."""
    
    class Meta:
        model = Client
        fields = ['id', 'name', 'credit_limit', 'active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class StoreWithOwnerSerializer(serializers.Serializer):
    """Serializer para crear Store + User + StoreMembership en una transacción atómica.
    
    Este serializer maneja el flujo completo de crear una tienda con su propietario.
    """
    
    # Store fields (input)
    store_name = serializers.CharField(max_length=200, required=True, write_only=True)
    store_plan = serializers.ChoiceField(choices=['basico', 'pro'], default='basico', write_only=True)
    store_tax_id = serializers.CharField(max_length=50, required=False, allow_blank=True, write_only=True)
    
    # User fields (input)
    owner_email = serializers.EmailField(required=True, write_only=True)
    owner_name = serializers.CharField(max_length=200, required=True, write_only=True)
    
    # Respuesta (solo lectura)
    store = StoreSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    credentials = serializers.SerializerMethodField(read_only=True)
    
    def get_credentials(self, obj):
        """Retorna las credenciales generadas del usuario."""
        return {
            'email': obj.get('user_email'),
            'password': 'nurax123',
            'username': obj.get('username')
        }
    
    def create(self, validated_data):
        """Crear Store + User + StoreMembership en una transacción atómica."""
        from django.db import transaction
        
        with transaction.atomic():
            # 1. Crear usuario con password default
            email = validated_data['owner_email']
            name = validated_data['owner_name']
            username = email.split('@')[0]  # Generar username desde email
            
            # Verificar que el email no exista
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError({'owner_email': 'Este email ya está registrado.'})
            
            user = User.objects.create_user(
                email=email,
                username=username,
                name=name,
                role=User.Role.CLIENTE,
                password='nurax123'  # Password por defecto
            )
            
            # 2. Crear tienda
            store = Store.objects.create(
                name=validated_data['store_name'],
                plan=validated_data.get('store_plan', 'basico'),
                tax_id=validated_data.get('store_tax_id', '')
            )
            
            # 3. Crear membresía (user es propietario de store)
            StoreMembership.objects.create(
                store=store,
                user=user,
                role=StoreMembership.Role.OWNER
            )
            
            return {
                'store': store,
                'user': user,
                'user_email': email,
                'username': username
            }


class StoreWithMembershipsSerializer(serializers.ModelSerializer):
    """Serializer para tienda con membresías."""
    
    memberships = StoreMembershipSerializer(many=True, read_only=True)
    
    class Meta:
        model = Store
        fields = ['id', 'name', 'plan', 'tax_id', 'active', 'memberships', 'created_at']


class OnboardingTiendaSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=200, required=True)
    identificador_fiscal = serializers.CharField(max_length=50, required=False, allow_blank=True)
    nicho = serializers.ChoiceField(
        choices=Store.Niche.choices,
        required=True
    )


class OnboardingConfiguracionSerializer(serializers.Serializer):
    fondo_inicial_defecto = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)


class OnboardingProveedorSerializer(serializers.Serializer):
    incluir = serializers.BooleanField(default=True)
    nombre = serializers.CharField(max_length=200, required=False, allow_blank=True)
    telefono = serializers.CharField(max_length=50, required=False, allow_blank=True)


class OnboardingWizardSerializer(serializers.Serializer):
    tienda = OnboardingTiendaSerializer()
    configuracion = OnboardingConfiguracionSerializer()
    proveedor_inicial = OnboardingProveedorSerializer()
