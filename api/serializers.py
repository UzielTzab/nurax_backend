from rest_framework import serializers
import cloudinary.uploader
from .models import User, Client, Product, Category, Supplier, Sale, SaleItem, StoreProfile

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

class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model  = Sale
        fields = ['id', 'transaction_id', 'user', 'status', 'total', 'items', 'created_at']
        
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
            # Descuentar stock automáticamente
            if product:
                product.stock = max(0, product.stock - item['quantity'])
                product.save()
        return sale

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Client
        fields = ['id', 'name', 'email', 'company', 'plan', 'active', 'created_at', 'avatar_color']

class UserSerializer(serializers.ModelSerializer):
    # Campo virtual de solo escritura para recibir el archivo de imagen del frontend
    avatar_file = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model  = User
        fields = ['id', 'username', 'password', 'name', 'email', 'role', 'avatar_url', 'avatar_file']
        extra_kwargs = {
            'password':   {'write_only': True},
            'username':   {'required': False, 'allow_blank': True},
            'avatar_url': {'read_only': True},  # Solo el backend puede escribir este campo
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
        return User.objects.create_user(
            username=username,
            email=email,
            password=validated_data.pop('password'),
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
