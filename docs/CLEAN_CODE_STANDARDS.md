# ESTÁNDARES DE CÓDIGO LIMPIO - Backend Nurax

## Principios Fundamentales

### 1. DRY (Don't Repeat Yourself)
Cada funcionalidad existe en **UN solo lugar**

❌ **Malo**: Validación en modelo + serializer + view
```python
# models.py
class Product(models.Model):
    price = DecimalField(validators=[MinValueValidator('0.01')])

# serializers.py
def validate_price(self, value):
    if value < Decimal('0.01'):
        raise ValidationError("...") 

# views.py
if product.price < 0:
    return error()
```

✅ **Bueno**: Validación en modelo + serializer solo donde necesario
```python
# models.py
class Product(models.Model):
    price = DecimalField(validators=[MinValueValidator(Decimal('0.01'))])

# serializers.py
# Solo para API-specific logic, el modelo valida datos
```

---

## Type Hints

### Regla: Siempre usar type hints

#### En Modelos
```python
from typing import Decimal

class Product(models.Model):
    name: str = models.CharField(max_length=200)
    price: Decimal = models.DecimalField(max_digits=12, decimal_places=2)
    stock: int = models.IntegerField(default=0)
    
    @property
    def status(self) -> str:
        """Retorna estado del stock."""
        if self.stock == 0:
            return 'out_of_stock'
        return 'in_stock'
```

#### En Managers
```python
class ProductQuerySet(models.QuerySet):
    def in_stock(self) -> QuerySet:
        return self.filter(stock__gt=10)
    
    def with_related(self) -> QuerySet:
        return self.select_related('category', 'supplier')

class ProductManager(models.Manager):
    def get_queryset(self) -> ProductQuerySet:
        return ProductQuerySet(self.model, using=self._db)
```

#### En Serializers
```python
from rest_framework import serializers
from decimal import Decimal

class ProductSerializer(serializers.ModelSerializer):
    category_name: str = serializers.CharField(
        source='category.name', 
        read_only=True
    )
    status: str = serializers.SerializerMethodField()
    
    def get_status(self, obj: Product) -> str:
        return obj.status
    
    def validate_price(self, value: Decimal) -> Decimal:
        if value < Decimal('0.01'):
            raise ValidationError("Precio debe ser > 0")
        return value
```

#### En Views
```python
from typing import Optional
from rest_framework.response import Response
from rest_framework import status

class ProductViewSet(viewsets.ModelViewSet):
    queryset: QuerySet = Product.objects.with_related()
    serializer_class: Type[serializers.Serializer] = ProductSerializer
    
    def list(self, request, *args, **kwargs) -> Response:
        """Listar todos los productos."""
        queryset: QuerySet = self.filter_queryset(self.get_queryset())
        page: Page = self.paginate_queryset(queryset)
        if page is not None:
            serializer: ProductSerializer = self.get_serializer(
                page, 
                many=True
            )
            return self.get_paginated_response(serializer.data)
        
        serializer: ProductSerializer = self.get_serializer(
            queryset, 
            many=True
        )
        return Response(serializer.data)
```

---

## Managers & QuerySets

### Patrón: Optimización de Queries

```python
# ✅ CORRECTO
class ProductQuerySet(models.QuerySet):
    def in_stock(self) -> QuerySet:
        return self.filter(stock__gt=10)
    
    def with_related(self) -> QuerySet:
        """Optimiza queries relacionales."""
        return self.select_related(
            'user',
            'category',
            'supplier'
        )

class ProductManager(models.Manager):
    def get_queryset(self) -> ProductQuerySet:
        return ProductQuerySet(self.model, using=self._db)
    
    def in_stock(self) -> ProductQuerySet:
        return self.get_queryset().in_stock()

# En view: evita N+1 query problem
products = Product.objects.in_stock().with_related()
```

### Checklist para Managers
- ✅ Heredar de `models.Manager` + custom `QuerySet`
- ✅ Implementar `get_queryset()` retornando custom QuerySet
- ✅ Delegadores en Manager usan `self.get_queryset()`
- ✅ QuerySet con métodos reutilizables
- ✅ Siempre considerar select_related/prefetch_related

---

## Validators 

