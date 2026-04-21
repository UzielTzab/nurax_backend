# ✅ Checklist de Verificación - Swagger Tags

Usa esta checklist para validar que la implementación de tags en Swagger está completa y funcionando correctamente.

---

## 📋 Verificación de Código

### Imports agregados

- [ ] `apps/products/views.py` - Import: `from drf_spectacular.utils import extend_schema_view, extend_schema`
- [ ] `apps/accounts/views.py` - Import: `from drf_spectacular.utils import extend_schema_view, extend_schema`
- [ ] `apps/sales/views.py` - Import: `from drf_spectacular.utils import extend_schema_view, extend_schema`
- [ ] `apps/inventory/views.py` - Import: `from drf_spectacular.utils import extend_schema_view, extend_schema`
- [ ] `apps/expenses/views.py` - Import: `from drf_spectacular.utils import extend_schema_view, extend_schema`
- [ ] `apps/carts/views.py` - Import: `from drf_spectacular.utils import extend_schema_view, extend_schema`
- [ ] `utils/auth_views.py` - Import: `from drf_spectacular.utils import extend_schema`

### Decoradores en ViewSets - Products

- [ ] `CategoryViewSet` - `@extend_schema_view` con tag `"Categorías"`
- [ ] `SupplierViewSet` - `@extend_schema_view` con tag `"Proveedores"`
- [ ] `ProductViewSet` - `@extend_schema_view` con tag `"Productos"` (incluye low_stock, out_of_stock)
- [ ] `ProductPackagingViewSet` - `@extend_schema_view` con tag `"Empaques de Producto"`
- [ ] `ProductCodeViewSet` - `@extend_schema_view` con tag `"Códigos de Producto"`

### Decoradores en ViewSets - Accounts

- [ ] `UserViewSet` - `@extend_schema_view` con tag `"Usuarios"` (incluye me, change_password, register, software_clients)
- [ ] `StoreViewSet` - `@extend_schema_view` con tag `"Tiendas"` (incluye create_with_owner, memberships)
- [ ] `OnboardingWizardView` - `@extend_schema` con tag `"Wizard de Configuración"`
- [ ] `StoreMembershipViewSet` - `@extend_schema_view` con tag `"Membresías"`
- [ ] `ClientViewSet` - `@extend_schema_view` con tag `"Clientes"`

### Decoradores en ViewSets - Sales

- [ ] `SaleViewSet` - `@extend_schema_view` con tag `"Ventas"` (incluye pending_payments)
- [ ] `SaleItemViewSet` - `@extend_schema_view` con tag `"Items de Venta"`
- [ ] `SalePaymentViewSet` - `@extend_schema_view` con tag `"Pagos"`

### Decoradores en ViewSets - Inventory

- [ ] `InventoryMovementViewSet` - `@extend_schema_view` con tag `"Inventario"` (solo list, retrieve)

### Decoradores en ViewSets - Expenses

- [ ] `CashShiftViewSet` - `@extend_schema_view` con tag `"Turnos de Caja"` (incluye open, current_open, close)
- [ ] `CashMovementViewSet` - `@extend_schema_view` con tag `"Movimientos de Caja"`
- [ ] `ExpenseCategoryViewSet` - `@extend_schema_view` con tag `"Categorías de Gasto"`
- [ ] `ExpenseViewSet` - `@extend_schema_view` con tag `"Gastos"`
- [ ] `PurchaseOrderViewSet` - `@extend_schema_view` con tag `"Órdenes de Compra"` (incluye mark_received)

### Decoradores en ViewSets - Carts

- [ ] `ActiveCartViewSet` - `@extend_schema_view` con tag `"Carritos"` (incluye add_item, remove_item, clear)

### Decoradores en Auth Views

- [ ] `CustomTokenObtainPairView` - `@extend_schema` con tag `"Autenticación"`
- [ ] `CustomTokenRefreshView` - `@extend_schema` con tag `"Autenticación"`
- [ ] `LogoutView` - `@extend_schema` con tag `"Autenticación"`

### Configuración en settings.py

- [ ] `core/settings.py` - `SPECTACULAR_SETTINGS` actualizado con:
  - [ ] `'TITLE': 'Nurax API'`
  - [ ] `'DESCRIPTION': 'Documentación de la API de Nurax - Sistema de Gestión de Tiendas'`
  - [ ] `'VERSION': '1.0.0'`
  - [ ] `'SERVE_INCLUDE_SCHEMA': False`
  - [ ] `'SCHEMA_PATH_PREFIX': '/api/v1/'`
  - [ ] `'ENUM_ADD_EXPLICIT_BLANK_NULLS': False`
  - [ ] `'COERCE_DECIMAL_TO_STRING': False`

