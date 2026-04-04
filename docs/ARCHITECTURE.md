# ARQUITECTURA - Nurax Backend ARCHITECTURE_V2

## Visión General

Arquitectura **multi-tenant enterprise-grade** con Domain-Driven Design (DDD). Cada Store es una organización independiente con sus propios usuarios, productos, ventas e inventario.

```
┌─────────────────────────────────────────────────────────────┐
│              API REST Versionizada (/api/v1/*)              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Accounts    │  │  Products    │  │   Sales      │      │
│  │(Auth, Teams) │  │ (Catalog)    │  │(Transactions)│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Inventory   │  │  Expenses    │  │   Carts      │      │
│  │   (Kárdex)   │  │ (Financial)  │  │ (Real-time)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Shared: exceptions.py, constants.py, pagination.py        │
├─────────────────────────────────────────────────────────────┤
│        PostgreSQL 15 (UUID PKs, Multi-tenancy)              │
└─────────────────────────────────────────────────────────────┘
```

---

## Contextos Acotados (Bounded Contexts) - V2

### 1. **ACCOUNTS** - Multi-Tenancy & Auth
**Responsabilidad**: Usuarios, Stores, membresías, control de acceso

**Modelos**:
- `User` (UUID PK)
  - email (USERNAME_FIELD), first_name, last_name, is_active
  - NO tiene role directo - roles en StoreMembership
  - Índices en: email

- `Store` (UUID PK) - Centro de Multi-tenancy
  - name, plan ('basico'/'pro'), tax_id, active
  - Todos los modelos de dominio tienen FK a Store
  - Índices en: name, active

- `StoreMembership` (UUID PK) - Control de Acceso
  - store FK, user FK, role ('owner'/'manager'/'cashier')
  - unique_together = (store, user) → Un rol por usuario/tienda
  - Valida: owner puede invitar, manager crea órdenes, cashier vende

- `Client` (UUID PK) - Clientes Finales
  - name, credit_limit
  - Separado de User (operadores vs compradores)

**Manager Customizado**:
```python
# En StoreMembership
StoreMembershipManager.get_user_stores(user)  # Tiendas del usuario
```

**Endpoints**:
- `GET /api/v1/accounts/users/me/` - Profile actual
- `GET /api/v1/accounts/stores/` - Mis tiendas
- `POST /api/v1/accounts/memberships/` - Agregar miembro
- `GET /api/v1/accounts/clients/` - Listar clientes

---

### 2. **PRODUCTS** - Catálogo Multi-Store
**Responsabilidad**: Productos, categorías, proveedores, códigos, empaques

**Modelos**:
- `Category` (UUID PK)
  - store FK, name
  - unique_together = (store, name)

- `Supplier` (UUID PK)
  - store FK, name, contact_info
  - indexed: (store_id, name)

- `Product` (UUID PK)
  - store FK, category FK, supplier FK
  - name, base_cost (Decimal), sale_price (Decimal), current_stock (int)
  - Validación: base_cost < sale_price
  - Propiedad: is_low_stock, is_out_of_stock

- `ProductPackaging` (UUID PK)
  - product FK, name ('Caja con 50'), quantity_per_unit

- `ProductCode` (UUID PK)
  - product FK, code (QR/EAN value), type ('ean13'/'qr'/'upc'/'shelf_label')
  - Múltiples códigos por producto

**Manager Customizado**:
```python
ProductManager.low_stock(threshold=10)    # current_stock <= threshold
ProductManager.out_of_stock()             # current_stock == 0
ProductManager.with_related()             # select_related optimizado
```

**Endpoints**:
- `GET /api/v1/products/categories/` - Filtrar por store
- `GET /api/v1/products/suppliers/` 
- `GET /api/v1/products/products/`
- `GET /api/v1/products/products/low_stock/?threshold=10`
- `GET /api/v1/products/products/out_of_stock/`
- `GET /api/v1/products/packagings/`
- `GET /api/v1/products/codes/`

---

### 3. **SALES** - Transacciones Multi-Store
**Responsabilidad**: Ventas, items, pagos, estado

**Modelos**:
- `Sale` (UUID PK)
  - store FK, customer FK (optional), cash_shift FK
  - status: PAID/PARTIAL/CANCELLED (TextChoices)
  - total_amount (Decimal), amount_paid (Decimal)
  - balance_due (property): total_amount - amount_paid
  - Auto-update: PAID si balance_due==0, PARTIAL si >0
  - Índices: (store_id, status, created_at)

- `SaleItem` (UUID PK)
  - sale FK, product FK
  - quantity (int), unit_price (Decimal - snapshot), unit_cost (Decimal - snapshot)
  - Propiedad: subtotal, profit

- `SalePayment` (UUID PK)
  - sale FK, cash_shift FK, amount (Decimal)
  - Auto-actualiza Sale.status al agregar

