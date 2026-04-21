# Documentación Swagger - Organización por Tags

## Descripción General

Se ha implementado un sistema de etiquetas (tags) en Swagger para organizar todos los endpoints de la API por entidades. Esto permite una navegación clara y agrupada en la documentación OpenAPI.

## Arquitectura

### Configuración Principal (`core/settings.py`)

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'Nurax API',
    'DESCRIPTION': 'Documentación de la API de Nurax - Sistema de Gestión de Tiendas',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/v1/',
    'ENUM_ADD_EXPLICIT_BLANK_NULLS': False,
    'COERCE_DECIMAL_TO_STRING': False,
}
```

### Implementación de Tags

Cada ViewSet y APIView incluye decoradores `@extend_schema_view` o `@extend_schema` para agrupar sus endpoints bajo un tag específico.

Ejemplo:
```python
@extend_schema_view(
    list=extend_schema(tags=["Productos"]),
    create=extend_schema(tags=["Productos"]),
    retrieve=extend_schema(tags=["Productos"]),
    # ... más acciones
)
class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de productos."""
```

---

## Tags Implementados por Módulo

### **Autenticación**
- `POST /api/auth/login/` - Login (HttpOnly cookies)
- `POST /api/auth/refresh/` - Refresh token
- `POST /api/auth/logout/` - Logout

**Archivo:** `utils/auth_views.py`

---

### **Usuarios** (`Accounts`)
- `GET /api/v1/accounts/users/me/` - Obtener perfil
- `PATCH /api/v1/accounts/users/me/` - Actualizar perfil
- `PATCH /api/v1/accounts/users/change-password/` - Cambiar contraseña
- `POST /api/v1/accounts/users/register/` - Registro
- `GET /api/v1/accounts/users/software-clients/` - Listar clientes del software
- `PATCH /api/v1/accounts/users/software-clients/{id}/toggle-active/` - Activar/desactivar cliente
- `DELETE /api/v1/accounts/users/software-clients/{id}/` - Eliminar cliente

**Archivo:** `apps/accounts/views.py`

---

### **Tiendas** (`Accounts`)
- `GET /api/v1/accounts/stores/` - Listar tiendas
- `POST /api/v1/accounts/stores/` - Crear tienda
- `GET /api/v1/accounts/stores/{id}/` - Obtener tienda
- `PUT /api/v1/accounts/stores/{id}/` - Actualizar tienda
- `PATCH /api/v1/accounts/stores/{id}/` - Actualización parcial
- `DELETE /api/v1/accounts/stores/{id}/` - Eliminar tienda
- `POST /api/v1/accounts/stores/create-with-owner/` - Crear tienda con propietario
- `GET /api/v1/accounts/stores/{id}/memberships/` - Obtener membresías de tienda

**Archivo:** `apps/accounts/views.py`

---

### **Membresías**
- `GET /api/v1/accounts/memberships/` - Listar membresías
- `POST /api/v1/accounts/memberships/` - Crear membresía
- `GET /api/v1/accounts/memberships/{id}/` - Obtener membresía
- `PUT /api/v1/accounts/memberships/{id}/` - Actualizar membresía
- `PATCH /api/v1/accounts/memberships/{id}/` - Actualización parcial
- `DELETE /api/v1/accounts/memberships/{id}/` - Eliminar membresía

**Archivo:** `apps/accounts/views.py`

---

### **Clientes**
- `GET /api/v1/accounts/clients/` - Listar clientes
- `POST /api/v1/accounts/clients/` - Crear cliente
- `GET /api/v1/accounts/clients/{id}/` - Obtener cliente
- `PUT /api/v1/accounts/clients/{id}/` - Actualizar cliente
- `PATCH /api/v1/accounts/clients/{id}/` - Actualización parcial
- `DELETE /api/v1/accounts/clients/{id}/` - Eliminar cliente

**Archivo:** `apps/accounts/views.py`

---

### **Wizard de Configuración**
- `POST /api/v1/onboarding/wizard/` - Ejecutar wizard (crea tienda + categorías + proveedor)

**Archivo:** `apps/accounts/views.py`

---

### **Productos**
- `GET /api/v1/products/products/` - Listar productos
- `POST /api/v1/products/products/` - Crear producto
- `GET /api/v1/products/products/{id}/` - Obtener producto
- `PUT /api/v1/products/products/{id}/` - Actualizar producto
- `PATCH /api/v1/products/products/{id}/` - Actualización parcial
- `DELETE /api/v1/products/products/{id}/` - Eliminar producto
- `GET /api/v1/products/products/low_stock/` - Productos con stock bajo
- `GET /api/v1/products/products/out_of_stock/` - Productos sin stock

**Archivo:** `apps/products/views.py`

---

### **Categorías**
- `GET /api/v1/products/categories/` - Listar categorías
- `POST /api/v1/products/categories/` - Crear categoría
- `GET /api/v1/products/categories/{id}/` - Obtener categoría
- `PUT /api/v1/products/categories/{id}/` - Actualizar categoría
- `PATCH /api/v1/products/categories/{id}/` - Actualización parcial
- `DELETE /api/v1/products/categories/{id}/` - Eliminar categoría

**Archivo:** `apps/products/views.py`

---

### **Proveedores**
- `GET /api/v1/products/suppliers/` - Listar proveedores
- `POST /api/v1/products/suppliers/` - Crear proveedor
- `GET /api/v1/products/suppliers/{id}/` - Obtener proveedor
- `PUT /api/v1/products/suppliers/{id}/` - Actualizar proveedor
- `PATCH /api/v1/products/suppliers/{id}/` - Actualización parcial
- `DELETE /api/v1/products/suppliers/{id}/` - Eliminar proveedor

**Archivo:** `apps/products/views.py`

---

### **Empaques de Producto**
- `GET /api/v1/products/packagings/` - Listar empaques
- `POST /api/v1/products/packagings/` - Crear empaque
- `GET /api/v1/products/packagings/{id}/` - Obtener empaque
- `PUT /api/v1/products/packagings/{id}/` - Actualizar empaque
- `PATCH /api/v1/products/packagings/{id}/` - Actualización parcial
- `DELETE /api/v1/products/packagings/{id}/` - Eliminar empaque

**Archivo:** `apps/products/views.py`

---

### **Códigos de Producto** (QR, EAN13, etc.)
- `GET /api/v1/products/codes/` - Listar códigos
- `POST /api/v1/products/codes/` - Crear código
- `GET /api/v1/products/codes/{id}/` - Obtener código
- `PUT /api/v1/products/codes/{id}/` - Actualizar código
- `PATCH /api/v1/products/codes/{id}/` - Actualización parcial
- `DELETE /api/v1/products/codes/{id}/` - Eliminar código

**Archivo:** `apps/products/views.py`

---

### **Ventas**
- `GET /api/v1/sales/sales/` - Listar ventas
- `POST /api/v1/sales/sales/` - Crear venta
- `GET /api/v1/sales/sales/{id}/` - Obtener venta
- `PUT /api/v1/sales/sales/{id}/` - Actualizar venta
- `PATCH /api/v1/sales/sales/{id}/` - Actualización parcial
- `DELETE /api/v1/sales/sales/{id}/` - Eliminar venta
- `GET /api/v1/sales/sales/pending_payments/` - Ventas con pagos pendientes

**Archivo:** `apps/sales/views.py`

---

### **Items de Venta**
- `GET /api/v1/sales/items/` - Listar items
- `POST /api/v1/sales/items/` - Crear item
- `GET /api/v1/sales/items/{id}/` - Obtener item
- `PUT /api/v1/sales/items/{id}/` - Actualizar item
- `PATCH /api/v1/sales/items/{id}/` - Actualización parcial
- `DELETE /api/v1/sales/items/{id}/` - Eliminar item

**Archivo:** `apps/sales/views.py`

---

### **Pagos**
- `GET /api/v1/sales/payments/` - Listar pagos
- `POST /api/v1/sales/payments/` - Crear pago
- `GET /api/v1/sales/payments/{id}/` - Obtener pago
- `PUT /api/v1/sales/payments/{id}/` - Actualizar pago
- `PATCH /api/v1/sales/payments/{id}/` - Actualización parcial
- `DELETE /api/v1/sales/payments/{id}/` - Eliminar pago

**Archivo:** `apps/sales/views.py`

---

### **Inventario**
- `GET /api/v1/inventory/movements/` - Listar movimientos (Kárdex)
- `GET /api/v1/inventory/movements/{id}/` - Obtener movimiento

**Archivo:** `apps/inventory/views.py`

---

### **Turnos de Caja**
- `GET /api/v1/expenses/cash-shifts/` - Listar turnos
- `POST /api/v1/expenses/cash-shifts/` - Crear turno
- `GET /api/v1/expenses/cash-shifts/{id}/` - Obtener turno
- `PUT /api/v1/expenses/cash-shifts/{id}/` - Actualizar turno
- `PATCH /api/v1/expenses/cash-shifts/{id}/` - Actualización parcial
- `DELETE /api/v1/expenses/cash-shifts/{id}/` - Eliminar turno
- `POST /api/v1/expenses/cash-shifts/open/` - Abrir turno (legacy compatibility)
- `GET /api/v1/expenses/cash-shifts/current_open/` - Obtener turno abierto actual
- `POST /api/v1/expenses/cash-shifts/{id}/close/` - Cerrar turno

**Archivo:** `apps/expenses/views.py`

---

### **Movimientos de Caja**
- `GET /api/v1/expenses/cash-movements/` - Listar movimientos
- `POST /api/v1/expenses/cash-movements/` - Crear movimiento
- `GET /api/v1/expenses/cash-movements/{id}/` - Obtener movimiento
- `PUT /api/v1/expenses/cash-movements/{id}/` - Actualizar movimiento
- `PATCH /api/v1/expenses/cash-movements/{id}/` - Actualización parcial
- `DELETE /api/v1/expenses/cash-movements/{id}/` - Eliminar movimiento

**Archivo:** `apps/expenses/views.py`

---

### **Categorías de Gasto**
- `GET /api/v1/expenses/expense-categories/` - Listar categorías
- `POST /api/v1/expenses/expense-categories/` - Crear categoría
- `GET /api/v1/expenses/expense-categories/{id}/` - Obtener categoría
- `PUT /api/v1/expenses/expense-categories/{id}/` - Actualizar categoría
- `PATCH /api/v1/expenses/expense-categories/{id}/` - Actualización parcial
- `DELETE /api/v1/expenses/expense-categories/{id}/` - Eliminar categoría

**Archivo:** `apps/expenses/views.py`

---

### **Gastos**
- `GET /api/v1/expenses/expenses/` - Listar gastos
- `POST /api/v1/expenses/expenses/` - Crear gasto
- `GET /api/v1/expenses/expenses/{id}/` - Obtener gasto
- `PUT /api/v1/expenses/expenses/{id}/` - Actualizar gasto
- `PATCH /api/v1/expenses/expenses/{id}/` - Actualización parcial
- `DELETE /api/v1/expenses/expenses/{id}/` - Eliminar gasto

**Archivo:** `apps/expenses/views.py`

---

### **Órdenes de Compra**
- `GET /api/v1/expenses/purchase-orders/` - Listar órdenes
- `POST /api/v1/expenses/purchase-orders/` - Crear orden
- `GET /api/v1/expenses/purchase-orders/{id}/` - Obtener orden
- `PUT /api/v1/expenses/purchase-orders/{id}/` - Actualizar orden
- `PATCH /api/v1/expenses/purchase-orders/{id}/` - Actualización parcial
- `DELETE /api/v1/expenses/purchase-orders/{id}/` - Eliminar orden
- `POST /api/v1/expenses/purchase-orders/{id}/mark_received/` - Marcar como recibida

**Archivo:** `apps/expenses/views.py`

---

### **Carritos**
- `GET /api/v1/carts/carts/` - Listar carritos
- `POST /api/v1/carts/carts/` - Crear carrito
- `GET /api/v1/carts/carts/{id}/` - Obtener carrito
- `PUT /api/v1/carts/carts/{id}/` - Actualizar carrito
- `PATCH /api/v1/carts/carts/{id}/` - Actualización parcial
- `DELETE /api/v1/carts/carts/{id}/` - Eliminar carrito
- `POST /api/v1/carts/carts/{id}/add_item/` - Agregar item al carrito
- `POST /api/v1/carts/carts/{id}/remove_item/` - Remover item del carrito
- `POST /api/v1/carts/carts/{id}/clear/` - Limpiar carrito

**Archivo:** `apps/carts/views.py`

---

## Verificación en Swagger

1. **Acceder a:** `http://localhost:8000/api/docs/`

2. **Validar que cada sección muestre:**
   - ✅ Título en grande (ej: "Productos", "Ventas", "Usuarios")
   - ✅ Todos los endpoints agrupados bajo el título correspondiente
   - ✅ Las operaciones (GET, POST, PUT, PATCH, DELETE) visibles

3. **Estructura esperada:**

```
Swagger/OpenAPI UI
├── Autenticación
│   ├── POST /api/auth/login/
│   ├── POST /api/auth/refresh/
│   └── POST /api/auth/logout/
├── Usuarios
│   ├── GET /api/v1/accounts/users/me/
│   ├── PATCH /api/v1/accounts/users/me/
│   ├── PATCH /api/v1/accounts/users/change-password/
│   └── ... más endpoints
├── Tiendas
│   ├── GET /api/v1/accounts/stores/
│   ├── POST /api/v1/accounts/stores/
│   └── ... más endpoints
├── Productos
│   ├── GET /api/v1/products/products/
│   ├── POST /api/v1/products/products/
│   └── ... más endpoints
└── ... más módulos
```

---

## Archivos Modificados

### Backend

1. **`core/settings.py`**
   - Actualización de `SPECTACULAR_SETTINGS`
   - Agregar configuración de esquema

2. **`apps/products/views.py`**
   - Importar `extend_schema_view`, `extend_schema` de drf_spectacular
   - Agregar decoradores a: `CategoryViewSet`, `SupplierViewSet`, `ProductViewSet`, `ProductPackagingViewSet`, `ProductCodeViewSet`

3. **`apps/accounts/views.py`**
   - Importar decoradores drf_spectacular
   - Agregar tags a: `UserViewSet`, `StoreViewSet`, `OnboardingWizardView`, `StoreMembershipViewSet`, `ClientViewSet`

4. **`apps/sales/views.py`**
   - Importar decoradores drf_spectacular
   - Agregar tags a: `SaleViewSet`, `SaleItemViewSet`, `SalePaymentViewSet`

5. **`apps/inventory/views.py`**
   - Importar decoradores drf_spectacular
   - Agregar tags a: `InventoryMovementViewSet`

6. **`apps/expenses/views.py`**
   - Importar decoradores drf_spectacular
   - Agregar tags a: `CashShiftViewSet`, `CashMovementViewSet`, `ExpenseCategoryViewSet`, `ExpenseViewSet`, `PurchaseOrderViewSet`

7. **`apps/carts/views.py`**
   - Importar decoradores drf_spectacular
   - Agregar tags a: `ActiveCartViewSet`

8. **`utils/auth_views.py`**
   - Importar decoradores drf_spectacular
   - Agregar tags a: `CustomTokenObtainPairView`, `CustomTokenRefreshView`, `LogoutView`

---

## Próximos Pasos

1. **Levantar el servidor Django**
   ```bash
   python manage.py runserver
   ```

2. **Acceder a Swagger**
   - Abre: `http://localhost:8000/api/docs/`

3. **Validar la organización**
   - Navega por cada sección
   - Confirma que todos los endpoints aparezcan bajo el tag correcto

4. **Documentar cambios** (opcional)
   - Agregar descripción de endpoints si es necesario
   - Usar `@extend_schema(description="...")` para detalles adicionales

---

## Notas Técnicas

- **Tags:** Son simplemente etiquetas que agrupan endpoints en la UI de Swagger
- **No afecta funcionamiento:** Los tags son solo para documentación/organización
- **Escalable:** Fácil agregar nuevos tags a nuevos endpoints en el futuro
- **Consistencia:** Mantén los nombres de tags consistentes (ej: "Productos" siempre en singular)