---

## 🧪 Verificación en Desarrollo

### Sintaxis Python

```bash
# En terminal (en el directorio del backend)
python -m py_compile core/settings.py
python -m py_compile apps/products/views.py
python -m py_compile apps/accounts/views.py
python -m py_compile apps/sales/views.py
python -m py_compile apps/inventory/views.py
python -m py_compile apps/expenses/views.py
python -m py_compile apps/carts/views.py
python -m py_compile utils/auth_views.py
```

**Resultado esperado:** Sin output (significa que compiló correctamente)

- [ ] Todos los archivos compilan sin errores

### Levantar el servidor

```bash
cd nurax_backend
python manage.py runserver
```

- [ ] El servidor se levanta sin errores
- [ ] No hay ImportError de `drf_spectacular`
- [ ] No hay errores de sintaxis en los ViewSets

### Acceder a Swagger

1. Abre el navegador: `http://localhost:8000/api/docs/`

- [ ] La página carga sin errores
- [ ] Ves el título "Nurax API"
- [ ] La descripción es "Documentación de la API de Nurax - Sistema de Gestión de Tiendas"

---

## 📊 Verificación Visual en Swagger

### Estructura de Tags - Autenticación

En `http://localhost:8000/api/docs/`:

- [ ] Existe una sección "Autenticación" (colapsable)
- [ ] Bajo "Autenticación":
  - [ ] POST /api/auth/login/
  - [ ] POST /api/auth/refresh/
  - [ ] POST /api/auth/logout/

### Estructura de Tags - Usuarios

- [ ] Existe una sección "Usuarios"
- [ ] Bajo "Usuarios":
  - [ ] GET /api/v1/accounts/users/me/
  - [ ] PATCH /api/v1/accounts/users/me/
  - [ ] PATCH /api/v1/accounts/users/change-password/
  - [ ] POST /api/v1/accounts/users/register/
  - [ ] GET /api/v1/accounts/users/software-clients/
  - [ ] Más endpoints...

### Estructura de Tags - Tiendas

- [ ] Existe una sección "Tiendas"
- [ ] Bajo "Tiendas":
  - [ ] GET /api/v1/accounts/stores/
  - [ ] POST /api/v1/accounts/stores/
  - [ ] GET /api/v1/accounts/stores/{id}/
  - [ ] Más endpoints...

### Estructura de Tags - Productos

- [ ] Existe una sección "Productos"
- [ ] Bajo "Productos":
  - [ ] GET /api/v1/products/products/
  - [ ] POST /api/v1/products/products/
  - [ ] GET /api/v1/products/products/low_stock/
  - [ ] GET /api/v1/products/products/out_of_stock/
  - [ ] Más endpoints...

### Estructura de Tags - Ventas

- [ ] Existe una sección "Ventas"
- [ ] Bajo "Ventas":
  - [ ] GET /api/v1/sales/sales/
  - [ ] POST /api/v1/sales/sales/
  - [ ] GET /api/v1/sales/sales/pending_payments/
  - [ ] Más endpoints...

### Estructura de Tags - Otros módulos

- [ ] Existe sección "Categorías"
- [ ] Existe sección "Proveedores"
- [ ] Existe sección "Empaques de Producto"
- [ ] Existe sección "Códigos de Producto"
- [ ] Existe sección "Membresías"
- [ ] Existe sección "Clientes"
- [ ] Existe sección "Wizard de Configuración"
- [ ] Existe sección "Items de Venta"
- [ ] Existe sección "Pagos"
- [ ] Existe sección "Inventario"
- [ ] Existe sección "Turnos de Caja"
- [ ] Existe sección "Movimientos de Caja"
- [ ] Existe sección "Categorías de Gasto"
- [ ] Existe sección "Gastos"
- [ ] Existe sección "Órdenes de Compra"
- [ ] Existe sección "Carritos"

### Total de Tags

- [ ] Contar todas las secciones colapsables: **~21 tags**

---

## 🧪 Pruebas de Interacción

### Prueba 1: Expandir una sección

- [ ] Haz clic en "Productos"
- [ ] La sección se expande
- [ ] Se muestran todos los endpoints de productos

### Prueba 2: Ver detalles de un endpoint

- [ ] Haz clic en "GET /api/v1/products/products/"
- [ ] Se muestra:
  - [ ] Descripción (ej: "Listar productos")
  - [ ] Parámetros (store_id, category_id, supplier_id)
  - [ ] Botón "Try it out"
  - [ ] Modelo de respuesta (schema)

