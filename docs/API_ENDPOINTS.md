# API Endpoints - Nurax Backend ARCHITECTURE_V2

Documentación completa de la API REST. Todos los endpoints requieren autenticación JWT (excepto login).

**Base URL:** `http://localhost:8000/api/v1/`

---

## 📋 Tabla de Contenidos

1. [Autenticación](#autenticación)
2. [Accounts (Usuarios, Tiendas, Membresías)](#accounts)
3. [Products (Catálogo)](#products)
4. [Sales (Ventas)](#sales)
5. [Inventory (Kárdex)](#inventory)
6. [Expenses (Caja, Gastos, Compras)](#expenses)
7. [Carts (Carrito en Tiempo Real)](#carts)

---

## Autenticación

### Obtener Tokens JWT

**POST** `/auth/login/`

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Refrescar Token

**POST** `/auth/refresh/`

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## Accounts

### Usuarios

#### Get Current User Profile
**GET** `/accounts/users/me/`

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true
}
```

#### Update User Profile
**PATCH** `/accounts/users/me/`

```json
{
  "first_name": "Juan",
  "last_name": "García"
}
```

#### Change Password
**PATCH** `/accounts/users/change_password/`

```json
{
  "current_password": "oldpass123",
  "new_password": "newpass456",
  "confirm_password": "newpass456"
}
```

---

### Tiendas (Stores)

#### List My Stores
**GET** `/accounts/stores/`

Obtiene todas las tiendas donde el usuario es miembro.

**Response (200):**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Electrónica Nurax",
    "plan": "pro",
    "tax_id": "J-12345678-9",
    "active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-03-01T14:20:00Z"
  }
]
```

#### Store Detail (con membresías)
**GET** `/accounts/stores/{store_id}/`

---

### Membresías de Tienda (StoreMemberships)

#### List Store Members
**GET** `/accounts/memberships/?store={store_id}`

#### Add Team Member
**POST** `/accounts/memberships/`

```json
{
  "store": "123e4567-e89b-12d3-a456-426614174000",
  "user": "550e8400-e29b-41d4-a716-446655440000",
  "role": "cashier"
}
```

**Roles:** `owner`, `manager`, `cashier`

---

### Clientes (Customers)

#### List Clients
**GET** `/accounts/clients/`

#### Create Client
**POST** `/accounts/clients/`

```json
{
  "name": "María López",
  "credit_limit": 10000.00
}
```

---

## Products

### Categorías

#### List Categories
**GET** `/products/categories/?store_id={store_id}`

#### Create Category
**POST** `/products/categories/`

```json
{
  "store": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Electrónica"
}
```

---

### Proveedores

#### List Suppliers
**GET** `/products/suppliers/?store_id={store_id}`

#### Create Supplier
**POST** `/products/suppliers/`

```json
{
  "store": "123e4567-e89b-12d3-a456-426614174000",
  "name": "ProTech Importaciones",
  "contact_info": "+58-212-1234567"
}
```

---

### Productos

#### List Products
**GET** `/products/products/?store_id={store_id}`

**Query Parameters:**
- `?category={id}` - Filtrar por categoría
- `?supplier={id}` - Filtrar por proveedor
- `?search=iphone` - Buscar por nombre

**Response (200):**
```json
{
  "count": 150,
  "results": [
    {
      "id": "prod-001",
      "store": "123e4567-e89b-12d3-a456-426614174000",
      "name": "iPhone 15 Pro",
      "base_cost": 800.00,
      "sale_price": 1299.99,
      "current_stock": 5,
      "category": "cat-001",
      "supplier": "sup-001",
      "packagings": [],
      "codes": []
    }
  ]
}
```

#### Create Product
**POST** `/products/products/`

```json
{
  "store": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Samsung Galaxy S24",
  "category": "cat-001",
  "supplier": "sup-002",
  "base_cost": 600.00,
  "sale_price": 999.99,
  "current_stock": 10
}
```

#### Low Stock Products
**GET** `/products/products/low_stock/?store_id={store_id}&threshold=10`

#### Out of Stock
**GET** `/products/products/out_of_stock/?store_id={store_id}`

---

### Empaques

#### List Packagings
**GET** `/products/packagings/?product_id={product_id}`

#### Create Packaging
**POST** `/products/packagings/`

```json
{
  "product": "prod-001",
  "name": "Caja por 50 unidades",
  "quantity_per_unit": 50
}
```

---

### Códigos QR/EAN

#### List Codes
**GET** `/products/codes/?product_id={product_id}`

#### Create Code
**POST** `/products/codes/`

```json
{
  "product": "prod-001",
  "code": "5901234123457",
  "code_type": "ean13"
}
```

**Tipos:** `ean13`, `qr`, `upc`, `shelf_label`

---

## Sales

### Ventas

#### List Sales
**GET** `/sales/sales/?store_id={store_id}`

#### Create Sale
**POST** `/sales/sales/`

```json
{
  "store": "123e4567-e89b-12d3-a456-426614174000",
  "cash_shift": "shift-001",
  "customer": null,
  "status": "paid",
  "total_amount": 1500.00,
  "amount_paid": 1500.00
}
```

#### Pending Payments
**GET** `/sales/sales/pending_payments/`

---

### Items de Venta

#### Create Sale Item
**POST** `/sales/items/`

```json
{
  "sale": "sale-001",
  "product": "prod-001",
  "quantity": 2,
  "unit_price": 1299.99,
  "unit_cost": 800.00
}
```

---

### Pagos

#### Register Payment
**POST** `/sales/payments/`

```json
{
  "sale": "sale-001",
  "cash_shift": "shift-001",
  "amount": 500.00
}
```

---

## Inventory

### Movimientos de Inventario (Kárdex - Solo lectura)

**GET** `/inventory/movements/`

**Filtros:**
- `?product={id}` - Por producto
- `?movement_type=sale` - Por tipo
- `?ordering=-created_at` - Ordenar

---

## Expenses

### Turnos de Caja

#### Open Cash Shift
**POST** `/expenses/cash-shifts/`

```json
{
  "store": "123e4567-e89b-12d3-a456-426614174000",
  "opened_by": "550e8400-e29b-41d4-a716-446655440000",
  "starting_cash": 500.00
}
```

#### Current Open Shift
**GET** `/expenses/cash-shifts/current_open/?store_id={store_id}`

#### Close Shift
**POST** `/expenses/cash-shifts/{shift_id}/close/`

---

### Movimientos de Caja

#### Record Movement
**POST** `/expenses/cash-movements/`

```json
{
  "cash_shift": "shift-001",
  "movement_type": "out",
  "amount": 50.00,
  "reason": "Pago servicios"
}
```

---

### Categorías de Gasto

#### Create Category
**POST** `/expenses/expense-categories/`

```json
{
  "store": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Servicios Públicos"
}
```

---

### Gastos

#### List Expenses
**GET** `/expenses/expenses/?store_id={store_id}`

#### Register Expense
**POST** `/expenses/expenses/`

```json
{
  "store": "123e4567-e89b-12d3-a456-426614174000",
  "category": "cat-001",
  "amount": 150.00,
  "description": "Pago factura",
  "payment_method": "transfer"
}
```

---

### Órdenes de Compra

#### List Purchase Orders
**GET** `/expenses/purchase-orders/?store_id={store_id}`

#### Create Purchase Order
**POST** `/expenses/purchase-orders/`

```json
{
  "store": "123e4567-e89b-12d3-a456-426614174000",
  "supplier": "sup-001",
  "status": "pending",
  "total_cost": 5000.00
}
```

#### Mark as Received
**POST** `/expenses/purchase-orders/{order_id}/mark_received/`

---

## Carts

### Carrito Activo

#### Create Cart
**POST** `/carts/carts/`

```json
{
  "store": "123e4567-e89b-12d3-a456-426614174000",
  "user": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "unique-session-id"
}
```

#### Add Item
**POST** `/carts/carts/{cart_id}/add_item/`

```json
{
  "product": "prod-001",
  "quantity": 1,
  "unit_price_at_time": 1299.99
}
```

#### Remove Item
**POST** `/carts/carts/{cart_id}/remove_item/`

```json
{
  "item_id": "item-001"
}
```

#### Clear Cart
**POST** `/carts/carts/{cart_id}/clear/`

---

## Status Codes

- `200 OK` - Éxito
- `201 Created` - Creado
- `400 Bad Request` - Datos inválidos
- `401 Unauthorized` - No autenticado
- `403 Forbidden` - No autorizado
- `404 Not Found` - No existe

- **Swagger UI**: `/api/docs/` (interfaz gráfica)
- **ReDoc**: `/api/redoc/` (documentación UI alternativa)
- **OpenAPI Schema**: `/api/schema/` (JSON raw)

---

## Códigos de Estado HTTP

| Código | Significado | Caso de Uso |
|--------|-------------|------------|
| **200** | OK | GET exitoso, PUT/PATCH exitoso |
| **201** | Created | POST exitoso (nuevo recurso) |
| **204** | No Content | DELETE exitoso |
| **400** | Bad Request | Datos inválidos/incompletos |
| **401** | Unauthorized | JWT inválido/expirado |
| **403** | Forbidden | Usuario no tiene permisos |
| **404** | Not Found | Recurso no existe |
| **500** | Server Error | Error en servidor |

---

## Errores Comunes y Respuestas

### **Sin Token**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### **Token Expirado**
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

### **Datos Incompletos**
```json
{
  "field_name": [
    "This field is required."
  ]
}
```

### **Recurso No Encontrado (404)**
```json
{
  "detail": "Not found."
}
```

---

## Ejemplos de Uso (cURL)

### **Autenticarse**
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@nurax.local","password":"admin123"}'
```

### **Listar Productos**
```bash
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### **Crear Venta**
```bash
curl -X POST http://localhost:8000/api/sales/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "total": "199.99",
    "customer_name": "Juan",
    "amount_paid": "199.99",
    "items": [{"product": 1, "quantity": 1, "unit_price": "199.99"}]
  }'
```

### **Abrir Turno**
```bash
curl -X POST http://localhost:8000/api/cash-shifts/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"starting_cash": "500.00"}'
```

---

## Paginación

Por defecto, los endpoints que returnan listas están paginados con **10 items por página**.

**Respuesta paginada:**
```json
{
  "count": 42,
  "next": "http://localhost:8000/api/products/?page=2",
  "previous": null,
  "results": [...]
}
```

**Cambiar página:**
```bash
GET /api/products/?page=3
```

**Cambiar tamaño página:**
```bash
GET /api/products/?page_size=50
```

---

## Filtrado Avanzado

Muchos endpoints soportan filtrado por query parameters:

**Ejemplo: Ventas completadas en este mes**
```bash
GET /api/sales/?status=completed&created_at__gte=2024-03-01
```

**Campos filtrables por entidad:**
- **Product**: category, status, user
- **Sale**: status, user, customer_name
- **Expense**: category, supplier, cash_shift
- **CashShift**: user, closed_at

---

**Última actualización:** Marzo 2026  
**Versión API:** 1.0.0
