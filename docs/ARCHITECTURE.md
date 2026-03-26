# ARQUITECTURA - Sistema de Gestión de Inventario Nurax

## Visión General

La refactorización del backend implementa **Domain-Driven Design (DDD)** con 5 **contextos acotados** independientes, cada uno optimizado para un dominio específico del negocio.

```
┌─────────────────────────────────────────────────────────────┐
│              API REST Versionizada (/api/v1/*)              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Accounts    │  │  Products    │  │   Sales      │      │
│  │   (Users)    │  │ (Catalog)    │  │(Transactions)│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │  Inventory   │  │  Expenses    │                        │
│  │   (Kárdex)   │  │ (Financial)  │                        │
│  └──────────────┘  └──────────────┘                        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Shared: exceptions.py, constants.py, pagination.py        │
├─────────────────────────────────────────────────────────────┤
│              PostgreSQL 15 (dev), SQLite (test)             │
└─────────────────────────────────────────────────────────────┘
```

---

## Contextos Acotados (Bounded Contexts)

### 1. **ACCOUNTS** - Gestión de Usuarios y Perfiles
**Responsabilidad**: Autenticación, autorización, perfiles de tienda

**Modelos**:
- `User` (extends AbstractUser)
  - Roles: 'admin' / 'cliente'
  - Campo: avatar_url (Cloudinary)
  - Índices en: email, role

- `Client`: Empresa contratante del servicio
  - plan: 'basico' / 'pro' (suscripción)
  - Índices en: email, active

- `StoreProfile`: Configuración por usuario
  - company_name, logo_url, tax_id, address, phone
  - Relación 1:1 con User

- `ActiveSessionCart`: Rastreador de carrito de sesión

**Manager Customizado**:
```python
UserManager.admins()          # Solo admins
UserManager.clients()         # Solo clientes
UserManager.active()          # Usuarios activos
```

**Endpoints**:
- `GET/POST /api/v1/accounts/users/`
- `GET/POST /api/v1/accounts/clients/`
- `GET/POST /api/v1/accounts/store-profiles/`

---

### 2. **PRODUCTS** - Catálogo de Productos
**Responsabilidad**: Definición de inventario, categorización, proveedores

**Modelos**:
- `Product`
  - user FK, category FK, supplier FK
  - sku (único por user), stock, price
  - Índices en: sku, (user, category), stock
  - Propiedad: `status` → 'in_stock' / 'low_stock' / 'out_of_stock'

- `Category`: Clasificación de productos
  - name (único)

- `Supplier`: Gestor de proveedores
  - email, phone, company_name
  - Índices en: user, email

**Manager Customizado**:
```python
ProductManager.in_stock()       # stock > 10
ProductManager.low_stock(10)    # 0 < stock <= 10
ProductManager.out_of_stock()   # stock == 0
ProductManager.with_related()   # select_related optimizado
```

**Validadores**:
- `validate_sku_format()`: SKU entre 3-50 caracteres
- `validate_stock_not_negative()`: Stock no negativo
- `validate_positive_decimal()`: Precios positivos

**Endpoints**:
- `GET/POST /api/v1/products/products/`
- `GET /api/v1/products/products/low_stock/`
- `GET /api/v1/products/products/out_of_stock/`
- `GET/POST /api/v1/products/categories/`
- `GET/POST /api/v1/products/suppliers/`

---

### 3. **SALES** - Transacciones y Pagos
**Responsabilidad**: Registro de ventas, items, pagos parciales (crédito/apartado)

**Modelos**:
- `Sale`
  - transaction_id (único), status (completed/pending/cancelled/credit/layaway)
  - total, amount_paid, customer_name/phone snapshot
  - Propiedad: `balance_due` → Calcula saldo adeudado
  - Índices en: transaction_id, status, created_at

- `SaleItem`: Items dentro de una venta
  - product_name (snapshot), quantity, unit_price
  - Propiedad: `subtotal` = quantity * unit_price
  - related_name: 'items'

- `SalePayment`: Abonos/pagos a ventas
  - amount, user (quién registró)
  - related_name: 'payments'
  - Índices compuestos: (sale, created_at)

