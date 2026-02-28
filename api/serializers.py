from rest_framework import serializers
import cloudinary.uploader
from .models import User, Client, Product, Category, Supplier, Sale, SaleItem

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
    class Meta:
        model  = User
        fields = ['id', 'username', 'password', 'name', 'email', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': False, 'allow_blank': True}
        }

    def create(self, validated_data):
        # Generar un username basado en el email si no se manda uno
        email = validated_data['email']
        username = validated_data.get('username')
        if not username:
            username = email.split('@')[0]
            
        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password'],
            name=validated_data.get('name', ''),
            role=validated_data.get('role', 'cliente')
        )
        return user
