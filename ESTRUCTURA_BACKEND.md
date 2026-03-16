# Estructura y documentación del backend — Nurax

## 1. Estructura de carpetas (diagrama)

```
nurax_backend/
├── api/                    # App Django: modelos, vistas, serializers, rutas y lógica de negocio
├── nurax_backend/          # Proyecto Django: settings, URLs raíz, WSGI/ASGI
├── api/migrations/         # Migraciones de base de datos (Django)
├── venv/                   # Entorno virtual Python (no versionar)
├── manage.py               # CLI de Django
├── requirements.txt        # Dependencias Python
├── docker-compose.yml      # Orquestación de servicios (DB + app)
├── Dockerfile              # Imagen para ejecutar la app
├── init_db.py              # Script de inicialización de BD
├── populate_db.py          # Script para datos de prueba
├── db.sqlite3              # BD SQLite (desarrollo local, opcional)
├── .env                    # Variables de entorno (no versionar)
├── .gitignore
└── .dockerignore
```

Solo es necesario conocer: **api** (lógica de la API), **nurax_backend** (configuración del proyecto) y los archivos raíz de despliegue/ejecución.

---

## 2. Desglose de carpetas principales

### Carpeta `nurax_backend/`

Es el **proyecto Django** (contenedor del sitio). Define configuración global y rutas raíz.

| Archivo      | Rol |
|-------------|-----|
| `settings.py` | Configuración: BD, apps instaladas, REST Framework, JWT, CORS, Cloudinary, Pusher, etc. |
| `urls.py`     | URLs raíz: `admin/`, `api/` (incluye `api.urls`), `api/auth/login`, `api/auth/refresh`, `api/schema`, `api/docs` (Swagger). |
| `wsgi.py`     | Punto de entrada WSGI para servidores (gunicorn, etc.). |
| `asgi.py`     | Punto de entrada ASGI para servidores asíncronos. |

---

### Carpeta `api/`

Es la **aplicación Django** que contiene toda la lógica de la API REST.

| Contenido conceptual | Descripción |
|----------------------|-------------|
| **Modelos**          | Entidades de negocio: User, Client, Category, Supplier, Product, Sale, SaleItem, SalePayment, InventoryTransaction, **InventoryMovement**, Expense, CashShift, StoreProfile, ActiveSessionCart. |
| **Vistas (ViewSets)**| Endpoints CRUD y acciones custom por recurso; permisos por rol (admin/cliente); integración con Pusher para tiempo real. |
| **Serializers**      | Validación y serialización entrada/salida; subida de archivos a Cloudinary (avatar, producto, logo, comprobantes). |
| **URLs**             | Router DRF que registra cada ViewSet bajo prefijo `/api/`. |
| **Paginación**       | Clases de paginación reutilizables (productos, ventas). |
| **Migrations**       | Historial de cambios del esquema de la base de datos. |

---

## 3. Contenido de cada archivo dentro de `api/`

