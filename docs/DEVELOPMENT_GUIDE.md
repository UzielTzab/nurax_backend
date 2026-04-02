# Guía de Desarrollo - Nurax Backend

Guía completa para desarrolladores que trabajan en el backend de Nurax.

---

## Índice

1. [Setup Inicial](#setup-inicial)
2. [Desarrollo Local vs Docker](#desarrollo-local-vs-docker)
3. [Estructura de Proyecto](#estructura-de-proyecto)
4. [Crear Nuevas Features](#crear-nuevas-features)
5. [Migraciones de BD](#migraciones-de-bd)
6. [Testing](#testing)
7. [Debugging](#debugging)
8. [Buenas Prácticas](#buenas-prácticas)
9. [Troubleshooting](#troubleshooting)

---

## Setup Inicial

### **Primera vez**

```bash
# 1. Clonar repo
git clone <repo-url>
cd nurax_backend

# 2. Crear .env (copiar de .env.example si existe)
cp .env.example .env
# O crear manual con variables (ver AGENT.md)

# 3. Opción A: Con Docker (recomendado)
docker-compose up --build

# Opción B: Local sin Docker
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python init_db.py
python manage.py runserver
```

### **Verificar que funciona**

```bash
# Si uso Docker:
docker exec nurax_api python manage.py check

# Si local:
python manage.py check

# Debería imprimir "System check identified no issues"
```

---

## Desarrollo Local vs Docker

### **Con Docker (Recomendado)**

✅ **Ventajas:**
- Entorno aislado idéntico a producción
- No contamina máquina local
- Fácil resetear todo: `docker-compose down -v`
- Base de datos en contenedor separado

❌ **Desventajas:**
- Un poco más lento
- Requiere Docker instalado

```bash
# Iniciar
docker-compose up

# Detener
docker-compose down

# Ver logs
docker logs -f nurax_api

# Shell dentro del contenedor
docker exec -it nurax_api bash

# Ejecutar comando
docker exec nurax_api python manage.py shell
```

### **Local sin Docker**

✅ **Ventajas:**
- Más rápido
- Directo con Python
- Debugging más fácil

❌ **Desventajas:**
- Necesita PostgreSQL instalado localmente
- Requiere setup manual
- Difícil sincronizar versiones

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar deps
pip install -r requirements.txt

# Configurar BD (debe estar corriendo PostgreSQL)
# Actualizar .env: DB_HOST=localhost

# Migraciones
python manage.py migrate

# Crear super user
python manage.py createsuperuser

# Correr
python manage.py runserver
```

### **Recomendación**

**Usa Docker para desarrollo regular.** Usa local solo si ya tienes PostgreSQL y quieres debugging IDE.

---

## Estructura de Proyecto

```
api/
├── models.py              # 🔴 CRÍTICO - Todos los modelos aquí
├── views.py               # 🔴 CRÍTICO - Todos los ViewSets aquí
├── serializers.py         # 🟡 ViewSet serializers
├── urls.py                # 🟡 Rutas (SimpleRouter)
├── pagination.py          # 🟢 Custom pagination
├── admin.py               # 🟢 Django admin
├── apps.py                # 🟢 Config app
├── tests.py               # 🟢 Tests
└── migrations/            # 🟢 Historia BD
    ├── __init__.py
    └── 000X_description.py

nurax_backend/
├── settings.py            # 🔴 Settings principales
├── urls.py                # 🟡 URLs raíz
├── asgi.py                # 🟢 ASGI
└── wsgi.py                # 🟢 WSGI

Raíz:
├── manage.py              # 🟡 Django CLI
├── requirements.txt       # 🔴 Dependencias
├── docker-compose.yml     # 🟡 Docker config
├── Dockerfile             # 🟡 Docker image
├── init_db.py             # 🟡 Script inicialización
├── populate_db.py         # 🟢 Datos prueba
└── README.md              # 📖 Documentación uso
```

**Colores:**
- 🔴 **CRÍTICO**: Modificar frecuentemente
- 🟡 **IMPORTANTE**: Ocasionalmente
- 🟢 **NORMAL**: Rara vez

---

## Crear Nuevas Features

### **Checklist: Agregar un Modelo**

#### **1. Definir el Modelo** (`api/models.py`)

```python
class MyModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
```

**Convenciones:**
- Siempre incluir `user = ForeignKey(User)` para multi-tenant
- Siempre incluir `created_at`, `updated_at`
- Implementar `__str__()`

#### **2. Crear Serializer** (`api/serializers.py`)

```python
class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = ['id', 'name', 'description', 'created_at', 'user']
        read_only_fields = ['created_at', 'user']
```

#### **3. Crear ViewSet** (`api/views.py`)

```python
from rest_framework import viewsets, permissions

class MyModelViewSet(viewsets.ModelViewSet):
    serializer_class = MyModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # 🔴 SIEMPRE filtrar por usuario actual
        return MyModel.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # 🔴 SIEMPRE asignar usuario
        serializer.save(user=self.request.user)
```

#### **4. Registrar Ruta** (`api/urls.py`)

```python
from rest_framework.routers import SimpleRouter
from .views import MyModelViewSet

router = SimpleRouter()
router.register(r'my-models', MyModelViewSet, basename='mymodel')

urlpatterns = [
    path('api/', include(router.urls)),
]
```

#### **5. Registrar en Admin** (`api/admin.py`)

```python
@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
```

#### **6. Crear Migración**

```bash
# En Docker:
docker exec nurax_api python manage.py makemigrations

# Local:
python manage.py makemigrations

# Ver qué cambió
cat api/migrations/000X_auto.py

# Aplicar:
docker exec nurax_api python manage.py migrate
# o
python manage.py migrate
```

#### **7. Test** (`api/tests.py`)

```python
from django.test import TestCase
from rest_framework.test import APITestCase
from api.models import MyModel, User

class MyModelTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            password='test123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_mymodel(self):
        response = self.client.post('/api/my-models/', {
            'name': 'Test',
            'description': 'Test description'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(MyModel.objects.count(), 1)
    
    def test_list_mymodel(self):
        MyModel.objects.create(
            user=self.user,
            name='Test'
        )
        response = self.client.get('/api/my-models/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
```

#### **8. Documentar**

Actualizar `docs/API_ENDPOINTS.md`:
```markdown
## My Models

### List/Create

**GET** `/api/my-models/` - Listar modelos
**POST** `/api/my-models/` - Crear modelo
```

---

### **Checklist: Modificar un Modelo Existente**

```bash
# 1. Editar api/models.py
# 2. Actualizar serializer si es necesario
# 3. Actualizar ViewSet si hay lógica nueva
# 4. Crear migración
docker exec nurax_api python manage.py makemigrations

# 5. Ver migración (sanity check)
cat api/migrations/000X_auto.py

# 6. Aplicar
docker exec nurax_api python manage.py migrate

# 7. Test en shell
docker exec -it nurax_api python manage.py shell
>>> from api.models import MyModel
>>> MyModel.objects.all()

# 8. Retest con API
curl -X GET http://localhost:8000/api/my-models/ ...
```

---

## Migraciones de BD

### **¿Qué es una Migración?**

Un archivo Python que describe cambios en la BD. Django las crea automáticamente y las guarda en `api/migrations/`.

### **Hacer Cambios a Modelos**

```bash
# 1. Editar api/models.py
nano api/models.py

# 2. Django *detecta* cambios y crea archivo de migración
docker exec nurax_api python manage.py makemigrations

# Salida:
# Migrations for 'api':
#   api/migrations/0014_mymodel.py

# 3. Ver lo que hará (SIEMPRE verificar!)
cat api/migrations/0014_mymodel.py

# 4. Aplicar cambio a BD
docker exec nurax_api python manage.py migrate

# 5. Verificar que funciona
docker exec nurax_api python manage.py check
```

### **Ver Estado Migraciones**

```bash
# Ver todas y cuál está aplicada
docker exec nurax_api python manage.py showmigrations

# Salida:
# api
#  [X] 0001_initial
#  [X] 0002_alter_user_email
#  [ ] 0003_new_model  ← no aplicada aún
```

### **Revertir Migración**

```bash
# Volver a migración anterior
docker exec nurax_api python manage.py migrate api 0012

# Volver a estado sin migraciones
docker exec nurax_api python manage.py migrate api zero
```

### **Casos Especiales**

#### **Agregar campo NOT NULL sin default**

```python
# ❌ MAL
new_field = models.CharField(max_length=100)  # Fallará

# ✅ BIEN
new_field = models.CharField(max_length=100, default='')
# O
new_field = models.CharField(max_length=100, null=True, blank=True)
```

#### **Renombrar campo**

```bash
# 1. Editar modelo (cambiar nombre)
# 2. makemigrations
docker exec nurax_api python manage.py makemigrations

# 3. Django pregunta si es un rename
# Responder Sí cuando pregunte

# 4. Aplicar
docker exec nurax_api python manage.py migrate
```

#### **Eliminar campo**

```python
# En models.py: simplemente eliminar línea
# Luego:
docker exec nurax_api python manage.py makemigrations
docker exec nurax_api python manage.py migrate
```

---

## Testing

### **Correr Tests**

```bash
# Todos los tests
docker exec nurax_api python manage.py test

# Solo app 'api'
docker exec nurax_api python manage.py test api

# Test específico
docker exec nurax_api python manage.py test api.tests.MyModelTest

# Con verbose
docker exec nurax_api python manage.py test -v 2
```

### **Escribir Tests Rápido**

```python
# En api/tests.py
from django.test import TestCase
from rest_framework.test import APITestCase
from api.models import Product, User

class ProductViewSetTest(APITestCase):
    def setUp(self):
        # Crear usuario y autenticar
        self.user = User.objects.create_user(
            email='test@test.com',
            password='test123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Crear datos de prueba
        self.product = Product.objects.create(
            user=self.user,
            name='iPhone 15',
            sku='IPHONE-15',
            stock=10,
            price='999.99'
        )
    
    def test_list_products(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_product(self):
        response = self.client.post('/api/products/', {
            'name': 'Samsung S24',
            'sku': 'SAMSUNG-S24',
            'stock': 5,
            'price': '899.99'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 2)
    
    def test_update_product_stock(self):
        response = self.client.patch(f'/api/products/{self.product.id}/', {
            'stock': 20
        })
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 20)
    
    def test_filter_by_status(self):
        Product.objects.create(
            user=self.user,
            name='Low Stock Item',
            sku='LOW-STOCK',
            stock=5,
            price='49.99'
        )
        response = self.client.get('/api/products/?status=low_stock')
        self.assertEqual(len(response.data['results']), 1)
    
    def test_unauthenticated_request(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 401)
```

---

## Debugging

### **Django Shell**

```bash
docker exec -it nurax_api python manage.py shell
```

Luego:
```python
>>> from api.models import Product, User

# Obtener usuario
>>> user = User.objects.first()

# Contar productos
>>> Product.objects.filter(user=user).count()

# Filtrar
>>> products = Product.objects.filter(stock__lte=10)

# Actualizar
>>> product = Product.objects.get(id=1)
>>> product.stock = 100
>>> product.save()

# Borrar
>>> Product.objects.get(id=999).delete()
```

### **Ver Queries SQL**

```bash
docker exec -it nurax_api python manage.py shell

>>> from django.db import connection
>>> from django.test.utils import CaptureQueriesContext
>>> from api.models import Product

>>> with CaptureQueriesContext(connection) as context:
...     products = Product.objects.select_related('category').all()
...
>>> for query in context:
...     print(query['sql'])
```

### **Logs en Vivo**

```bash
# Ver logs API
docker logs -f nurax_api

# Ver logs DB
docker logs -f nurax_db

# Buscar error específico
docker logs nurax_api | grep ERROR
```

### **Acceder a BD Directamente**

```bash
# Conectar a PostgreSQL
docker exec -it nurax_db psql -U nurax_user -d nurax_db

# Listar tablas
\dt

# Ver datos
SELECT * FROM api_product;

# Ver schema tabla
\d api_product

# Salir
\q
```

---

## Buenas Prácticas

### **1. Filtrar Siempre por Usuario**

```python
# ❌ MAL - Expone datos de otros usuarios
def get_queryset(self):
    return Product.objects.all()

# ✅ BIEN
def get_queryset(self):
    return Product.objects.filter(user=self.request.user)
```

### **2. Asignar Usuario en Create**

```python
# ❌ MAL
def perform_create(self, serializer):
    serializer.save()

# ✅ BIEN
def perform_create(self, serializer):
    serializer.save(user=self.request.user)
```

### **3. Usar related_name para Relaciones Inversas**

```python
# ✅ BIEN
class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')

# Ahora en User:
>>> user.products.all()  # En lugar de Product.objects.filter(user=user)
```

### **4. Usar select_related para ForeignKey**

```python
# ❌ MAL - N+1 queries
products = Product.objects.all()

# ✅ BIEN - Una sola query
products = Product.objects.select_related('category', 'supplier')
```

### **5. Usar prefetch_related para ManyToMany o reverse FK**

```python
# ❌ MAL - N+1 queries
sales = Sale.objects.all()

# ✅ BIEN
sales = Sale.objects.prefetch_related('items', 'payments')
```

### **6. Timestamps Siempre**

```python
class MyModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)    # Inmutable
    updated_at = models.DateTimeField(auto_now=True)        # Auto-actualiza
```

### **7. Usar Transacciones para Operaciones Múltiples**

```python
from django.db import transaction

@transaction.atomic
def create_sale_with_items(sale_data, items):
    # Si falla algo, TODO se revierte
    sale = Sale.objects.create(**sale_data)
    for item_data in items:
        SaleItem.objects.create(sale=sale, **item_data)
    return sale
```

### **8. Usar Manager Customizado para Lógica Común**

```python
# api/models.py
class UserProductsManager(models.Manager):
    def for_user(self, user):
        return self.filter(user=user)

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    
    objects = UserProductsManager()

# Uso:
>>> Product.objects.for_user(request.user)
```

### **9. Validación en Serializer**

```python
class SaleSerializer(serializers.ModelSerializer):
    def validate_total(self, value):
        if value <= 0:
            raise serializers.ValidationError("Total debe ser mayor a 0")
        return value
    
    def validate(self, data):
        if data['status'] == 'completed' and not data.get('amount_paid'):
            raise serializers.ValidationError({
                'amount_paid': 'Es requerido para ventas completadas'
            })
        return data
```

### **10. Documentar con Docstrings**

```python
class ProductViewSet(viewsets.ModelViewSet):
    """
    API para gestionar productos.
    
    Methods:
        GET /api/products/ - Listar productos del usuario
        POST /api/products/ - Crear producto
        GET /api/products/{id}/ - Obtener producto
        PUT /api/products/{id}/ - Actualizar producto
        DELETE /api/products/{id}/ - Eliminar producto
    """
    
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Retorna productos del usuario autenticado."""
        return Product.objects.filter(user=self.request.user)
```

---

## Flujos Especiales de Negocio

### **Creación de Cliente con Usuario Automático**

**Contexto:** Cuando un administrador crea un cliente en el sistema, se debe crear automáticamente una cuenta de usuario para que el cliente pueda acceder.

**Implementación:**
- Ubicación: `accounts/views.py` - `ClientViewSet.perform_create()`
- Transacción atómica: Si falla la creación del usuario, se revierte la creación del cliente

**Credenciales de Nueva Cuenta:**
- **email**: Igual al email del cliente
- **username**: Igual al email del cliente
- **password**: `nurax123` (se recomienda cambiar en primer acceso)
- **role**: `cliente`
- **name**: Nombre del cliente

**Código:**
```python
from django.db import transaction

class ClientViewSet(viewsets.ModelViewSet):
    @transaction.atomic
    def perform_create(self, serializer):
        """Crea cliente y usuario asociado automáticamente."""
        client_data = serializer.validated_data
        
        # Crear usuario
        user = User.objects.create_user(
            email=client_data['email'],
            username=client_data['email'],
            password='nurax123',
            name=client_data['name'],
            role=User.Role.CLIENTE
        )
        
        # Guardar cliente con usuario
        serializer.save(user=user)
```

**Validación:**
- El email debe ser único en ambas tablas (User y Client)
- Se valida en el `ClientSerializer.validate_email()`
- Ver `accounts/tests.py` para casos de prueba

**Respuesta API:**
```json
{
  "id": 1,
  "name": "Juan García",
  "email": "juan@example.com",
  "company": "García Inc",
  "plan": "basico",
  "active": true,
  "user": {
    "id": 42,
    "email": "juan@example.com",
    "name": "Juan García",
    "role": "cliente",
    "is_active": true
  }
}
```

---

## Troubleshooting

### **⚠️ "InconsistentMigrationHistory" en Producción**

```
django.db.migrations.exceptions.InconsistentMigrationHistory: 
Migration admin.0001_initial is applied before its dependency accounts.0001_initial
```

**Solución completa:** Ver [MIGRATION_ORDER_FIX.md](./MIGRATION_ORDER_FIX.md)

**Quick fix:**
```bash
# La migración 0002_fix_admin_dependency.py en accounts/ corrige esto automaticamente
python manage.py migrate
```

**En Render:** El fix se aplicará en el próximo deploy.

---

### **"relation 'api_product' does not exist"**

```bash
# Migración no aplicada
docker exec nurax_api python manage.py migrate

# O resetear todo:
docker-compose down -v
docker-compose up --build
```

### **"User matching query does not exist"**

```bash
# Usuario no existe. Crear:
docker exec nurax_api python manage.py createsuperuser

# O en shell:
>>> from api.models import User
>>> User.objects.create_user(email='test@test.com', password='test123')
```

### **"Column 'X' does not exist"**

Modelo cambió pero BD no:
```bash
docker exec nurax_api python manage.py makemigrations
docker exec nurax_api python manage.py migrate
```

### **"Conflict writing to __pycache__"**

Problema de permisos en Docker:
```bash
docker-compose down
docker system prune -a
docker-compose up --build
```

### **Puerto 8000 ya está en uso**

```bash
# Encontrar qué usa puerto 8000
lsof -i :8000

# O cambiar puerto:
docker run -p 9000:8000 ...
```

### **Cambios en Python no se reflejan**

```bash
# Si usas Docker, el servidor se recarga automáticamente
# Si no, debes parar y reiniciar:
docker exec nurax_api python manage.py runserver 0.0.0.0:8000

# O local:
python manage.py runserver
```

### **Base de datos corrupida**

```bash
# Opción 1: Resetear volumen
docker-compose down -v
docker-compose up --build

# Opción 2: Backup y restore
docker exec nurax_db pg_dump -U nurax_user -d nurax_db > backup.sql
# Luego restore...
```

---

## Recursos Útiles

- **Django Docs**: https://docs.djangoproject.com/
- **DRF Docs**: https://www.django-rest-framework.org/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **This Project**: Ver `docs/AGENT.md`, `docs/API_ENDPOINTS.md`, `docs/DATABASE_SCHEMA.md`

---

**Última actualización:** Marzo 2026
