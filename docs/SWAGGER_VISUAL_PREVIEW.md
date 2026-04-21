# 📊 Vista Previa Visual - Swagger UI

## Cómo Se Vé en la Interfaz de Swagger

Después de ejecutar los cambios, cuando abras `http://localhost:8000/api/docs/`, verás esta estructura:

---

## 🖥️ Interfaz de Swagger (Antes vs Después)

### ANTES (sin tags)

```
Swagger UI
│
├── Default
│   ├── GET /api/v1/products/products/
│   ├── POST /api/v1/products/products/
│   ├── GET /api/v1/accounts/stores/
│   ├── POST /api/v1/accounts/stores/
│   ├── GET /api/v1/sales/sales/
│   │   ... (todos mezclados sin organización)
```

**Problema:** Los endpoints aparecen en orden alfabético sin agrupar por entidad.

---

### DESPUÉS (con tags)

```
Swagger UI
│
├── 🔐 Autenticación (3)
│   ├── POST /api/auth/login/
│   │   └── "Body: {email, password}"
│   ├── POST /api/auth/refresh/
│   │   └── "Refresh token en cookies"
│   └── POST /api/auth/logout/
│       └── "Clear cookies"
│
├── 👤 Usuarios (6)
│   ├── GET /api/v1/accounts/users/me/
│   │   └── "Obtiene o actualiza perfil"
│   ├── PATCH /api/v1/accounts/users/me/
│   ├── PATCH /api/v1/accounts/users/change-password/
│   ├── POST /api/v1/accounts/users/register/
│   ├── GET /api/v1/accounts/users/software-clients/
│   └── ...más
│
├── 🏪 Tiendas (8)
│   ├── GET /api/v1/accounts/stores/
│   │   └── "Listar tiendas del usuario"
│   ├── POST /api/v1/accounts/stores/
│   │   └── "Crear tienda"
│   ├── GET /api/v1/accounts/stores/{id}/
│   ├── PUT /api/v1/accounts/stores/{id}/
│   ├── PATCH /api/v1/accounts/stores/{id}/
│   ├── DELETE /api/v1/accounts/stores/{id}/
│   ├── POST /api/v1/accounts/stores/create-with-owner/
│   │   └── "Crear tienda con propietario"
│   └── GET /api/v1/accounts/stores/{id}/memberships/
│
├── 👥 Membresías (6)
│   ├── GET /api/v1/accounts/memberships/
│   ├── POST /api/v1/accounts/memberships/
│   └── ...más CRUD
│
├── 👥 Clientes (6)
│   ├── GET /api/v1/accounts/clients/
│   ├── POST /api/v1/accounts/clients/
│   └── ...más CRUD
│
├── 🎯 Wizard de Configuración (1)
│   └── POST /api/v1/onboarding/wizard/
│       └── "Crea tienda + categorías + proveedor en una llamada"
│
├── 📦 Productos (8)
│   ├── GET /api/v1/products/products/
│   │   └── "Listar productos con filtros (store, category, supplier)"
│   ├── POST /api/v1/products/products/
│   │   └── "Crear producto"
│   ├── GET /api/v1/products/products/{id}/
│   ├── PUT /api/v1/products/products/{id}/
│   ├── PATCH /api/v1/products/products/{id}/
│   ├── DELETE /api/v1/products/products/{id}/
│   ├── GET /api/v1/products/products/low_stock/
│   │   └── "Productos con stock < 10 (configurable)"
│   └── GET /api/v1/products/products/out_of_stock/
│       └── "Productos con stock = 0"
│
├── 📂 Categorías (6)
│   ├── GET /api/v1/products/categories/
│   ├── POST /api/v1/products/categories/
│   └── ...más CRUD
│
├── 🤝 Proveedores (6)
│   ├── GET /api/v1/products/suppliers/
│   ├── POST /api/v1/products/suppliers/
│   └── ...más CRUD
│
├── 📦 Empaques de Producto (6)
│   ├── GET /api/v1/products/packagings/
│   └── ...más CRUD
│
├── 🏷️ Códigos de Producto (6)
│   ├── GET /api/v1/products/codes/
│   └── ...más CRUD (QR, EAN13, etc.)
│
├── 💰 Ventas (7)
│   ├── GET /api/v1/sales/sales/
│   │   └── "Listar ventas"
│   ├── POST /api/v1/sales/sales/
│   ├── GET /api/v1/sales/sales/{id}/
│   ├── PUT /api/v1/sales/sales/{id}/
│   ├── PATCH /api/v1/sales/sales/{id}/
│   ├── DELETE /api/v1/sales/sales/{id}/
│   └── GET /api/v1/sales/sales/pending_payments/
│       └── "Ventas con pagos parciales (crédito)"
│
├── 📋 Items de Venta (6)
│   ├── GET /api/v1/sales/items/
│   └── ...más CRUD
│
├── 💳 Pagos (6)
│   ├── GET /api/v1/sales/payments/
│   └── ...más CRUD
│
├── 📊 Inventario (2)
│   ├── GET /api/v1/inventory/movements/
│   │   └── "Kárdex completo (solo lectura)"
│   └── GET /api/v1/inventory/movements/{id}/
│
├── 🏪 Turnos de Caja (9)
│   ├── GET /api/v1/expenses/cash-shifts/
│   ├── POST /api/v1/expenses/cash-shifts/
│   ├── GET /api/v1/expenses/cash-shifts/{id}/
│   ├── PUT /api/v1/expenses/cash-shifts/{id}/
│   ├── PATCH /api/v1/expenses/cash-shifts/{id}/
│   ├── DELETE /api/v1/expenses/cash-shifts/{id}/
│   ├── POST /api/v1/expenses/cash-shifts/open/
│   │   └── "Abrir turno (legacy compatibility)"
│   ├── GET /api/v1/expenses/cash-shifts/current_open/
│   │   └── "Obtener turno abierto actual"
│   └── POST /api/v1/expenses/cash-shifts/{id}/close/
│       └── "Cerrar turno"
│
├── 💵 Movimientos de Caja (6)
│   ├── GET /api/v1/expenses/cash-movements/
│   └── ...más CRUD
│
├── 📂 Categorías de Gasto (6)
│   ├── GET /api/v1/expenses/expense-categories/
│   └── ...más CRUD
│
├── 💸 Gastos (6)
│   ├── GET /api/v1/expenses/expenses/
│   └── ...más CRUD
│
├── 🛒 Órdenes de Compra (7)
│   ├── GET /api/v1/expenses/purchase-orders/
│   ├── POST /api/v1/expenses/purchase-orders/
│   ├── GET /api/v1/expenses/purchase-orders/{id}/
│   ├── PUT /api/v1/expenses/purchase-orders/{id}/
│   ├── PATCH /api/v1/expenses/purchase-orders/{id}/
│   ├── DELETE /api/v1/expenses/purchase-orders/{id}/
│   └── POST /api/v1/expenses/purchase-orders/{id}/mark_received/
│       └── "Marcar como recibida (actualiza inventario)"
│
└── 🛍️ Carritos (9)
    ├── GET /api/v1/carts/carts/
    ├── POST /api/v1/carts/carts/
    ├── GET /api/v1/carts/carts/{id}/
    ├── PUT /api/v1/carts/carts/{id}/
    ├── PATCH /api/v1/carts/carts/{id}/
    ├── DELETE /api/v1/carts/carts/{id}/
    ├── POST /api/v1/carts/carts/{id}/add_item/
    │   └── "Agregar item (suma cantidad si existe)"
    ├── POST /api/v1/carts/carts/{id}/remove_item/
    │   └── "Remover item del carrito"
    └── POST /api/v1/carts/carts/{id}/clear/
        └── "Vaciar todos los items"
```