| Archivo           | Contenido |
|-------------------|-----------|
| **models.py**     | Modelos Django: User (AbstractUser), Client, Category, Supplier, Product, Sale, SaleItem, SalePayment, InventoryTransaction, **InventoryMovement**, Expense, CashShift, StoreProfile, ActiveSessionCart. Incluye choices (Role, Plan, Status, MovementType, etc.), propiedades calculadas (`status`, `balance_due`, `subtotal`) y relaciones FK/OneToOne. |
| **views.py**      | ViewSets (ProductViewSet, SaleViewSet, …). Permisos (IsAdmin, IsAuthenticated), FilterSet para productos, acciones custom (low_stock, scan, sync_cart, **register_restock**, cancel, open/close shift, etc.) e integración con Pusher. El endpoint `/api/store/onboarding-complete/` marca el flag `is_first_setup_completed` en `StoreProfile`. |
| **serializers.py**| Serializers para todos los modelos; **InventoryMovementSerializer**, **RestockSerializer** (reabastecimiento); ProductSerializer/UserSerializer/StoreProfileSerializer/ExpenseSerializer con subida a Cloudinary; `UserSerializer` ahora incluye el `store_profile` embebido (con `is_first_setup_completed`) para que el frontend sepa si mostrar el wizard; SaleSerializer con creación de SaleItem y movimientos de inventario; ChangePasswordSerializer. |
| **urls.py**       | DefaultRouter que registra: products, sales, clients, categories, suppliers, users, store, expenses, shifts, inventory-tx, payments. |
| **pagination.py**| ProductPagination y SalesPagination (page_size, page_size_query_param, max_page_size). |
| **admin.py**      | Vacío (solo comentario “Register your models here”). |
| **apps.py**       | ApiConfig: nombre de la app `'api'`. |
| **tests.py**      | Vacío (solo comentario “Create your tests here”). |
| **migrations/**   | Archivos de migración de Django (0001_initial hasta 0012_expense_cash_shift_expense_supplier_and_more) que definen y modifican tablas. |

**Funcionalidad añadida — Reabastecimiento:**  
- **POST /api/products/register-restock/** (ProductViewSet): registra una entrada de inventario (reabastecimiento) con costo unitario. Crea un `Expense` de categoría `inventario`, un `InventoryMovement` de tipo `restock`, actualiza el stock del producto y emite evento Pusher `INVENTORY_UPDATED`. Requiere caja abierta. Body: `product_id`, `quantity`, `unit_cost`; opcionales: `supplier_id`, `expense_category`, `notes`. Serializer: `RestockSerializer`.

---

## 4. Modelos en `models.py` — tablas y resumen de campos

### User (extiende AbstractUser)

| Campo        | Tipo        | Resumen |
|-------------|-------------|---------|
| role        | CharField   | Rol: admin o cliente. |
| name        | CharField   | Nombre del usuario. |
| email       | EmailField  | Email único; usado como USERNAME_FIELD. |
| avatar_url  | URLField    | URL de la foto de perfil (Cloudinary). |

---

### Client

| Campo       | Tipo        | Resumen |
|------------|-------------|---------|
| user       | OneToOne(User) | Usuario asociado (opcional). |
| name       | CharField   | Nombre del cliente. |
| email      | EmailField  | Email único. |
| company    | CharField   | Empresa. |
| plan       | CharField   | Plan: basico o pro. |
| active     | BooleanField| Si está activo. |
| created_at | DateTimeField | Fecha de creación. |
| avatar_color | CharField | Color del avatar (hex). |

---

### Category

| Campo | Tipo      | Resumen |
|-------|-----------|---------|
| name  | CharField | Nombre único de la categoría. |

---

### Supplier

| Campo      | Tipo        | Resumen |
|-----------|-------------|---------|
| user      | FK(User)    | Usuario dueño (opcional). |
| name      | CharField   | Nombre. |
| email     | EmailField  | Email. |
| phone     | CharField   | Teléfono. |
| company   | CharField   | Empresa. |
| created_at| DateTimeField | Fecha de creación. |

---

### Product

| Campo     | Tipo        | Resumen |
|----------|-------------|---------|
| user     | FK(User)    | Usuario dueño (opcional). |
| name     | CharField   | Nombre del producto. |
| category | FK(Category)| Categoría. |
| supplier | FK(Supplier)| Proveedor (opcional). |
| sku      | CharField   | Código SKU. |
| stock    | PositiveInteger | Cantidad en inventario. |
| price    | DecimalField| Precio. |
| image_url| URLField    | URL de imagen (Cloudinary). |
| created_at / updated_at | DateTimeField | Auditoría. |
| *status* | property    | Calculado: in_stock / low_stock / out_of_stock según stock. |

---

### Sale

| Campo           | Tipo        | Resumen |
|----------------|-------------|---------|
| transaction_id | CharField   | ID único de la transacción. |
| user           | FK(User)    | Usuario que registra la venta. |
| status         | CharField   | completed, pending, cancelled, credit, layaway. |
| total          | DecimalField| Total de la venta. |
| created_at     | DateTimeField | Fecha. |
| customer_name  | CharField   | Nombre del cliente (opcional). |
| customer_phone | CharField   | Teléfono (opcional). |
| amount_paid    | DecimalField| Monto abonado (crédito/apartado). |
| *balance_due*  | property    | Saldo pendiente (total − pagos). |

---

### SaleItem

| Campo        | Tipo        | Resumen |
|-------------|-------------|---------|
| sale        | FK(Sale)    | Venta a la que pertenece. |
| product     | FK(Product) | Producto (puede ser null si se borra). |
| product_name| CharField   | Snapshot del nombre al momento de la venta. |
| quantity    | PositiveInteger | Cantidad. |
| unit_price  | DecimalField| Precio unitario. |
| *subtotal*  | property    | quantity × unit_price. |

---

### SalePayment

| Campo     | Tipo        | Resumen |
|----------|-------------|---------|
| sale      | FK(Sale)    | Venta. |
| amount    | DecimalField| Monto del abono. |
| created_at| DateTimeField | Fecha. |
| user      | FK(User)    | Usuario que registra. |

---

### InventoryTransaction (Kárdex)

| Campo            | Tipo        | Resumen |
|------------------|-------------|---------|
| product          | FK(Product) | Producto. |
| transaction_type | CharField   | in, out, adjustment, waste. |
| quantity         | PositiveInteger | Cantidad. |
| reason           | CharField   | Motivo (opcional). |
| user             | FK(User)    | Usuario. |
| created_at       | DateTimeField | Fecha. |

---

### InventoryMovement (movimientos con costo / reabastecimiento)

Registra entradas de inventario con costo unitario, vinculadas a un gasto y al turno de caja.

| Campo         | Tipo        | Resumen |
|---------------|-------------|---------|
| product       | FK(Product) | Producto. |
| movement_type | CharField   | sale, restock, adjust. |
| quantity      | PositiveInteger | Cantidad. |
| unit_cost     | DecimalField| Costo unitario (opcional). |
| total_cost    | DecimalField| Costo total (opcional). |
| expense       | FK(Expense) | Gasto asociado (reabastecimiento). |
| cash_shift    | FK(CashShift) | Turno de caja. |
| user          | FK(User)    | Usuario. |
| created_at    | DateTimeField | Fecha. |
| notes         | TextField   | Notas (opcional). |

---

### Expense

| Campo       | Tipo        | Resumen |
|------------|-------------|---------|
| amount     | DecimalField| Monto del gasto. |
| category   | CharField   | servicios, nomina, proveedores, **inventario**, varios. |
| description| CharField   | Descripción. |
| receipt_url| URLField    | URL del comprobante (Cloudinary). |
| user       | FK(User)    | Usuario. |
| supplier   | FK(Supplier)| Proveedor asociado (opcional). |
| cash_shift | FK(CashShift)| Turno de caja (opcional). |
| date       | DateField   | Fecha del gasto. |

---

### CashShift (Corte de caja / turnos)

| Campo         | Tipo        | Resumen |
|--------------|-------------|---------|
| user         | FK(User)    | Usuario del turno. |
| opened_at    | DateTimeField | Apertura. |
| closed_at    | DateTimeField | Cierre (null si abierto). |
| starting_cash| DecimalField| Efectivo inicial. |
| expected_cash| DecimalField| Efectivo esperado al cierre. |
| actual_cash  | DecimalField| Efectivo contado. |
| difference   | DecimalField| Diferencia (actual − expected). |

---

### StoreProfile (Configuración del negocio)

| Campo          | Tipo        | Resumen |
|----------------|-------------|---------|
| user           | OneToOne(User) | Usuario dueño. |
| store_name     | CharField   | Nombre de la tienda. |
| currency_symbol| CharField   | Símbolo de moneda. |
| address        | CharField   | Dirección. |
| phone          | CharField   | Teléfono. |
| ticket_message | TextField   | Mensaje en ticket. |
| logo_url       | URLField    | Logo (Cloudinary). |
| company_name   | CharField   | Nombre comercial usado en el wizard de onboarding. |
| ticket_name    | CharField   | Etiqueta del ticket (ej. “Recibo”, “Nota de venta”), configurada en el onboarding. |
| is_first_setup_completed | BooleanField | Indica si el usuario ya completó el wizard inicial. |
| updated_at     | DateTimeField | Última actualización. |

---

### ActiveSessionCart (Carrito activo por usuario)

| Campo     | Tipo     | Resumen |
|----------|----------|---------|
| user     | OneToOne(User) | Usuario. |
| cart_data| JSONField| Lista con el estado del carrito. |
| updated_at | DateTimeField | Última actualización. |

---

## 5. Patrón de arquitectura y estilo de código

### Patrón de arquitectura

- **Django + Django REST Framework (DRF)** con enfoque **resource-based (REST)**.
- **Estructura por capas implícita**:
  - **URLs** → **ViewSets** (controladores) → **Serializers** (validación/serialización) → **Models** (persistencia).
- **Autenticación**: JWT (Simple JWT) con login/refresh; permisos por rol (admin ve todo, cliente solo sus datos).
- **Tiempo real**: Pusher (canales por usuario `pos-user-{id}`) para inventario, ventas, carrito y escaneo.
- **Almacenamiento de archivos**: URLs en BD; archivos subidos a **Cloudinary** (avatars, productos, logos, comprobantes).
- No hay capa de “servicios” explícita: lógica de negocio repartida entre serializers (creación de ventas, stock, kárdex) y vistas (cancelación, turnos, ajustes).

### Estilo de código observado

- **PEP 8**: indentación 4 espacios, nombres en snake_case para funciones/variables, PascalCase para clases.
- **Docstrings** en español en acciones y métodos relevantes (p. ej. `scan`, `update_profile`, `change_password`).
- **ViewSets** con atributos de clase: `queryset`, `serializer_class`, `filter_backends`, `permission_classes`, `ordering`.
- **Permisos**: clases propias (`IsAdmin`) y `permissions.IsAuthenticated`; `get_permissions()` dinámico en UserViewSet.
- **Filtros**: django-filter con FilterSet personalizado (ProductFilterSet) y filtros por query params.
- **Respuestas**: `Response()` de DRF con códigos HTTP explícitos (`status=status.HTTP_400_BAD_REQUEST`, etc.).
- **Imports**: agrupados (stdlib, terceros, locales); en views se usa `from .models import ...` y `from .serializers import *`.

---

## 6. Reglas de codificación limpia (editables)

Estas reglas se pueden copiar a un archivo de convenciones (p. ej. `CONVENTIONES.md` o `.cursor/rules`) y ajustar a tu gusto.

```markdown
### General
- Seguir PEP 8 (longitud de línea recomendada 100–120 caracteres).
- Nombres descriptivos: variables y funciones en snake_case, clases en PascalCase.
- Evitar `import *` en producción; listar imports explícitos desde serializers y models.

### Modelos
- Un modelo por entidad; usar TextChoices para opciones fijas (Role, Plan, Status, etc.).
- Comentario breve por modelo o bloque de campos cuando aclare negocio (ej. “snapshot por si se elimina el producto”).
- Propiedades calculadas (`@property`) solo cuando no convenga persistir el valor (ej. status, balance_due, subtotal).

### Vistas (ViewSets)
- Una ViewSet por recurso principal; acciones extra con `@action(detail=...)` y métodos HTTP claros.
- Permisos declarativos por ViewSet; lógica por acción con `get_permissions()` si aplica.
- Queryset filtrado por usuario cuando el rol no es admin (get_queryset).
- Respuestas con status codes explícitos; mensajes de error en español en `detail`.

### Serializers
- Validación en el serializer; no dejar validación de negocio solo en la vista.
- Campos virtuales (write_only) para archivos (image_file, avatar_file, logo_file, receipt_file); URL solo lectura.
- Creación/actualización que afecte a otros modelos (SaleItem, InventoryTransaction) en create/update del serializer o bien en la vista, pero de forma centralizada.

### Seguridad y datos
- Nunca loguear contraseñas ni tokens; evitar print de datos sensibles en producción.
- Variables sensibles y configuración por entorno (.env); no hardcodear SECRET_KEY ni credenciales.

### Documentación
- Docstrings en español para endpoints y métodos no triviales (qué hace, qué parámetros espera).
- Mantener este documento (ESTRUCTURA_BACKEND.md) actualizado al agregar modelos o endpoints relevantes.
```

Puedes modificar este bloque (añadir reglas de tests, formato de commits, uso de type hints, etc.) según lo que quieras exigir en el proyecto.
