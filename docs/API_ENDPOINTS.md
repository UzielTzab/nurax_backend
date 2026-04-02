# API Endpoints - Nurax Backend

Listado completo de endpoints de la API REST. Todos requieren autenticación con JWT.

---

## Autenticación

### **Obtener Tokens JWT**

**POST** `/api/token/`

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Respuesta (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### **Refrescar Token**

**POST** `/api/token/refresh/`

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Respuesta (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## Users

### **List/Create Users**

- **GET** `/api/users/` - Listar usuarios (solo admin)
- **POST** `/api/users/` - Crear usuario (registro)

**POST Body:**
```json
{
  "email": "newuser@example.com",
  "username": "newuser",
  "password": "secure123",
  "name": "Juan Pérez",
  "role": "cliente"
}
```

### **Detail/Update/Delete**

- **GET** `/api/users/{id}/` - Obtener usuario
- **PUT** `/api/users/{id}/` - Actualizar usuario
- **PATCH** `/api/users/{id}/` - Actualizar parcial
- **DELETE** `/api/users/{id}/` - Eliminar usuario

---

## Products

### **List/Create Products**

**GET** `/api/products/` - Listar productos del usuario actual

**Parámetros query:**
- `?category=Electrónica` - Filtrar por categoría
- `?status=in_stock` - Filtrar por stock (in_stock, low_stock, out_of_stock)
- `?search=iphone` - Buscar por nombre
- `?page=2` - Paginación
- `?page_size=50` - Cambiar tamaño página

**POST** `/api/products/` - Crear producto

```json
{
  "name": "iPhone 15 Pro",
  "category": 1,
  "supplier": 2,
  "sku": "IPHONE-15-PRO",
  "stock": 5,
  "price": "1299.99",
  "image_url": "https://cloudinary.com/image.jpg"
}
```

### **Detail/Update/Delete**

- **GET** `/api/products/{id}/` - Obtener producto
- **PUT** `/api/products/{id}/` - Actualizar producto
- **PATCH** `/api/products/{id}/` - Actualizar parcial (útil para stock)
- **DELETE** `/api/products/{id}/` - Eliminar producto

**PATCH Body (actualizar solo stock):**
```json
{
  "stock": 10
}
```

---

## Categories

### **List/Create**

- **GET** `/api/categories/` - Listar categorías
- **POST** `/api/categories/` - Crear categoría

**POST Body:**
```json
{
  "name": "Electrónica"
}
```

### **Detail/Update/Delete**

- **GET** `/api/categories/{id}/`
- **PUT** `/api/categories/{id}/`
- **DELETE** `/api/categories/{id}/`

---

## Suppliers

### **List/Create Suppliers**

**GET** `/api/suppliers/` - Listar proveedores del usuario

**POST** `/api/suppliers/` - Crear proveedor

```json
{
  "name": "TechWholesale Inc",
  "email": "contact@techwholesale.com",
  "phone": "+1-800-TECH",
  "company": "TechWholesale"
}
```

### **Detail/Update/Delete**

- **GET** `/api/suppliers/{id}/`
- **PUT** `/api/suppliers/{id}/`
- **PATCH** `/api/suppliers/{id}/`
- **DELETE** `/api/suppliers/{id}/`

---

## Clients

### **List/Create Clients**

**GET** `/api/clients/` - Listar clientes (admin/owner)

**POST** `/api/clients/` - Crear cliente

⚠️ **IMPORTANTE**: Al crear un cliente se crea automáticamente una cuenta de usuario con:
- **email**: igual al email del cliente
- **username**: igual al email del cliente
- **password**: `nurax123` (se recomienda cambiar en el primer acceso)
- **role**: `cliente`
- **name**: nombre del cliente

```json
{
  "name": "Carlos López",
  "email": "carlos@example.com",
  "company": "Tienda XYZ",
  "plan": "pro",
  "avatar_color": "#FF5733"
}
```

**Respuesta (201) - Nota que incluye usuario creado:**
```json
{
  "id": 1,
  "name": "Carlos López",
  "email": "carlos@example.com",
  "company": "Tienda XYZ",
  "plan": "pro",
  "active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "user": {
    "id": 15,
    "email": "carlos@example.com",
    "name": "Carlos López",
    "role": "cliente",
    "avatar_url": null,
    "is_active": true
  }
}
```

### **Detail/Update/Delete**

- **GET** `/api/clients/{id}/`
- **PUT** `/api/clients/{id}/` - Actualizar cliente
- **DELETE** `/api/clients/{id}/`

---

## Sales (Ventas)

### **List/Create Sales**

**GET** `/api/sales/` - Listar ventas del usuario

**Parámetros query:**
- `?status=completed` - Filtrar por estado
- `?created_at__gte=2024-01-01` - Ventas desde fecha

**POST** `/api/sales/` - Crear venta

```json
{
  "status": "completed",
  "total": "499.98",
  "customer_name": "Juan Pérez",
  "customer_phone": "555-1234",
  "amount_paid": "499.98",
  "items": [
    {
      "product": 5,
      "product_name": "iPhone 15",
      "quantity": 1,
      "unit_price": "999.99"
    }
  ]
}
```

### **Detail/Update**

- **GET** `/api/sales/{id}/` - Obtener venta con items y pagos
- **PUT** `/api/sales/{id}/` - Actualizar venta
- **PATCH** `/api/sales/{id}/` - Actualizar estado

**PATCH Body (cambiar estado):**
```json
{
  "status": "completed"
}
```

### **Cancelar Venta**

**POST** `/api/sales/{id}/cancel/` - Cancelar una venta

---

## Sale Items

### **List/Create**

**GET** `/api/sale-items/` - Listar items de venta

**POST** `/api/sale-items/` - Crear item (se hace normalmente en venta)

```json
{
  "sale": 1,
  "product": 5,
  "product_name": "iPhone 15",
  "quantity": 2,
  "unit_price": "999.99"
}
```

### **Detail/Update**

- **GET** `/api/sale-items/{id}/`
- **PUT** `/api/sale-items/{id}/`
- **DELETE** `/api/sale-items/{id}/`

---

## Sale Payments (Abonos)

### **List/Create Payments**

**GET** `/api/sale-payments/` - Listar pagos

**POST** `/api/sale-payments/` - Registrar pago/abono

```json
{
  "sale": 3,
  "amount": "250.00"
}
```

Esto:
1. Crea un SalePayment record
2. Actualiza sale.amount_paid
3. Calcula automáticamente balance_due

### **Detail**

- **GET** `/api/sale-payments/{id}/`
- **DELETE** `/api/sale-payments/{id}/` - Revertir pago

---

## Inventory Transactions (Kárdex)

### **List/Create**

**GET** `/api/inventory-transactions/` - Histórico de movimientos

**POST** `/api/inventory-transactions/` - Registrar movimiento

```json
{
  "product": 5,
  "transaction_type": "adjustment",
  "quantity": 10,
  "reason": "Conteo físico - ajuste encontrado"
}
```

**transaction_type opciones:**
- `in` - Entrada (compra a proveedor)
- `out` - Salida (venta/manual)
- `adjustment` - Ajuste de inventario
- `waste` - Merma/dañado

---

## Inventory Movements (Movimientos Detallados)

### **List/Create**

**GET** `/api/inventory-movements/` - Movimientos con costos

**POST** `/api/inventory-movements/` - Crear movimiento

```json
{
  "product": 5,
  "movement_type": "restock",
  "quantity": 50,
  "unit_cost": "450.00",
  "cash_shift": 1,
  "notes": "Reabastecimiento proveedor principal"
}
```

**movement_type opciones:**
- `sale` - Venta
- `restock` - Reabastecimiento
- `adjust` - Ajuste inventario

### **Detail/Update**

- **GET** `/api/inventory-movements/{id}/`
- **PATCH** `/api/inventory-movements/{id}/` - Actualizar notas

---

## Expenses (Gastos)

### **List/Create**

**GET** `/api/expenses/` - Listar gastos

**POST** `/api/expenses/` - Registrar gasto

```json
{
  "amount": "150.00",
  "category": "servicios",
  "description": "Pago factura de internet",
  "supplier": 2,
  "cash_shift": 1,
  "receipt_url": "https://cloudinary.com/receipt.pdf"
}
```

**category opciones:**
- `servicios` - Servicios (Luz, Agua, Internet)
- `nomina` - Nómina/Sueldos
- `proveedores` - Pago a Proveedores
- `inventario` - Reabastecimiento
- `varios` - Gastos Varios

### **Detail/Update**

- **GET** `/api/expenses/{id}/`
- **PUT** `/api/expenses/{id}/`
- **DELETE** `/api/expenses/{id}/`

---

## Cash Shifts (Cortes de Caja)

### **List/Create**

**GET** `/api/cash-shifts/` - Listar cortes

**POST** `/api/cash-shifts/` - Abrir turno

```json
{
  "starting_cash": "500.00"
}
```

### **Detail**

**GET** `/api/cash-shifts/{id}/` - Ver detalle turno (incluye movimientos y gastos)

### **Cerrar Turno**

**POST** `/api/cash-shifts/{id}/close/`

```json
{
  "actual_cash": "645.50"
}
```

Esto calcula automáticamente:
- `expected_cash` = starting_cash + ventas - gastos
- `difference` = actual_cash - expected_cash

---

## Store Profile

### **Get/Update**

**GET** `/api/store-profile/` - Obtener configuración tienda actual

**PUT** `/api/store-profile/` - Actualizar configuración

```json
{
  "store_name": "Mi Tienda Tech",
  "currency_symbol": "$",
  "address": "Calle 5 #123",
  "phone": "555-1234",
  "ticket_message": "¡Gracias por su compra!",
  "company_name": "Tech Store Inc",
  "ticket_name": "TIENDA TECH"
}
```

### **Marcar Setup Completo**

**PATCH** `/api/store-profile/`

```json
{
  "is_first_setup_completed": true
}
```

---

## Active Session Cart

### **Get/Update**

**GET** `/api/active-session-cart/` - Obtener carrito sesión actual

**PUT** `/api/active-session-cart/`

```json
{
  "cart_data": [
    {
      "product_id": 5,
      "product_name": "iPhone 15",
      "quantity": 2,
      "unit_price": "999.99"
    }
  ]
}
```

---

## Documentación Interactiva

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