### Prueba 3: Probar un endpoint

- [ ] Haz clic en "Try it out" de un GET endpoint
- [ ] Se habilitan los campos para escribir parámetros
- [ ] Haz clic en "Execute"
- [ ] Ves una respuesta (status, datos, etc.)

### Prueba 4: Búsqueda

- [ ] Usa el campo de búsqueda (arriba a la izquierda)
- [ ] Busca por: "productos"
- [ ] Se muestran los endpoints relacionados

### Prueba 5: Descargar esquema

- [ ] Busca el botón "Download" (formato YAML o JSON)
- [ ] El archivo se descarga correctamente

---

## 📚 Verificación de Documentación

### Archivos nuevos creados

- [ ] `docs/SWAGGER_TAGS_ORGANIZATION.md` - Listado de tags y endpoints
- [ ] `docs/SWAGGER_IMPLEMENTATION_SUMMARY.md` - Detalles técnicos
- [ ] `docs/SWAGGER_VISUAL_PREVIEW.md` - Vista previa visual
- [ ] `docs/SWAGGER_TAGS_CHECKLIST.md` - Este archivo

### Archivo README.md actualizado

- [ ] Referencia a `SWAGGER_TAGS_ORGANIZATION.md`
- [ ] Referencia a `SWAGGER_IMPLEMENTATION_SUMMARY.md`
- [ ] Referencia a `SWAGGER_VISUAL_PREVIEW.md`
- [ ] Nueva sección en FAQs sobre Swagger

---

## 🔄 Validación de Cambios

### Git Status

```bash
git status --short
```

Deberías ver cambios en:

- [ ] `core/settings.py`
- [ ] `apps/products/views.py`
- [ ] `apps/accounts/views.py`
- [ ] `apps/sales/views.py`
- [ ] `apps/inventory/views.py`
- [ ] `apps/expenses/views.py`
- [ ] `apps/carts/views.py`
- [ ] `utils/auth_views.py`
- [ ] `docs/README.md`
- [ ] Nuevos archivos: `SWAGGER_TAGS_ORGANIZATION.md`, `SWAGGER_IMPLEMENTATION_SUMMARY.md`, `SWAGGER_VISUAL_PREVIEW.md`

### Git Diff

```bash
git diff --stat
```

Deberías ver algo como:

```
core/settings.py                                 |  4 +
apps/products/views.py                          | 30 ++
apps/accounts/views.py                          | 40 ++
apps/sales/views.py                             | 20 ++
apps/inventory/views.py                         | 10 ++
apps/expenses/views.py                          | 50 ++
apps/carts/views.py                             | 15 ++
utils/auth_views.py                             | 10 ++
docs/README.md                                  | 20 ++
docs/SWAGGER_TAGS_ORGANIZATION.md               | 300 ++
docs/SWAGGER_IMPLEMENTATION_SUMMARY.md          | 250 ++
docs/SWAGGER_VISUAL_PREVIEW.md                  | 280 ++
```

- [ ] El total de cambios es consistente

---

## 🚀 Pasos Finales

### 1. Commit de cambios (opcional)

```bash
git add .
git commit -m "feat(swagger): Agregar tags para organizar endpoints por entidad

- Implementar @extend_schema_view en todos los ViewSets
- Agregar 21 tags para agrupar ~140 endpoints
- Crear documentación visual y técnica de tags
- Actualizar settings.py con mejor configuración de drf-spectacular"
```

- [ ] Commit creado exitosamente

### 2. Push a repositorio (opcional)

```bash
git push origin <rama>
```

- [ ] Push exitoso

### 3. Validación en CI/CD (si aplica)

- [ ] Build pasa sin errores
- [ ] Tests pasan (si existen)
- [ ] No hay warnings de linting

---

## ✅ Checklist Final

- [ ] Todos los imports están en lugar
- [ ] Todos los decoradores están aplicados
- [ ] El servidor levanta sin errores
- [ ] Swagger carga correctamente
- [ ] Todos los tags aparecen en Swagger
- [ ] Los endpoints están organizados por tag
- [ ] Documentación está completa y actualizada
- [ ] Git status muestra los archivos esperados
- [ ] Los cambios se pueden hacer commit

---

## 🎉 ¡Listo!

Si marcaste todos los checkboxes, la implementación de tags en Swagger está completa y funcionando correctamente.

**Próximos pasos:**
1. Accede a `http://localhost:8000/api/docs/` para ver la nueva organización
2. Comparte la URL con tu equipo
3. Actualiza cualquier documentación externa que haga referencia a los endpoints
4. Considera agregar descripciones detalladas a los endpoints en el futuro

