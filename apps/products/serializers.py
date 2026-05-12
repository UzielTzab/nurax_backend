from decimal import Decimal
from rest_framework import serializers
from .models import Product, Category, Supplier, ProductPackaging, ProductCode, ProductVariation


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'store', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'id', 'store', 'name', 'contact_person', 'phone', 'email',
            'website', 'address', 'contact_info', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductPackagingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPackaging
        fields = ['id', 'product', 'name', 'quantity_per_unit']
        read_only_fields = ['id']


class ProductCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCode
        fields = ['id', 'product', 'code', 'code_type', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariation
        fields = ['id', 'product', 'variation_type', 'variation_value', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    packagings = ProductPackagingSerializer(many=True, read_only=True)
    codes = ProductCodeSerializer(many=True, read_only=True)
    variations = ProductVariationSerializer(many=True, read_only=True)
    image_file = serializers.ImageField(write_only=True, required=False, allow_null=True)
    remove_image = serializers.BooleanField(write_only=True, required=False, default=False)
    
    class Meta:
        model = Product
        fields = [
            'id', 'store', 'name', 'base_cost', 'sale_price', 'current_stock',
            'category', 'category_name', 'supplier', 'supplier_name',
            'image_url', 'image_file', 'remove_image',
            'packagings', 'codes', 'variations', 'created_at', 'updated_at'
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
        import cloudinary.uploader
        try:
            result = cloudinary.uploader.upload(
                image_file,
                folder='products',
                transformation=[{'width': 800, 'height': 800, 'crop': 'limit'}]
            )
            return result.get('secure_url')
        except Exception as exception_error:
            raise serializers.ValidationError({'image_file': f'Error al subir imagen: {exception_error}'})

    def create(self, validated_data):
        image_file = validated_data.pop('image_file', None)
        validated_data.pop('remove_image', None)
        validated_data.setdefault('base_cost', Decimal('0.00'))
        validated_data.setdefault('sale_price', Decimal('0.01'))
        validated_data.setdefault('current_stock', 0)
        
        if image_file:
            validated_data['image_url'] = self._upload_to_cloudinary(image_file)
            
        return super().create(validated_data)

    def update(self, instance, validated_data):
        image_file = validated_data.pop('image_file', None)
        remove_image = validated_data.pop('remove_image', False)

        if remove_image and not image_file:
            validated_data['image_url'] = None

        if image_file:
            validated_data['image_url'] = self._upload_to_cloudinary(image_file)

        return super().update(instance, validated_data)

    def validate_base_cost(self, base_cost_value):
        if base_cost_value < 0:
            raise serializers.ValidationError("Costo base no puede ser negativo")
        return base_cost_value

    def validate_sale_price(self, sale_price_value):
        if sale_price_value <= 0:
            raise serializers.ValidationError("Precio de venta debe ser mayor a 0")
        return sale_price_value

    def validate(self, product_data):
        base_cost = product_data.get('base_cost')
        sale_price = product_data.get('sale_price')
        
        if base_cost is not None and sale_price is not None:
            if base_cost > sale_price:
                raise serializers.ValidationError(
                    "El costo base no puede ser mayor que el precio de venta"
                )
        return product_data


class ProductSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'base_cost', 'sale_price', 'current_stock']
        read_only_fields = ['id']