**Manager Customizado**:
```python
SaleManager.completed()        # status == 'completed'
SaleManager.pending()          # status == 'pending'
SaleManager.with_payments()    # prefetch_related optimizado
```

**Endpoints**:
- `GET/POST /api/v1/sales/sales/`
- `GET /api/v1/sales/sales/pending_payments/` (custom action)
- `GET/POST /api/v1/sales/payments/`

---

### 4. **INVENTORY** - Kárdex y Movimientos
**Responsabilidad**: Registro de cambios de inventario, auditoría

**Modelos**:
- `InventoryTransaction`
  - product FK, transaction_type (in/out/adjustment/waste)
  - quantity, reason, user
  - Índices: (transaction_type, created_at), product

- `InventoryMovement`
  - movement_type (sale/restock/adjust), quantity
  - unit_cost, total_cost, cash_shift FK
  - Índices: (movement_type, created_at), product

**Manager Customizado**:
```python
InventoryTransactionManager.entries()  # in, restock
InventoryTransactionManager.exits()    # out, sales
```

**Endpoints**:
- `GET/POST /api/v1/inventory/transactions/`
- `GET /api/v1/inventory/transactions/?transaction_type=in`
- `GET/POST /api/v1/inventory/movements/`

---

### 5. **EXPENSES** - Gestión Financiera
**Responsabilidad**: Gasto operativo, reconciliación de caja

**Modelos**:
- `Expense`
  - category (servicios/nomina/proveedores/inventario/varios)
  - amount, description, receipt_url
  - Índices: (category, date), user

- `CashShift`
  - user, opened_at, closed_at, starting_cash
  - expected_cash, actual_cash, difference
  - Índices: opened_at, user

**Manager Customizado**:
```python
ExpenseManager.by_category('servicios')
CashShiftManager.open()    # closed_at is NULL
CashShiftManager.closed()  # closed_at is NOT NULL
```

**Endpoints**:
- `GET/POST /api/v1/expenses/expenses/`
- `GET /api/v1/expenses/expenses/?category=servicios`
- `GET/POST /api/v1/expenses/cash-shifts/`
- `GET /api/v1/expenses/cash-shifts/current/` (custom action)

---

## Patrones Arquitectónicos

### 1. Manager/QuerySet Pattern
Cada app implementa custom managers con QuerySet optimizations:

```python
# Ejemplo: ProductManager
class ProductQuerySet(models.QuerySet):
    def in_stock(self):
        return self.filter(stock__gt=10)
    
    def with_related(self):
        return self.select_related('category', 'supplier', 'user')

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)
    
    def in_stock(self):
        return self.get_queryset().in_stock()
```

**Beneficios**:
- ✅ Evita N+1 queries
- ✅ Código reutilizable
- ✅ Semántica clara

### 2. Multi-Layer Validation
Cada app implementa validación en 3 capas:

1. **Model Validators** (field-level)
   ```python
   price = DecimalField(validators=[MinValueValidator(Decimal('0.01'))])
   ```

2. **Custom Validators** (business logic)
   ```python
   # products/validators.py
   def validate_sku_format(value):
       if not (3 <= len(value) <= 50):
           raise ValidationError("SKU debe tener 3-50 caracteres")
   ```

3. **Serializer Validators** (API layer)
   ```python
   def validate_stock(self, value):
       if value < 0:
           raise ValidationError("Stock no puede ser negativo")
       return value
   ```

### 3. Centralized Exception Handling
Todas las apps usan excepciones custom heredadas de `APIException`:

```python
# api/exceptions.py
class InsufficientStockError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Stock insuficiente para esta operación"

class InvalidTransactionError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Transacción inválida"
```

### 4. Constants Centralized
Toda configuración en `api/constants.py`:

```python
SALE_STATUS_COMPLETED = 'completed'
SALE_STATUS_CREDIT = 'credit'

STOCK_LOW_THRESHOLD = 10
STOCK_CRITICAL_THRESHOLD = 5

PAGINATION_MAX = 100
PAGINATION_DEFAULT = 20
```

### 5. API Versionization
Endpoints estructurados con versionado explícito:

```
/api/v1/accounts/users/
/api/v1/products/categories/
/api/v1/sales/sales/
/api/v1/inventory/transactions/
/api/v1/expenses/cash-shifts/
```

---

## Flujos de Negocio Clave

### Flujo 1: Venta Simple
```
1. Crear Sale (status='completed', total calculado)
2. Agregar items: SaleItem[] con producto y cantidad
3. Restar stock automáticamente (trigger opcional)
4. Registrar InventoryMovement (type='sale')
```

### Flujo 2: Venta a Crédito
```
1. Crear Sale (status='credit', total=monto crédito)
2. Agregar items
3. SalePayment #1: abono parcial
4. SalePayment #2: abono final
5. balance_due: calcula automáticamente
```

### Flujo 3: Reconciliación de Caja
```
1. CashShift.open() al inicio del turno
2. Registrar Expense[] durante turno
3. Al cierre: CashShift.closed_at = now()
4. Validar: actual_cash vs expected_cash
5. Registrar diferencia
```

---

## Estructura de Db_Tables

Eliminación completa de prefijo "api_":

```sql
user               # User model
client             # Client model
store_profile      # StoreProfile model
active_session_cart # ActiveSessionCart model

category           # Category model
product            # Product model
supplier           # Supplier model

sale               # Sale model
sale_item          # SaleItem model
sale_payment       # SalePayment model

inventory_transaction  # InventoryTransaction model
inventory_movement     # InventoryMovement model

expense            # Expense model
cash_shift         # CashShift model
```

---

## Testing Strategy

**Total Coverage**: 60 tests automáticos

### Unit Tests (52 tests)
- **accounts/tests.py**: 7 tests
  - UserModel, ClientModel, StoreProfileModel, ActiveSessionCartModel
  - Field validation, relationships, string representations

- **products/tests.py**: 11 tests
  - CategoryModel, SupplierModel, ProductModel
  - Status tracking, QuerySet optimization

- **sales/tests.py**: 14 tests
  - SaleModel (balance_due property), SaleItemModel, SalePaymentModel
  - Multi-payment scenarios

- **inventory/tests.py**: 7 tests
  - InventoryTransactionModel, InventoryMovementModel
  - QuerySet filtering (entries/exits)

- **expenses/tests.py**: 13 tests
  - ExpenseModel, CashShiftModel
  - Queryset operations (by_category, open/closed)

### Integration Tests (8 tests)
- **api/tests.py**
  - AccountsAPITest: user endpoints
  - ProductsAPITest: catalog endpoints
  - SalesAPITest: transaction endpoints
  - WorkflowIntegrationTest: complete business workflows

---

## Performance Optimizations

### 1. Select Related (1-to-1, Foreign Keys)
```python
# products/managers.py
.select_related('user', 'category', 'supplier')
```

### 2. Prefetch Related (Reverse Relations)
```python
# sales/managers.py
.prefetch_related('items', 'payments')
```

### 3. Database Indexes
Todos los modelos incluyen índices estratégicos:
- Primary keys
- Foreign keys frecuentemente filtrados
- Campos de búsqueda (email, sku, transaction_id)
- Campos de ordenamiento (created_at, status)

### 4. Pagination
Endpoints implementan paginación por defecto:
```python
MAX_PAGE_SIZE = 100
PAGE_SIZE = 20
```

---

## Type Hints & Code Quality

Todos los modelos, serializers y views incluyen:
- ✅ Type hints completos
- ✅ Docstrings descriptivos
- ✅ Error handling explícito
- ✅ Validación multi-capas

---

## Próximas Mejoras

1. **GraphQL Layer**: Considerar GraphQL para queries complejas
2. **Caching**: Redis para QuerySets frecuentes
3. **Webhooks**: Pusher integración para real-time
4. **Auditoría**: Registro de cambios (django-audit-log)
5. **Admin Avanzado**: Acciones en bulk en admin
6. **API Documentation**: Swagger/OpenAPI completo

---

## Referencias

- [Django Best Practices](https://docs.djangoproject.com/en/6.0/)
- [DDD Eric Evans](https://www.domainlanguage.com/ddd/)
- [Django REST Framework](https://www.django-rest-framework.org/)