### Ubicación: Centralizar en `app/validators.py`

```python
# products/validators.py
from django.core.exceptions import ValidationError
from decimal import Decimal

def validate_sku_format(value: str) -> None:
    """
    Valida formato de SKU.
    - Min 3 caracteres
    - Max 50 caracteres
    - Alfanumérico
    """
    if not (3 <= len(value) <= 50):
        raise ValidationError(
            "SKU debe tener entre 3 y 50 caracteres"
        )
    if not value.replace('-', '').replace('_', '').isalnum():
        raise ValidationError(
            "SKU solo puede contener letras, números, guiones y guiones bajos"
        )

def validate_positive_decimal(value: Decimal) -> None:
    """Valida que un decimal sea positivo."""
    if value <= Decimal('0'):
        raise ValidationError("El valor debe ser positivo")

# En modelo
class Product(models.Model):
    sku = models.CharField(
        max_length=50,
        validators=[validate_sku_format],
        help_text="ID único del producto"
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[validate_positive_decimal],
        help_text="Precio unitario"
    )
```

---

## Serializers

### Multi-Layer Validation

```python
from rest_framework import serializers
from products.models import Product
from products.validators import validate_sku_format

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'category', 'category_name',
            'price', 'stock', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'status']
    
    def validate_sku(self, value: str) -> str:
        """Valida formato y unicidad de SKU."""
        # Layer 1: validar formato (delegado a model validator)
        validate_sku_format(value)
        
        # Layer 2: validar unicidad en contexto de usuario
        user = self.context['request'].user
        if Product.objects.filter(
            user=user,
            sku=value
        ).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError(
                "SKU ya existe para este usuario"
            )
        
        return value
    
    def validate_price(self, value: Decimal) -> Decimal:
        """Valida precio en contexto de negocio."""
        if value < Decimal('0.01'):
            raise serializers.ValidationError(
                "Precio mínimo es $0.01"
            )
        return value
    
    def validate_stock(self, value: int) -> int:
        """Valida stock no negativo."""
        if value < 0:
            raise serializers.ValidationError(
                "Stock no puede ser negativo"
            )
        return value
```

---

## Views & ViewSets

### Patrón: Responsabilidad Única

```python
from typing import Optional, Dict, Any
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from products.models import Product
from products.serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de productos.
    
    Acciones disponibles:
    - list: Listar todos los productos
    - create: Crear nuevo producto
    - retrieve: Obtener detalle
    - update: Actualizar
    - destroy: Eliminar
    - low_stock: Productos con bajo stock
    - out_of_stock: Productos sin stock
    """
    
    queryset = Product.objects.with_related()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'sku']
    ordering_fields = ['created_at', 'price', 'stock']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Personaliza queryset según usuario y filtros.
        """
        user = self.request.user
        queryset = self.queryset.filter(user=user)
        
        # Filtro por categoría si se proporciona
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        return queryset.with_related()
    
    def perform_create(self, serializer: ProductSerializer) -> None:
        """Asigna usuario al crear producto."""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request: Request) -> Response:
        """Retorna productos con bajo stock."""
        products = self.get_queryset().filter(stock__lte=10, stock__gt=0)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def out_of_stock(self, request: Request) -> Response:
        """Retorna productos sin stock."""
        products = self.get_queryset().filter(stock=0)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
```

---

## Exceptions

### Centralizar en `api/exceptions.py`

```python
from rest_framework.exceptions import APIException
from rest_framework import status

class InsufficientStockError(APIException):
    """Excepción cuando no hay suficiente stock."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Stock insuficiente para esta operación"
    default_code = 'insufficient_stock'

class InvalidTransactionError(APIException):
    """Excepción para transacciones inválidas."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Transacción inválida"
    default_code = 'invalid_transaction'

class PermissionDeniedError(APIException):
    """Excepción de permisos insuficientes."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "No tiene permisos para esta acción"
    default_code = 'permission_denied'

# Uso en view
class SaleViewSet(viewsets.ModelViewSet):
    def create(self, request):
        product = get_object_or_404(Product, id=request.data['product_id'])
        if product.stock < request.data['quantity']:
            raise InsufficientStockError()
        # ... resto de lógica
```

---

## Constants