**Endpoints**:
- `GET /api/v1/sales/sales/` - Filtrar por store
- `POST /api/v1/sales/sales/` - Crear venta
- `POST /api/v1/sales/items/` - Agregar items
- `POST /api/v1/sales/payments/` - Registrar pago

---

### 4. **INVENTORY** - Kárdex Inmutable (Auditoría)
**Responsabilidad**: Histórico de movimientos, no creación directa

**Modelos**:
- `InventoryMovement` (UUID PK) - READ-ONLY
  - product FK, user FK (quién lo registró)
  - movement_type: SALE/PURCHASE/ADJUSTMENT/RETURN
  - quantity (int, puede ser negativo), stock_before, stock_after (ambos Decimal)
  - indexed: (product_id, movement_type, created_at)

**Auto-Creación**:
- SALE: Cuando se crea SaleItem
- PURCHASE: Cuando PurchaseOrder.mark_received()
- ADJUSTMENT: Manual via custom endpoint
- RETURN: Manual via custom endpoint

**ViewSet**: ReadOnlyModelViewSet - solo GET

**Endpoints**:
- `GET /api/v1/inventory/movements/` - Filtrar por product, type, store
- `?movement_type=sale` - Por tipo
- `?product_id=xxx` - Por producto

---

### 5. **EXPENSES** - Caja & Gastos & Compras
**Responsabilidad**: Turnos, movimientos, gastos, órdenes de compra

**Modelos**:
- `CashShift` (UUID PK)
  - store FK, opened_by FK (user)
  - opened_at, closed_at (NULL si abierto), starting_cash (Decimal)
  - is_open (property): closed_at is None
  - Validación: Solo 1 por tienda abierto

- `CashMovement` (UUID PK)
  - cash_shift FK, movement_type: IN/OUT
  - amount (Decimal), reason, created_at

- `ExpenseCategory` (UUID PK)
  - store FK, name ('Servicios'/'Nómina'/'Compras'/etc)
  - unique_together = (store, name)

- `Expense` (UUID PK)
  - store FK, category FK
  - cash_shift FK (opcional), purchase_order FK (opcional)
  - amount (Decimal), description, payment_method: CASH/TRANSFER/CARD

- `PurchaseOrder` (UUID PK)
  - store FK, supplier FK
  - status: PENDING/RECEIVED/CANCELLED
  - total_cost (Decimal)
  - mark_received: @action atomica que actualiza stock + crea InventoryMovements

- `PurchaseOrderItem` (UUID PK)
  - purchase_order FK, product FK
  - quantity (int), unit_cost (Decimal - snapshot)

**Endpoints**:
- `POST /api/v1/expenses/cash-shifts/` - Abrir turno
- `GET /api/v1/expenses/cash-shifts/current_open/?store_id=xxx` - Turno actual
- `POST /api/v1/expenses/cash-shifts/{id}/close/` - Cerrar turno
- `POST /api/v1/expenses/cash-movements/` - Registrar movimiento
- `POST /api/v1/expenses/expenses/` - Registrar gasto
- `GET /api/v1/expenses/purchase-orders/`
- `POST /api/v1/expenses/purchase-orders/{id}/mark_received/` - Recibir compra (atomic)

---

### 6. **CARTS** - Carrito Real-time (WebSocket-Ready)
**Responsabilidad**: Carrito activo, sincronización real-time

**Modelos**:
- `ActiveCart` (UUID PK)
  - store FK, user FK, session_id (unique, para Pusher)
  - total_temp (Decimal - denormalized), updated_at
  - WebSocket: Canal Pusher = `carts.{session_id}`

- `CartItem` (UUID PK)
  - cart FK, product FK
  - quantity (int), unit_price_at_time (Decimal)
  - unique_together = (cart, product)
  - Propiedad: subtotal

**Custom Actions**:
- `POST /carts/{id}/add_item/` - Agregar producto
- `POST /carts/{id}/remove_item/` - Quitar producto
- `POST /carts/{id}/clear/` - Vaciar carrito
- Todos recalculan total_temp y broadcast via Pusher

**Endpoints**:
- `POST /api/v1/carts/` - Crear carrito
- `GET /api/v1/carts/` - Mi carrito activo
- `POST /api/v1/carts/{id}/add_item/`
- `POST /api/v1/carts/{id}/remove_item/`
- `POST /api/v1/carts/{id}/clear/`

---

## Patrones Arquitectónicos

### 1. Multi-Tenancy Pattern
```python
# En todos los ViewSets
def get_queryset(self):
    user_stores = self.request.user.storemembership_set.values_list('store_id', flat=True)
    return self.model.objects.filter(store_id__in=user_stores)

# En perform_create
def perform_create(self, serializer):
    store_id = self.request.query_params.get('store_id')
    # Verificar acceso
    serializer.save(store_id=store_id, user=self.request.user)
```

