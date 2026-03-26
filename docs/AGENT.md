# Nurax Backend - AGENT.md

Documentación técnica del backend de Nurax Inventario. Este archivo contiene información crítica para IAs/Copilot que necesiten trabajar en este proyecto.

---

## Eres un ingeniero de software, que escribe código limpio y se prevee de errores antes de que ocurran, aplica las mejores práctcas y modelos/patrones más eficientes a nivel de rendimiento computacional. No escribes código de borrador, escribes código preparado para producción.

## Recuerda que cada vez que vaya a realizar un cambio, actualices los archivos y su contenido de la carpeta docs, ya que es importante que estén actualizados.

## Siempre que inicies un nuevo cambio debes realizar un planeaci'on que posteriormente te debo aprobar para que depués lo implmentes. 

## Project Overview

**Nombre:** Nurax Backend (API + Base de Datos)  
**Descripción:** API REST para gestión de inventario, ventas, gastos y cortes de caja. Sistema POS (Point of Sale) para tiendas pequeñas y medianas.  
**Tipo:** Proyecto único (no monorepo)  
**Stack principal:** Django 6.0.2 + Django REST Framework 3.16.1 + PostgreSQL 15 + Docker  
**Propósito:** Proporcionar backend robusto para aplicación de inventario con gestión de:
- Productos y categorías
- Ventas y pagos (crédito, apartado, venta normal)
- Inventario (kárdex, movimientos, ajustes)
- Gastos y cortes de caja
- Perfiles de tienda (configuración por usuario)

---

## Estructura del Repositorio

```
nurax_backend/
├── manage.py                    # Script de gestión de Django
├── requirements.txt             # Dependencias Python
├── Dockerfile                   # Configuración Docker
├── docker-compose.yml           # Orquestación de servicios
├── init_db.py                   # Script inicialización de BD
├── populate_db.py               # Script de datos de prueba
├── db.sqlite3                   # BD local (no usar en prod)
├── README.md                    # Documentación de uso
│
├── docs/                        # 📁 Documentación para IAs
│   ├── AGENT.md                 # Este archivo
│   ├── DATABASE_SCHEMA.md       # Diagrama ERD y relaciones
│   ├── API_ENDPOINTS.md         # Listado de endpoints
│   └── DEVELOPMENT_GUIDE.md     # Guía para desarrollo
│
├── api/                         # 🔷 Aplicación principal Django
│   ├── models.py                # Definición de modelos de BD
│   ├── views.py                 # ViewSets y vistas DRF
│   ├── serializers.py          # Serialización de datos
│   ├── urls.py                 # Rutas de la API
│   ├── pagination.py           # Configuración de paginación
│   ├── admin.py                # Panel de administración
│   ├── apps.py                 # Configuración de app
│   ├── tests.py                # Tests unitarios
│   └── migrations/             # Historial de cambios BD
│       ├── 0001_initial.py
│       ├── 0002_alter_user_email.py
│       ├── ...
│       └── 0013_storeprofile_company_name_and_more.py
│
└── nurax_backend/              # 🔧 Configuración del proyecto
    ├── settings.py             # Configuración principal
    ├── urls.py                 # URLs raíz
    ├── asgi.py                 # ASGI para servidor async
    └── wsgi.py                 # WSGI para producción
```

---

## Componentes/Módulos Principales

### **1. API Application (`api/`)**

| Aspecto | Detalle |
|---------|---------|
| **Directorio** | `api/` |
| **Purpose** | Núcleo de la API REST. Define modelos, vistas, serializadores y rutas |
| **Tecnologías** | Django 6.0.2, Django REST Framework 3.16.1, django-filter, drf-spectacular |
| **Archivos clave** | `models.py`, `views.py`, `serializers.py`, `urls.py`, `pagination.py` |

#### Modelos principales (ver DATABASE_SCHEMA.md para diagrama):
- **User** - usuario del sistema (extiende AbstractUser)
- **Client** - empresas que contratan el servicio
- **Product** - productos en inventario
- **Category** - categorización de productos
- **Supplier** - proveedores
- **Sale** - transacciones de venta
- **SaleItem** - ítems dentro de una venta
- **SalePayment** - abonos a ventas en crédito/apartado
- **InventoryTransaction** - movimientos de inventario (kárdex)
- **InventoryMovement** - detalles de movimientos
- **Expense** - gastos/egresos
- **CashShift** - cortes de caja
- **StoreProfile** - configuración por tienda
- **ActiveSessionCart** - carrito de sesión activa

### **2. Settings y Configuración (`nurax_backend/`)**

| Aspecto | Detalle |
|---------|---------|
| **Directorio** | `nurax_backend/` |
| **Purpose** | Configuración central del proyecto Django |
| **Archivos clave** | `settings.py`, `urls.py` |

#### En `settings.py`:
- **INSTALLED_APPS**: incluye `api`, `rest_framework`, `corsheaders`, `cloudinary_storage`, etc.
- **Autenticación**: JWT (SimpleJWT) con `TokenObtainPairView` y `TokenRefreshView`
- **Paginación**: `PageNumberPagination` (defecto: 10 items/página)
- **Filtrado**: `django-filter` habilitado
- **CORS**: Hace que cualquier origen pueda acceder (revisar en producción)
- **Base de datos**: PostgreSQL configurada por variables de entorno

---

## Key Technologies

### **Backend**
- **Framework**: Django 6.0.2
- **API**: Django REST Framework 3.16.1
- **ORM**: Django ORM (modelos)
- **BD**: PostgreSQL 15 (producción), SQLite3 (dev local)
- **Autenticación**: JWT (djangorestframework_simplejwt)
- **Almacenamiento**: Cloudinary (imágenes/archivos)
- **Notificaciones**: Pusher (tiempo real)

### **Infrastructure**
- **Containerización**: Docker + Docker Compose
- **Servidor**: Python 3.12
- **Librerías clave**:
  - `django-cors-headers` - manejo de CORS
  - `django-cloudinary-storage` - integración con Cloudinary
  - `django-filter` - filtrado avanzado en APIs
  - `drf-spectacular` - documentación automática OpenAPI
  - `psycopg2-binary` - driver PostgreSQL
  - `python-dotenv` - variables de entorno

### **Utilidades**
- `Pillow` - procesamiento de imágenes
- `requests` - HTTP client
- `PyYAML` - parsing YAML (para especificaciones)
- `whitenoise` - servicio de archivos estáticos en prod

---

## Cómo Ejecutar / Desarrollar

### **Build y Levantamiento (con Docker)**

```bash
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
