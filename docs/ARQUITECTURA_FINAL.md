# Arquitectura Final

Backend Django REST Framework para Nurax. El sistema esta organizado como una API multi-tienda con autenticacion JWT por cookies HttpOnly, catalogo de productos, ventas, caja, gastos, inventario y carritos sincronizados.

## Stack Real

- Django `6.0.2`
- Django REST Framework `3.16.1`
- Simple JWT
- drf-spectacular para OpenAPI/Swagger
- django-filter
- PostgreSQL en Docker, SQLite como fallback local si no hay `DATABASE_URL` ni `DB_HOST`
- Cloudinary para imagenes
- Pusher para sincronizacion de carrito

## Estructura

```text
nurax_backend/
  apps/
    accounts/
    products/
    inventory/
    expenses/
    sales/
    carts/
  core/
    settings.py
    urls.py
  utils/
    auth_views.py
    authentication.py
    pagination.py
  docker-compose.yml
  init_db.py
  manage.py
```

## Apps

| App | Responsabilidad |
| --- | --- |
| `accounts` | Usuarios, tiendas, membresias, clientes, equipo y onboarding |
| `products` | Categorias, proveedores, productos, empaques, codigos y variaciones |
| `inventory` | Kardex de movimientos de inventario |
| `expenses` | Turnos de caja, movimientos de efectivo, gastos y ordenes de compra |
| `sales` | Ventas, items, pagos, cuentas por cobrar y cancelaciones |
| `carts` | Carritos activos, carritos aparcados y sincronizacion con Pusher |

## Modelo de Datos

### Accounts

- `User`
  - Autenticacion por `email`.
  - Campos principales: `username`, `email`, `role`, `avatar_url`, `name`.
  - Roles globales: `admin`, `cliente`.
- `Store`
  - Representa una tienda/empresa.
  - Campos principales: `name`, `plan`, `tax_id`, `currency_symbol`, `address`, `phone`, `country_code`, `ticket_message`, `logo_url`, `niche`, `active`, `default_cash`.
  - Planes: `basico`, `pro`.
- `StoreMembership`
  - Relaciona `User` con `Store`.
  - Roles de tienda: `owner`, `manager`, `cashier`.
- `Client`
  - Cliente de venta/credito.
  - Actualmente no tiene FK directa a `Store`; las ventas lo referencian desde `Sale.customer`.

### Products

- `Category`: categoria por tienda.
- `Supplier`: proveedor por tienda.
- `Product`
  - Pertenece a `Store`.
  - Usa `base_cost`, `sale_price`, `current_stock`.
  - Imagen mediante `image_url`.
- `ProductPackaging`: empaques por producto.
- `ProductCode`: codigos UPC/EAN/QR/etiqueta.
- `ProductVariation`: variaciones como color, talla, peso, material u otro.

### Inventory

- `InventoryMovement`
  - Movimiento de inventario por producto.
  - Tipos: `sale`, `purchase`, `adjustment`, `return`.
  - Registra `quantity`, `stock_before`, `stock_after`.

### Expenses

- `CashShift`
  - Turno de caja por tienda.
  - `opened_by`, `opened_at`, `closed_at`, `starting_cash`, `expected_cash`, `actual_cash`, `difference`.
- `CashMovement`
  - Entrada/salida de efectivo dentro de un turno.
- `ExpenseCategory`
  - Categoria de gasto por tienda.
- `Expense`
  - Gasto operativo por tienda.
- `PurchaseOrder` y `PurchaseOrderItem`
  - Ordenes de compra a proveedor.
  - `mark_received` actualiza stock y crea movimientos de inventario.

### Sales

- `Sale`
  - Venta por tienda.
  - Campos: `id` (UUID tecnico), `sale_number` (folio incremental visible por tienda), `transaction_id`, `store`, `cash_shift`, `customer`, `status`, `sale_type`, `total_amount`, `amount_paid`, `amount_tendered`, `change`.
  - Estados: `paid`, `partial`, `cancelled`.
  - Tipos: `cash`, `credit`, `layaway`.
- `SaleItem`
  - Producto vendido, cantidad, precio y costo al momento de la venta.
- `SalePayment`
  - Abonos/pagos de venta.
  - Metodo: `cash`, `card`, `transfer`, `other`.

### Carts

- `ActiveCart`
  - Carrito activo por tienda, usuario y `session_id`.
  - Puede aparcarse con `is_parked` y `parked_at`.
- `CartItem`
  - Producto, cantidad y precio al momento de agregarlo al carrito.

## Autenticacion

El backend usa JWT en cookies HttpOnly:

- Login: `POST /api/auth/login/`
- Refresh: `POST /api/auth/refresh/`
- Logout: `POST /api/auth/logout/`

`utils.authentication.CookieJWTAuthentication` lee `access_token` desde cookie. Tambien queda habilitado el fallback por header `Authorization: Bearer ...`.

## Multi-Tienda y Permisos

- La pertenencia a tienda se resuelve con `StoreMembership`.
- Los viewsets de productos, ventas, inventario, gastos y caja filtran por tiendas donde el usuario es miembro.
- Usuarios globales `admin` tienen rutas especiales de administracion de clientes del software.
- La gestion de empleados solo la puede hacer un owner de tienda o un admin global.

## Flujos Clave

### Onboarding

`POST /api/v1/onboarding/wizard/` crea o actualiza la tienda del usuario, marca el primer setup como completo y genera categorias sugeridas por nicho. Puede crear un proveedor inicial.

### Venta

1. El frontend crea una venta con `SaleCreateSerializer`.
2. El backend asigna `sale_number` incremental por tienda (con control de concurrencia).
3. Se crean `SaleItem`.
4. Si hay pago inicial, se crea `SalePayment`.
5. Si el item tiene producto, se descuenta `Product.current_stock`.
6. Se registra `InventoryMovement`.

### Cancelacion de Venta

`POST /api/v1/sales/sales/{id}/cancel/` marca la venta como `cancelled` y devuelve stock con movimientos de inventario.

### Compra Recibida

`POST /api/v1/expenses/purchase-orders/{id}/mark_received/` marca la orden como recibida, incrementa `current_stock` y registra movimientos.

### Carrito

Los carritos se sincronizan con Pusher. El endpoint `sync-cart` actualiza el carrito activo compartido por usuario/tienda y emite `CART_UPDATED`.

## Integraciones

- Cloudinary: avatares, logos y fotos de producto.
- Pusher: canales privados de carrito.
- Swagger: `/api/docs/`.