### Centralizar en `api/constants.py`

```python
# api/constants.py

# ===== SALE STATUS =====
class SaleStatus:
    COMPLETED = 'completed'
    PENDING = 'pending'
    CANCELLED = 'cancelled'
    CREDIT = 'credit'
    LAYAWAY = 'layaway'
    
    CHOICES = [
        (COMPLETED, 'Completada'),
        (PENDING, 'Pendiente'),
        (CANCELLED, 'Cancelada'),
        (CREDIT, 'Crédito'),
        (LAYAWAY, 'Apartado'),
    ]

# ===== INVENTORY =====
STOCK_LOW_THRESHOLD = 10
STOCK_CRITICAL_THRESHOLD = 5

# ===== PAGINATION =====
PAGINATION_MAX_SIZE = 100
PAGINATION_DEFAULT_SIZE = 20

# ===== ROLES =====
class UserRole:
    ADMIN = 'admin'
    CLIENT = 'cliente'

# Uso en código
from api.constants import SaleStatus, STOCK_LOW_THRESHOLD

class Sale(models.Model):
    status = models.CharField(
        max_length=15,
        choices=SaleStatus.CHOICES,
        default=SaleStatus.COMPLETED
    )
```

---

## Docstrings

### Estilo: Google Style Docstrings

```python
def calculate_profit_margin(cost: Decimal, price: Decimal) -> Decimal:
    """
    Calcula el margen de ganancia porcentual.
    
    Args:
        cost: Costo unitario del producto
        price: Precio de venta
    
    Returns:
        Margen de ganancia como decimal (0-100)
    
    Raises:
        ValueError: Si cost o price son negativos
    
    Example:
        >>> calculate_profit_margin(Decimal('10'), Decimal('15'))
        Decimal('33.33')
    """
    if cost < 0 or price < 0:
        raise ValueError("Costo y precio deben ser positivos")
    
    margin = ((price - cost) / cost) * 100
    return margin.quantize(Decimal('0.01'))


class ProductManager(models.Manager):
    """
    Manager customizado para Product model.
    
    Métodos adicionales:
        - in_stock(): Productos con stock > 10
        - low_stock(): Productos con stock <= 10
        - with_related(): Optimiza queries con select_related
    """
    
    def get_queryset(self) -> QuerySet:
        """Retorna custom QuerySet optimizado."""
        return ProductQuerySet(self.model, using=self._db)
```

---

## Testing

### Patrón: AAA (Arrange-Act-Assert)

```python
from django.test import TestCase
from products.models import Product, Category
from decimal import Decimal

class ProductModelTest(TestCase):
    """Tests para modelo Product."""
    
    def test_product_status_low_stock(self):
        """Verifica que status es 'low_stock' cuando 0 < stock <= 10."""
        # Arrange: Preparar datos
        category = Category.objects.create(name='Electronics')
        product = Product.objects.create(
            name='Laptop',
            category=category,
            sku='SKU-001',
            stock=8,
            price=Decimal('999.99')
        )
        
        # Act: Ejecutar
        actual_status = product.status
        
        # Assert: Verificar
        self.assertEqual(actual_status, 'low_stock')
    
    def test_product_invalid_negative_stock(self):
        """Verifica que no se puede crear producto con stock negativo."""
        category = Category.objects.create(name='Electronics')
        
        with self.assertRaises(ValidationError):
            product = Product(
                name='Invalid',
                category=category,
                sku='SKU-BAD',
                stock=-5,
                price=Decimal('100')
            )
            product.full_clean()
```

---

## Checklist para Code Review

- ✅ Type hints en todas las funciones
- ✅ Docstrings en clases y métodos públicos
- ✅ Validación multi-capa (model + serializer + view)
- ✅ Managers con QuerySet optimization
- ✅ Excepciones centralizadas
- ✅ Constantes en api/constants.py
- ✅ Tests con patrones AAA
- ✅ Sin hardcoding de valores
- ✅ Sin duplicación de lógica (DRY)
- ✅ Índices en campos filtrados frecuentemente

---

## Recursos

- [PEP 8 - Style Guide for Python Code](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Django Coding Style](https://docs.djangoproject.com/en/6.0/internals/contributing/coding-style/)
