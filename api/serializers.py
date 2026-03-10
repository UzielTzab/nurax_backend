from rest_framework import serializers
import cloudinary.uploader
from .models import (
    User, Client, Product, Category, Supplier, Sale, SaleItem, StoreProfile,
    InventoryTransaction, Expense, CashShift, SalePayment
)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'email', 'phone', 'company', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    status        = serializers.ReadOnlyField()
    # image_file es virtual: lo usamos para atrapar el archivo en el form-data del frontend
    image_file    = serializers.ImageField(write_only=True, required=False)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'category_name', 'supplier',
                  'sku', 'stock', 'price', 'image_url', 'image_file',
                  'status', 'created_at', 'updated_at']
                  
    def create(self, validated_data):
        image_file = validated_data.pop('image_file', None)
        if image_file:
            # Subimos el archivo capturado a Cloudinary
            upload_data = cloudinary.uploader.upload(image_file, folder="products")
            # Guardamos la URL segura retornada en nuestro campo string
            validated_data['image_url'] = upload_data.get('secure_url')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        image_file = validated_data.pop('image_file', None)
        if image_file:
            upload_data = cloudinary.uploader.upload(image_file, folder="products")
            validated_data['image_url'] = upload_data.get('secure_url')
        return super().update(instance, validated_data)

class SaleItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()
    product_name = serializers.CharField(required=False, allow_blank=True, default='')
    
    class Meta:
        model  = SaleItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price', 'subtotal']

class SalePaymentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SalePayment
        fields = ['id', 'amount', 'created_at', 'user']

class SaleSerializer(serializers.ModelSerializer):
    items    = SaleItemSerializer(many=True)
    payments = SalePaymentSerializer(many=True, read_only=True)
    user     = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model  = Sale
        fields = ['id', 'transaction_id', 'user', 'status', 'total', 'items', 'payments', 'created_at']
        
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        sale = Sale.objects.create(**validated_data)
        for item in items_data:
            product = item.get('product')
            prod_name_fallback = item.pop('product_name', '')
            SaleItem.objects.create(
                sale=sale,
                product_name=product.name if product else prod_name_fallback,
                **item
            )
            # Descuentar stock automáticamente y registrar en Kárdex
            if product:
                product.stock = max(0, product.stock - item['quantity'])
                product.save()
                
                InventoryTransaction.objects.create(
                    product=product,
                    transaction_type=InventoryTransaction.TransactionType.OUT,
                    quantity=item['quantity'],
                    reason=f'Venta {sale.transaction_id}',
                    user=validated_data.get('user')
                )
        return sale

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Client
        fields = ['id', 'name', 'email', 'company', 'plan', 'active', 'created_at', 'avatar_color']

class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para validar cambio de contraseña seguro."""
    current_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='Tu contraseña actual para confirmar identidad'
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='Tu nueva contraseña (mín 8 caract, mayúscula, número)'
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='Confirma tu nueva contraseña'
    )
    
    def validate(self, data):
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        
        current_pwd = data.get('current_password')
        new_pwd = data.get('new_password')
        confirm_pwd = data.get('confirm_password')
        
        # 1. Validar que las nuevas contraseñas coincidan
        if new_pwd != confirm_pwd:
            raise serializers.ValidationError({
                'confirm_password': 'Las contraseñas no coinciden.'
            })
        
        # 2. Validar que la nueva no sea igual a la actual
        user = self.context.get('request').user
        if user.check_password(new_pwd):
            raise serializers.ValidationError({
                'new_password': 'La nueva contraseña no puede ser igual a la actual.'
            })
        
        # 3. Validar políticas de seguridad de Django
        try:
            validate_password(new_pwd, user=user)
        except ValidationError as e:
            raise serializers.ValidationError({
                'new_password': e.messages
            })
        
        return data


class UserSerializer(serializers.ModelSerializer):
    # Campo virtual de solo escritura para recibir el archivo de imagen del frontend
    avatar_file = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model  = User
        fields = ['id', 'username', 'password', 'name', 'email', 'role', 'is_active', 'date_joined', 'avatar_url', 'avatar_file']
        extra_kwargs = {
            'password':    {'write_only': True, 'required': False},
            'username':    {'required': False, 'allow_blank': True},
            'avatar_url':  {'read_only': True},  # Solo el backend puede escribir este campo
            'is_active':   {'read_only': True},
            'date_joined': {'read_only': True},
        }

    def _handle_avatar(self, validated_data):
        """Sube la imagen a Cloudinary y retorna la secure_url si se recibió un archivo."""
        avatar_file = validated_data.pop('avatar_file', None)
        if avatar_file:
            result = cloudinary.uploader.upload(
                avatar_file,
                folder='avatars',
                transformation=[{'width': 400, 'height': 400, 'crop': 'fill', 'gravity': 'face'}]
            )
            validated_data['avatar_url'] = result.get('secure_url')
        return validated_data

    def create(self, validated_data):
        validated_data = self._handle_avatar(validated_data)
        email    = validated_data['email']
        username = validated_data.pop('username', None) or email.split('@')[0]
        # Si no se provee contraseña (o se manda un string vacío) asignar una por defecto
        pwd = validated_data.pop('password', None)
        password = pwd if pwd else 'nurax123'
        
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            name=validated_data.get('name', ''),
            role=validated_data.get('role', 'cliente'),
            avatar_url=validated_data.get('avatar_url'),
        )

    def update(self, instance, validated_data):
        validated_data = self._handle_avatar(validated_data)
        # Manejar el password de manera segura si se manda en una edición
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class StoreProfileSerializer(serializers.ModelSerializer):
    # Campo virtual para recibir el archivo del logo desde el frontend
    logo_file = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model  = StoreProfile
        fields = ['id', 'store_name', 'currency_symbol', 'address',
                  'phone', 'ticket_message', 'logo_url', 'logo_file', 'updated_at']
        extra_kwargs = {
            'logo_url': {'read_only': True},  # El backend controla este campo
        }

    def update(self, instance, validated_data):
        logo_file = validated_data.pop('logo_file', None)
        if logo_file:
            result = cloudinary.uploader.upload(logo_file, folder='logos')
            validated_data['logo_url'] = result.get('secure_url')
        return super().update(instance, validated_data)


class InventoryTransactionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = InventoryTransaction
        fields = ['id', 'product', 'product_name', 'transaction_type', 'quantity', 'reason', 'user', 'created_at']


class ExpenseSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    # Útil para recibir un archivo de comprobante opcional
    receipt_file = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = Expense
        fields = ['id', 'amount', 'category', 'description', 'receipt_url', 'receipt_file', 'user', 'date']
        extra_kwargs = {
            'receipt_url': {'read_only': True}
        }

    def create(self, validated_data):
        receipt_file = validated_data.pop('receipt_file', None)
        if receipt_file:
            result = cloudinary.uploader.upload(receipt_file, folder="expenses")
            validated_data['receipt_url'] = result.get('secure_url')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        receipt_file = validated_data.pop('receipt_file', None)
        if receipt_file:
            result = cloudinary.uploader.upload(receipt_file, folder="expenses")
            validated_data['receipt_url'] = result.get('secure_url')
        return super().update(instance, validated_data)


class CashShiftSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = CashShift
        fields = ['id', 'user', 'user_name', 'opened_at', 'closed_at', 
                  'starting_cash', 'expected_cash', 'actual_cash', 'difference']

