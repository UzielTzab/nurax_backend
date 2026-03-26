# Nurax Backend - AGENT GUIDE

Documentación técnica para desarrolladores y agentes de IA que trabajan en el backend de Nurax Inventario.

---

## 🎯 Principios de Desarrollo

1. **Domain-Driven Design (DDD)**: Cada app representa un "bounded context"
2. **Clean Code**: Type hints, docstrings Google-style, validación multi-capas
3. **Zero Prefixes**: DB tables sin prefijo "api_" (user, product, sale, etc)
4. **Test Coverage**: Mínimo 60 tests automáticos (actualmente 60/60 ✅)
5. **API Versionizing**: Todos los endpoints en /api/v1/*

---

## 🏗️ Arquitectura Actual (Post-Refactorización)

### Estructura de Aplicaciones

```
nurax_backend/
├── accounts/          # Usuarios, clientes, perfiles de tienda
├── products/          # Catálogo de productos
├── sales/             # Transacciones de venta
├── inventory/         # Kárdex y movimientos
├── expenses/          # Gastos y cortes de caja
├── api/               # Shared: exceptions, constants
└── nurax_backend/     # Config central
```

### Aplicaciones por Contexto

| App | Responsabilidad | Modelos | Tests |
|-----|-----------------|---------|-------|
| **accounts** | Auth, usuarios, clientes, perfiles | User, Client, StoreProfile, ActiveSessionCart | 7 |
| **products** | Catálogo, categorías, proveedores | Product, Category, Supplier | 11 |
| **sales** | Ventas, items, pagos | Sale, SaleItem, SalePayment | 14 |
| **inventory** | Kárdex, auditoría de stock | InventoryTransaction, InventoryMovement | 7 |
| **expenses** | Gastos, cortes de caja | Expense, CashShift | 13 |
| **api** | Shared, excepciones, constantes | - | 8 |

---

## 📋 Workflow para Nuevas Características

### 1. Planificación (SIEMPRE PRIMERO)
```markdown
Antes de implementar, estructura el plan:

**Objetivo**: [qué se busca lograr]
**Contexto**: [qué app/apps afecta]
**Cambios**:
  - Models: [qué modelos se crean/modifican]
  - Serializers: [qué serializers se actualizan]
  - Views: [qué endpoints se agregan]
  - Tests: [qué tests se agregan]
  - Migrations: [migrations necesarias]
**Riesgos**: [qué podría salir mal]
**Validación**: [cómo verificar que funciona]
```

### 2. Implementación
- Crear migrations inmediatamente
- Escribir tests primero (TDD)
- Implementar código
- Ejecutar tests locales
- Hacer git commit

### 3. Actualización de Documentación
- Actualizar ARCHITECTURE.md si hay cambios de modelos
- Actualizar API_ENDPOINTS.md si hay nuevos endpoints
- Actualizar este AGENT.md si hay cambios en workflow

---

## 🔧 Patrones & Standards

### Type Hints (SIEMPRE)
```python
# ✅ CORRECTO
def get_status(self) -> str:
    return 'in_stock'

class ProductManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        return ProductQuerySet(...)

# ❌ INCORRECTO
def get_status(self):  # Sin type hint
    return 'in_stock'
```

### Docstrings (Google Style)
```python
def calculate_total(items: List[SaleItem]) -> Decimal:
    """
    Calcula el total de una venta.
    
    Args:
        items: Lista de items de venta
    
    Returns:
        Total de la venta como Decimal
    
    Example:
        >>> calculate_total([item1, item2])
        Decimal('299.97')
    """
```

### Validación Multi-Capas
```
1. MODEL: validators= en Field
2. CUSTOM: MyValidator() en model Meta
3. SERIALIZER: validate_field() en Serializer
4. VIEW: Logic en ViewSet si es necesario
```

### Managers con QuerySet Optimization
```python
# Siempre incluir select_related/prefetch_related
class ProductQuerySet(models.QuerySet):
    def with_related(self) -> QuerySet:
        return self.select_related('user', 'category', 'supplier')
```

---

## 📍 Archivos Clave

### Excepciones
**Archivo**: `api/exceptions.py`
- `InsufficientStockError`
- `InvalidTransactionError`
- `UserNotAuthenticatedError`
- `PermissionDeniedError`
- `ResourceNotFoundError`
- `ValidationError`

**Patrón**: Heredar de `APIException`, establecer `status_code` y `default_detail`

### Constantes
**Archivo**: `api/constants.py`
- `SaleStatus`: COMPLETED, PENDING, CANCELLED, CREDIT, LAYAWAY
- `STOCK_LOW_THRESHOLD`: 10
- `STOCK_CRITICAL_THRESHOLD`: 5
- Pricing, pagination, categorías, etc

**Regla**: Nunca hardcodear valores, usar constantes!

### Settings
**Archivo**: `nurax_backend/settings.py`
- `INSTALLED_APPS`: Todas las 5 apps + api
- `AUTH_USER_MODEL`: 'accounts.User'
- `REST_FRAMEWORK`: Paginación, autenticación, filtrado
- `CLOUDINARY`: Configuración de almacenamiento

### URLs
**Archivo**: `nurax_backend/urls.py`
- Estructura: `/api/v1/{app}/{plural_resource}/`
- Ejemplos:
  - `/api/v1/accounts/users/`
  - `/api/v1/products/products/`
  - `/api/v1/sales/sales/`
  - `/api/v1/inventory/transactions/`
  - `/api/v1/expenses/expenses/`

---

## 🧪 Testing Strategy

### Archivo de Tests por App
- `accounts/tests.py`: 7 tests
- `products/tests.py`: 11 tests
- `sales/tests.py`: 14 tests
- `inventory/tests.py`: 7 tests
- `expenses/tests.py`: 13 tests
- `api/tests.py`: 8 tests (integration)
- **TOTAL**: 60 tests ✅

### Patrón: AAA (Arrange-Act-Assert)
```python
def test_product_status_low_stock(self):
    # Arrange: Preparar datos
    product = Product.objects.create(name='X', stock=8)
    
    # Act: Ejecutar
    status = product.status
    
    # Assert: Verificar
    self.assertEqual(status, 'low_stock')
```

### Ejecución
```bash
# Ejecutar todos los tests
docker-compose exec -T api python manage.py test accounts products sales inventory expenses api -v 0

# Ejecutar solo una app
docker-compose exec -T api python manage.py test accounts -v 2

# Con coverage (si está instalado)
docker-compose exec -T api pytest --cov=accounts --cov=products --cov-report=html
```

---

## 📦 Dependencias Clave

### Django & DRF
- `Django==6.0.2` - Framework web
- `djangorestframework==3.16.1` - API REST
- `rest_framework_simplejwt==5.3.2` - JWT auth
- `django-filter==24.1` - Filtrado de API
- `drf-spectacular==0.27.2` - OpenAPI docs
- `django-cors-headers==4.3.1` - CORS handling

### Database & ORM
- `psycopg2-binary==2.9.9` - PostgreSQL driver
- `dj-database-url==2.1.0` - Parsing DATABASE_URL

### Storage & Media
- `cloudinary==1.36.0` - Image hosting
- `django-cloudinary-storage==0.3.10` - Storage backend
- `Pillow==10.1.0` - Image manipulation

### Utilities
- `python-dotenv==1.0.0` - Environment variables
- `requests==2.31.0` - HTTP client
- `PyYAML==6.0.1` - YAML parsing
- `whitenoise==6.6.0` - Static files (prod)

### Development
- `pytest-django==4.7.0` - Testing framework
- `pytest-cov==4.1.0` - Coverage measurement

---

## 🐳 Docker & Environment

### docker-compose.yml
```yaml
services:
  db:
    image: postgres:15-alpine
    env_file: postgres.env      # DB credentials
    volumes: ['./nurax_pgdata:/var/lib/postgresql/data']
  
  api:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    env_file: postgres.env      # DB connection
    ports: ['8000:8000']
    volumes: ['${PWD}:/app']
```

### postgres.env
```bash
DB_NAME=nurax_db
DB_USER=nurax_user
DB_PASSWORD=secure_password
DB_HOST=db
DB_PORT=5432
DB_SSLMODE=disable
```

### .env (Cloudinary, Pusher)
```bash
CLOUDINARY_CLOUD_NAME=xxx
CLOUDINARY_API_KEY=xxx
CLOUDINARY_API_SECRET=xxx

PUSHER_APP_ID=xxx
PUSHER_KEY=xxx
PUSHER_SECRET=xxx
PUSHER_CLUSTER=xxx

DJANGO_SECRET_KEY=xxx
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

### Comandos Comunes
```bash
# Build imagen
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs api

# Ejecutar migrations
docker-compose exec -T api python manage.py migrate

# Acceder a shell Django
docker-compose exec api python manage.py shell

# Crear superuser
docker-compose exec api python manage.py createsuperuser

# Limpiar datos y recrear
docker-compose down -v && docker-compose up -d
```

---

## 🔄 Git Workflow

### Commits después de cambios
```bash
git add .
git commit -m "feat: [descripción breve]

- Cambio 1
- Cambio 2
- Tests agregados"
```

### Convención de mensajes
- `feat:` - Nueva característica
- `fix:` - Arreglo de bug
- `refactor:` - Cambio de código sin funcionalidad
- `docs:` - Cambios en documentación
- `test:` - Agregar/actualizar tests
- `chore:` - Cambios en dependencias, config

---

## 📚 Documentación Relacionada

- **ARCHITECTURE.md** - Diseño de bounded contexts, patrones, flujos de negocio
- **CLEAN_CODE_STANDARDS.md** - Estándares de código (type hints, validators, etc)
- **DATABASE_SCHEMA.md** - Diagrama ERD, relaciones, índices
- **API_ENDPOINTS.md** - Listado completo de endpoints
- **DEVELOPMENT_GUIDE.md** - Guía paso-a-paso

---

## ✅ Checklist para Code Review

Antes de hacer commit, verificar:

- [ ] Type hints en todas las funciones
- [ ] Docstrings en métodos públicos
- [ ] Tests escritos (AAA pattern)
- [ ] Managers con select_related/prefetch_related
- [ ] Validación multi-capas
- [ ] Excepciones centralizadas (no raise generic)
- [ ] Constantes en api/constants.py
- [ ] Migraciones creadas y correctas
- [ ] Documentación actualizada
- [ ] Tests pasen: `python manage.py test`
- [ ] Commit message descriptivo

---

## 🚨 Troubleshooting

### "Module not found" error
- Verificar que app está en `INSTALLED_APPS` en settings.py
- Ejecutar migrations: `python manage.py makemigrations && migrate`

### "No database table" error
- Crear migrations: `python manage.py makemigrations app_name`
- Aplicar: `python manage.py migrate`

### Import errors entre apps
- Usar `from typing import TYPE_CHECKING` para evitar circular imports
- Preferir strings para ForeignKey: `models.ForeignKey('other_app.Model')`

### Tests lentos
- Verificar que no hay queries sin `select_related`/`prefetch_related`
- Usar `--parallel` para Tests: `pytest --parallel 4`

---

## Última Actualización

**Fecha**: Marzo 26, 2026
**Versión**: 2.0 (Post-Refactorización DDD)
**Tests**: 60/60 ✅
**Coverage**: Modelos, Serializers, Views, Integración

# Construir imágenes y levantar contenedores
docker-compose up --build

# Levantar sin reconstruir
docker-compose up

# Detener contenedores
docker-compose down

# Detener y eliminar volúmenes (limpia BD)
docker-compose down -v
```

### **Dentro del Contenedor (docker exec)**

```bash
# LS Bash en el contenedor de API
docker exec -it nurax_api bash

# Conectar a PostgreSQL
docker exec -it nurax_db psql -U nurax_user -d nurax_db

# Ver logs en vivo
docker logs -f nurax_api
docker logs -f nurax_db
```

### **Comandos de Django**

```bash
# Ejecutar migraciones pendientes
docker exec nurax_api python manage.py migrate

# Crear nuevas migraciones
docker exec nurax_api python manage.py makemigrations

# Ver estado de migraciones
docker exec nurax_api python manage.py showmigrations

# Crear superusuario (admin)
docker exec -it nurax_api python manage.py createsuperuser

# Script de inicialización de BD
docker exec nurax_api python init_db.py

# Script de datos de prueba
docker exec nurax_api python populate_db.py

# Shell interactiva de Django (REPL)
docker exec -it nurax_api python manage.py shell

# Collectstatic (para producción)
docker exec nurax_api python manage.py collectstatic --noinput
```

### **Desarrollo Local (sin Docker)**

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Inicializar datos
python init_db.py

# Iniciar servidor
python manage.py runserver
```

---

## Puertos Principales

| Servicio | Puerto | URL | Notas |
|----------|--------|-----|-------|
| **API Django** | 8000 | `http://localhost:8000` | Servidor REST |
| **Admin Django** | 8000 | `http://localhost:8000/admin` | Panel administrativo |
| **PostgreSQL** | 5432 | `localhost:5432` | Base de datos |

---

## Environment Configuration

### **Variables de Entorno Críticas**

Crear `.env` en la raíz del proyecto:

```env
# BASES DE DATOS
DB_NAME=nurax_db
DB_USER=nurax_user
DB_PASSWORD=nurax_password
DB_HOST=db                    # "db" si usa Docker, "localhost" si es local
DB_PORT=5432
DB_SSLMODE=disable

# DJANGO
DEBUG=True                     # SIEMPRE False en producción
SECRET_KEY=dev-key-change-in-prod-insecure

# CLOUDINARY (para imágenes/archivos)
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret

# PUSHER (notificaciones en tiempo real)
PUSHER_APP_ID=tu_app_id
PUSHER_KEY=tu_key
PUSHER_SECRET=tu_secret
PUSHER_CLUSTER=tu_cluster
```

### **Cómo Configurar**

1. Copia valores a `.env` (NO versionarlo en git)
2. Docker Compose lee automáticamente variables del `.env`
3. Settings.py lee con `os.getenv('VAR_NAME', 'DEFAULT')`

---

## Patrones Clave del Proyecto

### **1. Autenticación y Autorización**

- **Sistema**: JWT (JSON Web Tokens) con `SimpleJWT`
- **Endpoints**:
  - `POST /api/token/` - Obtener tokens (email + password)
  - `POST /api/token/refresh/` - Refrescar access token
- **Roles**: ADMIN, CLIENTE (definidos en `User.Role`)
- **Permisos**: Django REST Framework permissions mixins en ViewSets
- **User Field**: Se autentica por EMAIL (no username)

```python
# Ejemplo en views
class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Product.objects.all()
```

### **2. Estructura de BD y Relaciones**

**Jerarquía de datos:**
```
User (autenticación)
  ├── StoreProfile (config del negocio)
  ├── ActiveSessionCart (carrito actual)
  ├── Products (inventario del usuario)
  │   ├── Category
  │   └── Supplier
  ├── Sales (transacciones realizadas)
  │   └── SaleItems
  │   └── SalePayments (abonos)
  └── CashShifts (cortes de caja)
      └── InventoryMovements
      └── Expenses
```

**Todos los modelos de "datos" tienen `user = ForeignKey(User)`** para aislar datos por usuario.

### **3. Inventario - Kárdex y Movimientos**

- **InventoryTransaction**: Registro histórico de cambios (IN/OUT/ADJUSTMENT/WASTE)
- **InventoryMovement**: Detalles con costo unitario, vinculado a CashShift
- **Product.stock**: Se actualiza automáticamente según estos movimientos
- **Product.status**: Propiedad que calcula estado (in_stock/low_stock/out_of_stock)

### **4. Ventas - Estados y Flujos**

Estados posibles de `Sale.Status`:
- `completed` - Venta pagada completa
- `pending` - Venta pendiente de pago
- `cancelled` - Venta cancelada
- `credit` - Venta a crédito
- `layaway` - Venta con apartado

Relación con pagos:
```python
# Ventas a crédito/apartado tienen "payments" relacionados
sale.payments.all()  # Se calculan abonos automáticamente
sale.balance_due    # Propiedad que calcula saldo
```

### **5. Snapshot de Datos**

En `SaleItem` hay un campo `product_name` que guarda el nombre del producto **en el momento de la venta**, por si el producto es eliminado después.

```python
class SaleItem(models.Model):
    product_name = models.CharField(max_length=250)  # snapshot
```

### **6. Almacenamiento de Imágenes**

- **NO se guardan archivos locales** en el servidor
- **Cloudinary almacena** imágenes y devuelve URL
- En BD solo se guarda: `image_url`, `avatar_url`, `logo_url` (campos URLField)
- Referencia: `django-cloudinary-storage`

### **7. Configuración por Tienda**

`StoreProfile` guarda config personalizada:
- Nombre de tienda
- Símbolo de moneda
- Dirección, teléfono
- Logo
- Nombre de empresa (para facturación)

Cada usuario tiene UNO (OneToOneField)

### **8. Corte de Caja (Cash Shift)**

Flujo:
1. Usuario abre turno con dinero inicial (`starting_cash`)
2. Sistema registra movimientos de inventario y gastos
3. Al cerrar, se calcula diferencia entre esperado y actual
4. Útil para auditoría y reconciliación

```python
class CashShift:
    expected_cash = sum(sales) - sum(gastos)
    actual_cash = dinero_real_en_caja
    difference = actual_cash - expected_cash
```

---

## Test Credentials

### **Usuarios de Prueba** (se crean con `populate_db.py`)

| Email | Password | Rol | Propósito |
|-------|----------|-----|-----------|
| admin@nurax.local | admin123 | ADMIN | Administrador del sistema |
| store1@nurax.local | pass123 | CLIENTE | Tienda 1 prueba |
| store2@nurax.local | pass123 | CLIENTE | Tienda 2 prueba |

### **Cómo Obtener Tokens JWT**

```bash
# Usando curl
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@nurax.local",
    "password": "admin123"
  }'

# Respuesta:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### **Usar Token en Requests**

```bash
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

## Domain Context (Conceptos de Negocio)

### **Entidades Principales**

1. **User** - Persona que usa el sistema (vendedor, gerente, admin)
2. **StoreProfile** - La "tienda" de un usuario (datos del negocio)
3. **Product** - Artículo vendido
4. **Sale** - Transacción comercial (lo que se vende)
5. **Inventory** - Stock de productos
6. **CashShift** - Turno de caja (para auditoría)

### **Flujos de Negocio**

#### **Flujo de Venta**
```
1. Agregar productos al carrito (ActiveSessionCart)
2. Crear Sale con status
3. Crear SaleItems para cada producto
4. Si es crédito/apartado:
   - Mantener Sale en estado CREDIT/LAYAWAY
   - Crear SalePayment para cada abono
5. Cerrar Sale cuando se pague completamente
```

#### **Flujo de Inventario**
```
1. Reabastecimiento desde proveedor
   └─ Crear InventoryMovement (type=restock)
   └─ Aumentar Product.stock
2. Venta de producto
   └─ Crear InventoryTransaction (type=out)
   └─ Decrementar Product.stock
3. Ajustes (merma, robo, error)
   └─ Crear InventoryTransaction (type=adjustment)
```

#### **Flujo de Gastos**
```
1. Registrar gasto (servicios, nómina, etc)
   └─ Crear Expense con categoría
2. Vincular al CashShift actual
3. Opcionalmente vincular a Supplier
```

#### **Flujo de Corte de Caja**
```
1. Abrir turno: crear CashShift con dinero inicial
2. Hacer transacciones (ventas, gastos)
3. Cerrar turno: total esperado vs real
4. Genera reporte para auditoría
```

### **Métricas Clave**

- **balance_due**: Saldo pendiente de una venta
- **subtotal (SaleItem)**: quantity × unit_price
- **status (Product)**: in_stock / low_stock / out_of_stock
- **difference (CashShift)**: actual_cash - expected_cash

---

## Key Patterns & Convenciones

### **1. Convención de Nombres**

| Tipo | Patrón | Ejemplo |
|------|--------|---------|
| **Modelos** | PascalCase | `Product`, `SaleItem`, `CashShift` |
| **Campos** | snake_case | `product_name`, `unit_price`, `created_at` |
| **Métodos** | snake_case | `get_stock_value()`, `calculate_balance()` |
| **Propiedades** | @property | `@property def status(self):` |
| **Enums (Choice)** | UPPER_SNAKE_CASE | `Status.COMPLETED`, `Role.ADMIN` |

### **2. Timestamps Estándar**

Todos los modelos tienen:
```python
created_at = models.DateTimeField(auto_now_add=True)  # Inmutable
updated_at = models.DateTimeField(auto_now=True)      # Auto-actualiza
```

### **3. Soft Deletes (Cascadas)**

- Usar `on_delete=models.CASCADE` cuando registros dependen
- Usar `on_delete=models.SET_NULL` para datos históricos sin referencia fuerte
- Ej: Product to Sale - SET_NULL (mantiene ventas aunque se borre producto)

### **4. Snapshots en Transacciones**

En `SaleItem` se guarda `product_name` para preservar histórico si el producto es borrado:
```python
class SaleItem:
    product = ForeignKey(Product, on_delete=models.SET_NULL)
    product_name = CharField()  # snapshot del nombre
```

### **5. Estructura de Carpetas en `api/`**

```
api/
├── models.py          # TODAS las clases Model
├── views.py           # TODOS los ViewSets
├── serializers.py     # TODOS los Serializers
├── urls.py            # Rutas (usa SimpleRouter)
├── admin.py           # Registros para Django Admin
├── pagination.py      # Clases de paginación custom
└── migrations/        # Historial de cambios
```

No se usan sub-carpetas (ej: `api/models/`, `api/views/`) - todo plano en archivos principales.

### **6. ViewSets y Permisos**

```python
from rest_framework import viewsets, permissions

class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        # IMPORTANTE: Filtrar por usuario actual
        return Product.objects.filter(user=self.request.user)
```

**SIEMPRE filtrar por `self.request.user`** para aislar datos.

### **7. Serializers con Nested**

Para respuestas complejas:
```python
class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    payments = SalePaymentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Sale
        fields = ['id', 'transaction_id', 'items', 'payments', ...]
```

### **8. Testing**

- Archivo central: `api/tests.py`
- Usar `TestCase` de Django para tests con BD
- Tests de API usan client DRF: `client.post('/api/...')`

---

## Archivos Importantes para IA

| Archivo | Propósito | Prioridad |
|---------|-----------|-----------|
| `api/models.py` | Definición completa de entidades | 🔴 CRÍTICA |
| `api/views.py` | Lógica de endpoints | 🔴 CRÍTICA |
| `api/serializers.py` | Transformación de datos | 🟡 ALTA |
| `api/urls.py` | Rutas de API | 🟡 ALTA |
| `nurax_backend/settings.py` | Configuración del proyecto | 🟡 ALTA |
| `requirements.txt` | Dependencias | 🟢 NORMAL |
| `.env.example` | Template de variables | 🔴 CRÍTICA |
| `docker-compose.yml` | Configuración de servicios | 🟡 ALTA |
| `Dockerfile` | Imagen de aplicación | 🟡 ALTA |

---

## Notas Especiales / Quirks

1. **User se autentica por EMAIL, no username**
   - `USERNAME_FIELD = 'email'` en modelo User
   - JWT endpoints esperan `email` + `password`

2. **Todos los datos están aislados por usuario**
   - Cada Product, Sale, etc. tiene `user = ForeignKey(User)`
   - Más seguro y escalable para multi-tenant

3. **Sin borrado físico (soft deletes via CASCADE/SET_NULL)**
   - No hay campo `deleted_at`
   - Usar CASCADE para datos relacionados, SET_NULL para histórico

4. **Imágenes en Cloudinary**
   - Nunca se guardan localmente
   - Solo URLs en campos `*_url`
   - Configuración en settings via django-cloudinary-storage

5. **Paginación por defecto: 10 items**
   - Definida en `api/pagination.py`
   - Modificable por query param `?page_size=50`

6. **Filtrado habilitado globalmente**
   - Usar en ViewSet: `filterset_fields = ['category', 'status']`
   - Ej: `/api/products/?category=Electrónica&status=in_stock`

7. **Documentación automática OpenAPI**
   - Usar `drf-spectacular`
   - Disponible en `/api/schema/` y `/api/docs/`

8. **Cors habilitado para cualquier origen** ⚠️
   - Revisar `CORS_ALLOWED_ORIGINS` en settings.py para producción
   - Restringir a dominios específicos

9. **CashShift es crucial para auditoría**
   - Siempre registra movimientos bajo un turno
   - Facilita reconciliación al cierre del día

10. **StoreProfile es la "configuración del negocio"**
    - Cada usuario tiene UNO (OneToOneField)
    - Datos como nombre tienda, símbolo moneda, logo

---

## Convenciones de Código

| Aspecto | Estándar | Herramienta |
|---------|----------|------------|
| **Linting** | PEP 8 (Django) | `flake8` (opcional) |
| **Formatting** | Black | Black (opcional) |
| **Type Checking** | None (Python dinámico) | - |
| **Testing** | unittest / pytest | Django TestCase |
| **Migrations** | Django migrations | `makemigrations` |

---

## Checklist para Nuevas Features

Cuando agregues una feature nueva:

- [ ] Crear modelo en `api/models.py`
- [ ] Crear serializer en `api/serializers.py`
- [ ] Crear ViewSet en `api/views.py`
- [ ] Registrar ruta en `api/urls.py`
- [ ] Registrar en `api/admin.py` para Django Admin
- [ ] Ejecutar `python manage.py makemigrations`
- [ ] Ejecutar `python manage.py migrate`
- [ ] Añadir tests en `api/tests.py`
- [ ] Documentar en `docs/API_ENDPOINTS.md`
- [ ] Verificar filtros/permisos por usuario

---

## Referencias Rápidas

### **Comandos Frecuentes**

```bash
# Dentro del contenedor
docker exec nurax_api python manage.py makemigrations
docker exec nurax_api python manage.py migrate
docker exec nurax_api python manage.py createsuperuser
docker exec nurax_api python manage.py shell

# Ver BD
docker exec -it nurax_db psql -U nurax_user -d nurax_db
```

### **Rutas Admin**

- Admin panel: `http://localhost:8000/admin`
- API docs: `http://localhost:8000/api/docs/`
- Schema OpenAPI: `http://localhost:8000/api/schema/`

### **Obtener Help**

```bash
docker exec nurax_api python manage.py help migrate
docker exec nurax_api python manage.py help makemigrations
```

---

**Última actualización:** Marzo 2026  
**Versión Backend:** 1.0.0  
**Python:** 3.12  
**Django:** 6.0.2  
**PostgreSQL:** 15
