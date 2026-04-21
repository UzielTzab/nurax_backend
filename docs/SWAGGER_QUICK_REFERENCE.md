# 🏷️ Referencia Rápida - Tags en Swagger

## Vista Rápida de Todos los Tags

```
┌─ 🔐 Autenticación (3)
│  ├─ Login
│  ├─ Refresh Token
│  └─ Logout
│
├─ 👤 Usuarios (6)
│  ├─ Perfil
│  ├─ Cambiar Contraseña
│  ├─ Registro
│  └─ Gestión de Software Clients
│
├─ 🏪 Tiendas (8)
│  ├─ CRUD de Tiendas
│  ├─ Crear con Propietario
│  └─ Gestionar Membresías
│
├─ 👥 Membresías (6)
│  └─ Control de Acceso
│
├─ 👥 Clientes (6)
│  └─ CRUD Básico
│
├─ 🎯 Wizard de Configuración (1)
│  └─ Setup Inicial
│
├─ 📦 Productos (8)
│  ├─ CRUD de Productos
│  ├─ Stock Bajo
│  └─ Sin Stock
│
├─ 📂 Categorías (6)
│  └─ CRUD Básico
│
├─ 🤝 Proveedores (6)
│  └─ CRUD Básico
│
├─ 📦 Empaques de Producto (6)
│  └─ CRUD Básico
│
├─ 🏷️ Códigos de Producto (6)
│  └─ QR, EAN13, etc.
│
├─ 💰 Ventas (7)
│  ├─ CRUD de Ventas
│  └─ Pagos Pendientes
│
├─ 📋 Items de Venta (6)
│  └─ CRUD Básico
│
├─ 💳 Pagos (6)
│  └─ CRUD Básico
│
├─ 📊 Inventario (2)
│  └─ Kárdex (Solo Lectura)
│
├─ 🏪 Turnos de Caja (9)
│  ├─ CRUD de Turnos
│  ├─ Abrir Turno
│  ├─ Obtener Actual
│  └─ Cerrar Turno
│
├─ 💵 Movimientos de Caja (6)
│  └─ CRUD Básico
│
├─ 📂 Categorías de Gasto (6)
│  └─ CRUD Básico
│
├─ 💸 Gastos (6)
│  └─ CRUD Básico
│
├─ 🛒 Órdenes de Compra (7)
│  ├─ CRUD de Órdenes
│  └─ Marcar Recibida
│
└─ 🛍️ Carritos (9)
   ├─ CRUD de Carritos
   ├─ Agregar Item
   ├─ Remover Item
   └─ Limpiar Carrito
```

---

## Tabla Rápida

| # | Tag | Qty | Principales |
|---|-----|-----|------------|
| 1 | 🔐 Autenticación | 3 | Login, Refresh, Logout |
| 2 | 👤 Usuarios | 6 | Perfil, Contraseña, Registro |
| 3 | 🏪 Tiendas | 8 | CRUD, Create-with-owner |
| 4 | 👥 Membresías | 6 | Control de acceso |
| 5 | 👥 Clientes | 6 | CRUD básico |
| 6 | 🎯 Wizard | 1 | Setup inicial |
| 7 | 📦 Productos | 8 | CRUD, Low stock |
| 8 | 📂 Categorías | 6 | CRUD básico |
| 9 | 🤝 Proveedores | 6 | CRUD básico |
| 10 | 📦 Empaques | 6 | CRUD básico |
| 11 | 🏷️ Códigos | 6 | QR, EAN13 |
| 12 | 💰 Ventas | 7 | CRUD, Pending |
| 13 | 📋 Items Venta | 6 | CRUD básico |
| 14 | 💳 Pagos | 6 | CRUD básico |
| 15 | 📊 Inventario | 2 | Kárdex (lectura) |
| 16 | 🏪 Turnos Caja | 9 | CRUD, Open, Close |
| 17 | 💵 Mov. Caja | 6 | CRUD básico |
| 18 | 📂 Cat. Gasto | 6 | CRUD básico |
| 19 | 💸 Gastos | 6 | CRUD básico |
| 20 | 🛒 Órdenes Compra | 7 | CRUD, Mark received |
| 21 | 🛍️ Carritos | 9 | CRUD, Add/Remove |
| **TOTAL** | | **~140** | |

---

## 🎨 Colores por Operación (HTTP Methods)