### 2. Atomic Operations
```python
from django.db import transaction

@action(detail=True, methods=['post'])
def mark_received(self, request, pk=None):
    order = self.get_object()
    with transaction.atomic():
        order.status = PurchaseOrder.Status.RECEIVED
        order.save()
        
        for item in order.items.all():
            item.product.current_stock += item.quantity
            item.product.save()
            
            InventoryMovement.objects.create(
                product=item.product,
                movement_type=InventoryMovement.MovementType.PURCHASE,
                quantity=item.quantity,
                stock_before=old_stock,
                stock_after=item.product.current_stock
            )
```

### 3. Snapshot Fields
Campos almacenados en el momento de la transacción:
- SaleItem.unit_price (no product.sale_price)
- SaleItem.unit_cost (no product.base_cost)
- PurchaseOrderItem.unit_cost

**Beneficios**: Histórico correcto de precios, auditoría.

### 4. UUID Primary Keys
Todos los modelos usan UUID:
```python
id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
```

**Beneficios**: Escalabilidad, seguridad, distributed systems.

### 5. QuerySet Optimization
```python
# En managers
def with_related(self):
    return self.select_related('store', 'category', 'supplier')
    
def with_nested(self):
    return self.prefetch_related('items', 'payments', 'movements')
```

---

## Flujos de Negocio Clave - V2

### Flujo 1: Venta Normal
```
1. CashShift.open() al inicio del turno
2. POST /sales/ → Crear Sale (store_id, cash_shift_id)
3. POST /sales/items/ → Agregar SaleItem[] (quantity, unit_price)
4. POST /sales/payments/ → Pagar
5. Sale.status AUTO → PAID (si amount_paid >= total)
6. InventoryMovement → AUTO (product stock -= quantity)
7. CashShift.close() al fin del turno
```

### Flujo 2: Compra a Proveedor
```
1. POST /purchase-orders/ → Crear orden (supplier_id)
2. POST /purchase-orders/{id}/items/ → Agregar items
3. POST /purchase-orders/{id}/mark_received/ → Marcar recibida
   a. product.current_stock += quantity (ATOMIC)
   b. InventoryMovement.create(type=PURCHASE)
   c. order.status = RECEIVED
```

### Flujo 3: Registrar Gasto
```
1. POST /expenses/ → Registrar gasto (amount, category, payment_method)
2. Si payment_method=CASH: Se vincula a cash_shift_id
3. Si es de PurchaseOrder: Se copia el total
```

### Flujo 4: Carrito Real-time
```
1. POST /carts/ → Crear carrito (store_id, user_id, session_id)
2. POST /carts/{id}/add_item/ → Agregar item
   a. CartItem.create(product_id, quantity)
   b. Recalcular ActiveCart.total_temp
   c. Pusher.broadcast('carts.{session_id}', 'item_added')
3. Cliente recibe actualización en tiempo real
4. POST /sales/ + carrito → Convertir a venta
```

---

## Índices de Base de Datos

Todos los modelos incluyen índices estratégicos:

```python
# Ejemplo: Product
class Meta:
    indexes = [
        models.Index(fields=['store_id', 'name']),
        models.Index(fields=['store_id', 'current_stock']),
        models.Index(fields=['-created_at']),
    ]
```

---

## Security & Multi-Tenancy

### Row-Level Security
```python
# Un usuario solo ve datos de sus tiendas
user.storemembership_set.values_list('store_id')
```

### Permission Classes
```python
permission_classes = [IsAuthenticated]  # Todo requiere autenticación
```

### Role-Based Validation
```python
if membership.role != 'owner':
    raise PermissionDenied("Solo propietarios pueden invitar usuarios")
```

---

## Type Hints & Code Quality

✅ Type hints completos en todos los modelos, serializers, views
✅ Docstrings descriptivos (Google style)
✅ Error handling explícito
✅ Validación multi-capas (model → serializer → view)

---

## Performance Optimizations

1. **Select Related** (1-to-1, ForeignKey)
   ```python
   .select_related('store', 'category', 'supplier')
   ```

2. **Prefetch Related** (Reverse relations)
   ```python
   .prefetch_related('items', 'payments', 'movements')
   ```

3. **Pagination**
   ```python
   MAX_PAGE_SIZE = 100
   PAGE_SIZE = 20
   ```

4. **Caching** (ready for Redis)
   - QuerySets frecuentes
   - Store configurations

---

## Próximas Mejoras

1. **WebSocket** - Pusher/Django Channels para real-time
2. **Redis** - Caching de QuerySets frecuentes
3. **Webhooks** - Notificaciones a sistemas externos
4. **GraphQL** - API alternativa para queries complejas
5. **Audit Trail** - django-audit-log para cambios
6. **Batch Operations** - Importación de productos vía CSV

---

## Referencias

- [Django Best Practices](https://docs.djangoproject.com/en/6.0/)
- [DDD Eric Evans](https://www.domainlanguage.com/ddd/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Multi-Tenancy Patterns](https://www.postgresql.org/docs/current/ddl-schemas.html)

