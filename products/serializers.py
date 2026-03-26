"""
Serializadores para la app Products.
"""
from rest_framework import serializers
from .models import Product, Category, Supplier


class CategorySerializer(serializers.ModelSerializer):
    """Serializador para categorías."""
    
    class Meta:
        model = Category
        fields = ['id', 'name']
        read_only_fields = ['id']


class SupplierSerializer(serializers.ModelSerializer):
    """Serializador para proveedores."""
    
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'email', 'phone', 'company', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    """Serializador para productos con validación completa."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'stock', 'sku', 'price',
            'category', 'category_name', 'supplier', 'supplier_name',
            'image_url', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']
    
    def validate_stock(self, value: int) -> int:
        """Validar stock no sea negativo."""
        if value < 0:
            raise serializers.ValidationError("Stock no puede ser negativo")
        return value
    
    def validate_sku(self, value: str) -> str:
        """Validar SKU único por usuario."""
        request = self.context.get('request')
        if not request:
            return value
        
        if Product.objects.filter(
            user=request.user,
            sku=value
        ).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("SKU ya existe para este usuario")
        return value
    
    def get_status(self, obj: Product) -> str:
        """Estado del producto basado en stock."""
        return obj.status
