# API

Base local:

```text
http://localhost:8000
```

Swagger:

```text
GET /api/docs/
GET /api/schema/
```

La mayoria de endpoints requiere autenticacion. El login usa cookies HttpOnly, pero tambien se acepta `Authorization: Bearer <token>`.

## Autenticacion

| Metodo | Ruta | Uso |
| --- | --- | --- |
| `POST` | `/api/auth/login/` | Inicia sesion y setea `access_token`/`refresh_token` como cookies |
| `POST` | `/api/auth/refresh/` | Renueva `access_token` desde cookie `refresh_token` |
| `POST` | `/api/auth/logout/` | Borra cookies de sesion |

## Accounts

| Metodo | Ruta | Uso |
| --- | --- | --- |
| `GET/PATCH` | `/api/v1/accounts/users/me/` | Perfil del usuario actual |
| `PATCH` | `/api/v1/accounts/users/change-password/` | Cambia contrasena |
| `POST` | `/api/v1/accounts/users/register/` | Registro simple |
| `GET` | `/api/v1/accounts/users/software-clients/` | Admin: lista clientes del software |
| `PATCH` | `/api/v1/accounts/users/software-clients/{user_id}/toggle-active/` | Admin: activa/desactiva usuario owner |
| `DELETE` | `/api/v1/accounts/users/software-clients/{user_id}/` | Admin: elimina cliente del software |
| `CRUD` | `/api/v1/accounts/stores/` | Tiendas accesibles por membresia |
| `POST` | `/api/v1/accounts/stores/create-with-owner/` | Crea tienda, owner y membresia |
| `GET` | `/api/v1/accounts/stores/{id}/memberships/` | Membresias de una tienda |
| `CRUD` | `/api/v1/accounts/memberships/` | Membresias administrables |
| `CRUD` | `/api/v1/accounts/clients/` | Clientes de venta/credito |
| `GET/POST` | `/api/v1/accounts/stores/{store_id}/employees/` | Lista o crea empleados |
| `PATCH` | `/api/v1/accounts/stores/{store_id}/employees/{user_id}/` | Edita empleado |
| `POST` | `/api/v1/accounts/stores/{store_id}/employees/{user_id}/reset-password/` | Resetea contrasena de empleado |

Alias existente:

```text
GET/POST /api/v1/stores/{store_id}/employees/
```

## Onboarding

| Metodo | Ruta | Uso |
| --- | --- | --- |
| `POST` | `/api/v1/onboarding/wizard/` | Completa configuracion inicial de tienda |

## Products

Todos bajo `/api/v1/products/`.

| Recurso | Ruta |
| --- | --- |
| Productos | `/products/` |
| Categorias | `/categories/` |
| Proveedores | `/suppliers/` |
| Empaques | `/packagings/` |
| Codigos | `/codes/` |
| Variaciones | `/variations/` |

Acciones de productos:

| Metodo | Ruta | Uso |
| --- | --- | --- |
| `POST` | `/api/v1/products/products/bulk_delete/` | Borra productos por lista de IDs |
| `GET` | `/api/v1/products/products/low_stock/` | Productos bajo umbral |
| `GET` | `/api/v1/products/products/out_of_stock/` | Productos sin stock |
| `GET` | `/api/v1/products/products/{id}/movements/` | Ultimos movimientos de inventario del producto |

Filtros utiles:

```text
store_id
category
supplier
stock_status=low_stock|out_of_stock
search
ordering=name|-created_at|current_stock|sale_price
```

## Inventory

| Metodo | Ruta | Uso |
| --- | --- | --- |
| `GET` | `/api/v1/inventory/movements/` | Lista movimientos filtrados por tiendas del usuario |
| `GET` | `/api/v1/inventory/movements/{id}/` | Detalle de movimiento |

Filtros:

```text
product
movement_type
created_at
search=nombre_producto
ordering=created_at|product
```

## Expenses

Todos bajo `/api/v1/expenses/`.

| Recurso | Ruta |
| --- | --- |
| Turnos de caja | `/cash-shifts/` |
| Movimientos de caja | `/cash-movements/` |
| Categorias de gasto | `/expense-categories/` |
| Gastos | `/expenses/` |
| Ordenes de compra | `/purchase-orders/` |

Acciones:

| Metodo | Ruta | Uso |
| --- | --- | --- |
| `GET` | `/api/v1/expenses/cash-shifts/current_open/?store_id={id}` | Turno abierto actual |
| `POST` | `/api/v1/expenses/cash-shifts/{id}/close/` | Cierra turno |
| `POST` | `/api/v1/expenses/purchase-orders/{id}/mark_received/` | Marca compra recibida y actualiza stock |

Nota: la apertura de turno usa el endpoint REST limpio:

```text
POST /api/v1/expenses/cash-shifts/
```

## Sales

Todos bajo `/api/v1/sales/`.

| Recurso | Ruta |
| --- | --- |
| Ventas | `/sales/` |
| Items | `/items/` |
| Pagos | `/payments/` |

Acciones:

| Metodo | Ruta | Uso |
| --- | --- | --- |
| `GET` | `/api/v1/sales/sales/pending_payments/` | Ventas con pagos pendientes |
| `GET` | `/api/v1/sales/sales/accounts_receivable/` | Cuentas por cobrar |
| `POST` | `/api/v1/sales/sales/{id}/cancel/` | Cancela venta y devuelve stock |

Filtros utiles:

```text
store
status
cash_shift
sale_type
search
ordering=created_at|total_amount|status
```

## Carts

Todos bajo `/api/v1/carts/`.

| Metodo | Ruta | Uso |
| --- | --- | --- |
| `CRUD` | `/carts/` | Carritos activos |
| `POST` | `/carts/{id}/add_item/` | Agrega item |
| `POST` | `/carts/{id}/remove_item/` | Quita item |
| `POST` | `/carts/{id}/clear/` | Vacia carrito |
| `GET` | `/carts/my-cart/` | Carrito activo del usuario |
| `POST` | `/carts/sync-cart/` | Sincroniza carrito enviado por cliente |
| `POST` | `/carts/{id}/park/` | Aparca carrito |
| `GET` | `/carts/parked/` | Lista carritos aparcados |
| `POST` | `/carts/{id}/restore/` | Restaura carrito aparcado |

Pusher auth:

```text
POST /api/pusher/auth/
```