| Método | Color | Significado |
|--------|-------|------------|
| GET | 🟦 Azul | Lectura |
| POST | 🟩 Verde | Crear |
| PUT | 🟨 Naranja | Reemplazar |
| PATCH | 🟨 Naranja claro | Actualizar parcial |
| DELETE | 🟥 Rojo | Eliminar |

---

## ⚡ Atajos Útiles en Swagger

| Acción | Cómo |
|--------|------|
| **Expandir todas** | Busca botón en la UI (⬆️ Expand all) |
| **Colapsar todas** | Busca botón en la UI (⬇️ Collapse all) |
| **Buscar endpoint** | Usa la barra de búsqueda (arriba) |
| **Probar endpoint** | Click "Try it out" en el endpoint |
| **Ver modelo** | Scroll hasta "Model" debajo del endpoint |
| **Descargar esquema** | Button "Download" (YAML/JSON) |
| **Autorizar** | Click botón "Authorize" (agregar token) |

---

## 🔗 Navegación Sugerida

### Si buscas **Productos:**
→ Abre sección "Productos"
→ También verás "Categorías", "Proveedores", "Empaques", "Códigos"

### Si buscas **Ventas:**
→ Abre sección "Ventas"
→ También verás "Items de Venta" y "Pagos"

### Si buscas **Control de Tienda:**
→ Abre sección "Tiendas"
→ También verás "Membresías" y "Usuarios"

### Si buscas **Caja:**
→ Abre sección "Turnos de Caja"
→ También verás "Movimientos de Caja", "Gastos", "Órdenes Compra"

### Si buscas **Carrito:**
→ Abre sección "Carritos"
→ Desde allí vincula a "Productos"

---

## 📱 URLs Directas

### Desarrollo
```
http://localhost:8000/api/docs/
```

### Producción (Render)
```
https://<tu-backend>.onrender.com/api/docs/
```

### Esquema JSON (descarga)
```
http://localhost:8000/api/schema/
```

---

## 🚀 Flujo Típico de Usuario

```
1. Abre Swagger
   ↓
2. Lee "Autenticación" y obtiene token
   ↓
3. Abre sección "Usuarios" → GET /users/me/
   ↓
4. Abre sección "Tiendas" → GET /stores/ (para ver tiendas del usuario)
   ↓
5. Abre sección "Productos" → GET /products/ (para listar productos)
   ↓
6. Abre sección "Carritos" → POST /carts/ (para crear carrito)
   ↓
7. Abre sección "Ventas" → POST /sales/ (para crear venta)
   ↓
8. Abre sección "Pagos" → POST /payments/ (para registrar pago)
```

---

## ✨ Tips Profesionales

### Tip 1: Favoritos
Guarda los endpoints que usas frecuentemente en marcadores del navegador:
```
http://localhost:8000/api/docs#/Productos
http://localhost:8000/api/docs#/Ventas
```

### Tip 2: cURL desde Swagger
Haz clic en "Try it out" → "Execute"
→ Copia el comando cURL generado
→ Úsalo en terminal

### Tip 3: Postman
Importa el esquema OpenAPI (JSON) en Postman:
1. Descarga el esquema: `http://localhost:8000/api/schema/`
2. En Postman: File → Import → Paste raw text
3. Tendrás todos los endpoints configurados

### Tip 4: Búsqueda Rápida
Usa Ctrl+F (en Swagger) para buscar:
- `"productos"` → todos los endpoints de productos
- `"GET"` → todos los GETs
- `"POST"` → todos los POSTs

---

## 🔒 Notas de Seguridad

⚠️ **En Producción:**
- Los endpoints documentados pueden ser deshabilitados
- Setting: `SERVE_INCLUDE_SCHEMA = False`
- El esquema JSON aún estará disponible en `/api/schema/`

✅ **En Desarrollo:**
- Swagger está habilitado para facilitar debugging
- Todos los endpoints son visibles

---

## 📞 ¿Necesitas más info?

Consulta los documentos completos:
- `SWAGGER_TAGS_ORGANIZATION.md` - Listado detallado
- `SWAGGER_IMPLEMENTATION_SUMMARY.md` - Detalles técnicos
- `SWAGGER_VISUAL_PREVIEW.md` - Vista previa visual

---

**Última actualización:** Abril 2026
**Versión API:** 1.0.0