---

## 🎨 Colores en Swagger (por HTTP Method)

```
🟦 GET    - Azul (lectura)
🟩 POST   - Verde (crear)
🟨 PUT    - Naranja (reemplazar)
🟨 PATCH  - Naranja claro (actualizar parcial)
🟥 DELETE - Rojo (eliminar)
```

---

## 💡 Ejemplo de Interacción en Swagger

### Paso 1: Seleccionar una categoría
```
El usuario hace clic en "📦 Productos"
→ La sección se expande
→ Se muestran todos los 8 endpoints
```

### Paso 2: Abrir un endpoint
```
El usuario hace clic en "GET /api/v1/products/products/"
→ Se muestra:
  - Descripción: "Listar productos"
  - Parámetros: store_id, category_id, supplier_id (filtros)
  - Botón: "Try it out"
```

### Paso 3: Probar el endpoint
```
El usuario hace clic en "Try it out"
→ Puede escribir valores en los parámetros
→ Hace clic en "Execute"
→ Ve la respuesta (status 200, JSON, etc.)
```

---

## 📱 Responsive Design

Swagger se ve bien en:
- ✅ Desktop (completa)
- ✅ Tablet (ajustada)
- ✅ Mobile (menú colapsable)

---

## 🔍 Características Disponibles en Swagger

1. **Búsqueda:** Campo de búsqueda en la parte superior
2. **Autenticación:** Botón "Authorize" para enviar token
3. **Ejemplos:** Cada endpoint muestra request/response de ejemplo
4. **Validación:** Muestra errores antes de enviar
5. **Descargar:** Opción para descargar el esquema OpenAPI (JSON/YAML)
6. **Copiar cURL:** Código cURL listo para pegar en terminal

---

## 📊 Estadísticas de la Documentación

| Métrica | Valor |
|---------|-------|
| Total de Tags | 21 |
| Total de Endpoints | ~140 |
| Endpoints más activos | Turnos de Caja (9), Carritos (9) |
| Endpoints más simples | Inventario (2) |
| Promedio endpoints/tag | 6-7 |

---

## 🚀 Cómo Acceder

### Desarrollo Local

```bash
1. Levanta el servidor
   python manage.py runserver

2. Abre el navegador
   http://localhost:8000/api/docs/

3. ¡Listo! Puedes interactuar con todos los endpoints
```

### Producción (Render)

```
URL: https://<tu-backend>.onrender.com/api/docs/
```

---

## 🔐 Nota de Seguridad

**En producción:**
- La documentación Swagger puede estar deshabilitada si lo prefieres
- Setting: `SERVE_INCLUDE_SCHEMA = False` desactiva el UI
- Pero el esquema JSON sigue disponible en `/api/schema/`

**En desarrollo:**
- Está habilitado por defecto para facilitar debugging

---

## 📚 Próximas Mejoras Opcionales

1. **Descripções Detalladas**
   - Agregar `description="..."` a cada endpoint
   - Ejemplo: "Crea un producto en la tienda del usuario"

2. **Ejemplos de Response**
   - Mostrar ejemplos de data real
   - Código de error con descripción

3. **Documentación de Parámetros**
   - Describir cada parámetro (ej: "ID de la tienda en UUID")
   - Valores requeridos vs opcionales

4. **Validación de Reglas**
   - Mostrar restricciones (ej: "stock > 0")
   - Patrones de validación

5. **Enlaces Cruzados**
   - Link desde Pagos → Ventas (relación)
   - Link desde Items → Productos

