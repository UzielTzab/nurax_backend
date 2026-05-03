"""
Serializadores para la app Products.
ARCHITECTURE_V2: Catálogo, categorías, proveedores y códigos de producto.
"""
from decimal import Decimal
from rest_framework import serializers
from .models import Product, Category, Supplier, ProductPackaging, ProductCode


class CategorySerializer(serializers.ModelSerializer):
    """Serializer para categorías."""
    
    class Meta:
        model = Category
        fields = ['id', 'store', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer para proveedores."""
    
    class Meta:
        model = Supplier
        fields = [
            'id',
            'store',
            'name',
            'contact_person',
            'phone',
            'email',
            'website',
            'address',
            'contact_info',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductPackagingSerializer(serializers.ModelSerializer):
    """Serializer para empaques de producto."""
    
    class Meta:
        model = ProductPackaging
        fields = ['id', 'product', 'name', 'quantity_per_unit']
        read_only_fields = ['id']


class ProductCodeSerializer(serializers.ModelSerializer):
    """Serializer para códigos de producto."""
    
    class Meta:
        model = ProductCode
        fields = ['id', 'product', 'code', 'code_type', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer para productos completos."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    packagings = ProductPackagingSerializer(many=True, read_only=True)
    codes = ProductCodeSerializer(many=True, read_only=True)

    # Mismo patrón que avatar en el perfil de usuario:
    # - image_file: recibe el archivo (write_only, nunca se devuelve)
    # - image_url:  devuelve la URL pública de Cloudinary (read_only)
    image_file = serializers.ImageField(write_only=True, required=False, allow_null=True)
    remove_image = serializers.BooleanField(write_only=True, required=False, default=False)
    
    class Meta:
        model = Product
        fields = [
            'id', 'store', 'name', 'base_cost', 'sale_price', 'current_stock',
            'category', 'category_name', 'supplier', 'supplier_name',
            'image_url', 'image_file', 'remove_image',
            'packagings', 'codes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'image_url', 'created_at', 'updated_at']
        extra_kwargs = {
            'store': {'required': False},
            'category': {'required': False, 'allow_null': True},
            'supplier': {'required': False, 'allow_null': True},
            'base_cost': {'required': False},
            'sale_price': {'required': False},
            'current_stock': {'required': False},
        }

    def _upload_to_cloudinary(self, image_file):
        """Sube el archivo a Cloudinary y retorna la URL segura."""
        import cloudinary.uploader
        try:
            result = cloudinary.uploader.upload(
                image_file,
                folder='products',
                transformation=[{'width': 800, 'height': 800, 'crop': 'limit'}]
            )
            return result.get('secure_url')
        except Exception as exc:
            raise serializers.ValidationError({'image_file': f'Error al subir imagen: {exc}'})

    def create(self, validated_data):
        """Crea el producto. Si viene image_file, lo sube a Cloudinary."""
        image_file = validated_data.pop('image_file', None)
        validated_data.pop('remove_image', None)
        validated_data.setdefault('base_cost', Decimal('0.00'))
        validated_data.setdefault('sale_price', Decimal('0.01'))
        validated_data.setdefault('current_stock', 0)
        if image_file:
            validated_data['image_url'] = self._upload_to_cloudinary(image_file)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Actualiza el producto y soporta quitar imagen sin subir una nueva."""
        image_file = validated_data.pop('image_file', None)
        remove_image = validated_data.pop('remove_image', False)

        if remove_image and not image_file:
            validated_data['image_url'] = None

        if image_file:
            validated_data['image_url'] = self._upload_to_cloudinary(image_file)

        return super().update(instance, validated_data)

    def validate_base_cost(self, value):
        if value < 0:
            raise serializers.ValidationError("Costo base no puede ser negativo")
        return value

    def validate_sale_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Precio de venta debe ser mayor a 0")
        return value

    def validate(self, data):
        base_cost = data.get('base_cost')
        sale_price = data.get('sale_price')
        if base_cost is not None and sale_price is not None:
            if base_cost > sale_price:
                raise serializers.ValidationError(
                    "El costo base no puede ser mayor que el precio de venta"
                )
        return data


class ProductSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple para productos (sin relaciones)."""
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'base_cost', 'sale_price', 'current_stock']
        read_only_fields = ['id']
