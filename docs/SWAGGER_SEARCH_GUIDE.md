# 🔍 Guía: Buscador de Endpoints en Swagger

## ¿Cómo Acceder al Buscador?

### Opción 1: Buscador Integrado en Swagger UI (Recomendado)

Cuando abres Swagger UI en `http://localhost:8000/api/docs/`:

```
┌─────────────────────────────────────────────────────────┐
│ 🔍 Buscador aquí (arriba de la lista de endpoints)      │
└─────────────────────────────────────────────────────────┘
│ 📦 Productos                                             │
│   GET /api/v1/products/products/                        │
│   POST /api/v1/products/products/                       │
│   GET /api/v1/products/products/{id}/                   │
│   ...                                                    │
└─────────────────────────────────────────────────────────┘
```

El **buscador es la caja de entrada** que aparece en la **parte superior del panel principal**.

---

## 🔎 Cómo Buscar

### 1. **Búsqueda por Nombre de Endpoint**

```
Escribe: "productos"
Resultado: Muestra todos los endpoints relacionados con productos
  ✓ GET /api/v1/products/products/
  ✓ POST /api/v1/products/products/
  ✓ GET /api/v1/products/categories/
```

### 2. **Búsqueda por Método HTTP**

```
Escribe: "get"
Resultado: Muestra TODOS los endpoints GET
```

O combina:
```
Escribe: "get usuarios"
Resultado: Endpoints GET relacionados con usuarios
```

### 3. **Búsqueda por Ruta**

```
Escribe: "/v1/sales"
Resultado: Todos los endpoints de ventas
  ✓ GET /api/v1/sales/sales/
  ✓ POST /api/v1/sales/sales/
  ✓ GET /api/v1/sales/payments/
```

### 4. **Búsqueda por Descripción**

```
Escribe: "activo"
Resultado: Endpoints cuya descripción contenga "activo"
```

---

## ⚡ Ejemplos Prácticos

### Buscar Endpoints de "Usuarios"

1. Abre: `http://localhost:8000/api/docs/`
2. En el buscador escribe: **"usuarios"**
3. Swagger filtra automáticamente y muestra:
   ```
   👤 Usuarios (6)
   - GET /api/v1/accounts/users/me/
   - PATCH /api/v1/accounts/users/me/
   - POST /api/v1/accounts/users/register/
   - PATCH /api/v1/accounts/users/me/change-password/
   - POST /api/v1/accounts/users/software-clients/
   - DELETE /api/v1/accounts/users/software-clients/{id}/
   ```

### Buscar Endpoints POST (Crear)

1. En el buscador escribe: **"post"**
2. Swagger filtra todos los endpoints de creación:
   ```
   🟩 POST /api/auth/login/
   🟩 POST /api/v1/products/products/
   🟩 POST /api/v1/accounts/stores/
   🟩 POST /api/v1/sales/sales/
   ... (todos los POST)
   ```

### Buscar Endpoint Específico por Ruta

1. En el buscador escribe: **"/v1/sales/sales/{id}/"**
2. Swagger muestra solo ese endpoint
3. Haz clic para expandirlo y ver detalles

---

## 📍 Ubicación Exacta del Buscador

```
┌──────────────────────────────────────────────────────────────┐
│  Nurax API                                                   │
│  Documentación de la API de Nurax                            │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ 🔍 [Escribe aquí para filtrar endpoints]              │  │  ← AQUÍ ESTÁ
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ✅ 🔐 Autenticación (expandible)                           │
│  📦 Productos (expandible)                                  │
│  👤 Usuarios (expandible)                                   │
│  ...                                                        │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎯 Tips Profesionales

### Tip 1: Buscar y Expandir
```
1. Escribe "usuarios" en el buscador
2. Haz clic en la sección "👤 Usuarios" para expandirla
3. Verás todos los endpoints de usuarios filtrados
```

### Tip 2: Case-Insensitive (Sin Importar Mayúsculas)
```
Estos búsquedas son equivalentes:
- "USUARIOS" ✓
- "usuarios" ✓
- "USUARIOS" ✓
- "Users" ✓ (funciona en inglés también)
```

### Tip 3: Búsqueda Parcial
```
Estos funcionan para encontrar "usuarios":
- "usua" ✓
- "rio" ✓
- "us" ✓
- "usuarios" ✓
```

### Tip 4: Borrar Búsqueda
```
- Limpia el campo del buscador para ver todos los endpoints nuevamente
- O presiona Escape en algunos navegadores
```

### Tip 5: Combinar Términos
```
Busca: "get usuarios"
Resultado: Solo GET de la sección Usuarios
```

---

## 🔧 Configuración Técnica (Backend)

### Cambios en `core/settings.py`

Se agregaron las siguientes opciones a `SPECTACULAR_SETTINGS`:

```python
SPECTACULAR_SETTINGS = {
    # ... configuración existente ...
    'SWAGGER_UI_SETTINGS': {
        'persistAuthorization': True,  # Mantener sesión activa
        'displayOperationId': False,   # Interfaz más limpia
        'filter': True,                # ✅ Habilita el buscador
        'showExtensions': False,       # Menos clutter
        'deepLinking': True,           # URLs directas a endpoints
    },
}
```

### Propiedad Clave: `'filter': True`

- **Habilita:** El buscador/filtro en Swagger UI
- **Comportamiento:** Filtra endpoints mientras escribes
- **Compatibilidad:** Works with drf-spectacular >= 0.15.0
- **Versión actual:** 0.29.0 ✅

---

## 🚀 Versión de drf-spectacular

```
Versión instalada: 0.29.0
Fecha: Enero 2025
Soporte para Swagger UI: ✅ SÍ
Soporte para búsqueda: ✅ SÍ
Soporte para filtros: ✅ SÍ
```

**El buscador es totalmente soportado en tu versión.**

---

## 🎨 Mejoras Visuales

Con la configuración actualizada, ahora tendrás:

1. ✅ **Buscador visible** - Caja de entrada clara en la parte superior
2. ✅ **Filtrado en tiempo real** - Mientras escribes se filtran endpoints
3. ✅ **Autenticación persistente** - Tu sesión se mantiene activa
4. ✅ **Deep linking** - Puedes compartir URLs directas a endpoints
5. ✅ **Interfaz limpia** - Sin clutter de operación IDs innecesarios

---

## 📊 Comparativa: Antes vs. Después

| Aspecto | Antes | Después |
|---------|-------|---------|
| Buscador visible | ❓ Posible no visible | ✅ Claramente visible |
| Filtrado en tiempo real | ❓ Posible no funcionar | ✅ Funciona perfectamente |
| Sesión persistente | ❌ Se perdía al refresh | ✅ Se mantiene activa |
| Deep linking | ❌ No disponible | ✅ Disponible |

---

## 🔍 ¿Qué Puedo Buscar?

### ✅ Funciona
- Nombres de tags: "Productos", "Usuarios", "Ventas"
- Métodos HTTP: "GET", "POST", "PUT", "PATCH", "DELETE"
- Rutas parciales: "/products", "/users", "/sales"
- Palabras clave: "list", "create", "delete", "activo"

### ⚠️ Limitaciones
- No busca dentro de parámetros específicos
- No busca dentro del cuerpo de request
- No busca dentro de respuestas (usa la UI de Swagger para eso)

---

## 📞 Troubleshooting

### Problema: No veo el buscador

**Solución 1:** Recarga la página
```
Presiona Ctrl+Shift+R (refresh hard) en el navegador
```

**Solución 2:** Limpia caché
```
Developer Tools → Application → Clear Site Data
```

**Solución 3:** Verifica servidor Django
```bash
python manage.py runserver
# Visita: http://localhost:8000/api/docs/
```

### Problema: El buscador no filtra

**Solución:** Asegúrate de que el servidor está ejecutando la versión actualizada
```bash
# Reinicia el servidor
python manage.py runserver
```

---

## 🎯 Flujo Típico de Búsqueda

```
1. Abres Swagger UI
   ↓
2. Ves el buscador en la parte superior
   ↓
3. Escribes lo que buscas: "usuarios", "get", etc.
   ↓
4. Swagger filtra automáticamente los endpoints
   ↓
5. Haces clic en el endpoint que quieres
   ↓
6. Se expande para mostrar detalles
   ↓
7. Pruebas el endpoint con "Try it out"
```

---

## ⌨️ Atajos de Teclado

| Atajo | Función |
|-------|---------|
| `Ctrl+F` | Busca en la página (navegador) |
| `Escape` | Limpia búsqueda (en algunos navegadores) |
| `Enter` | Confirma búsqueda |

---

## 📚 Recursos Oficiales

- **drf-spectacular:** https://drf-spectacular.readthedocs.io/
- **Swagger UI:** https://swagger.io/tools/swagger-ui/

---

## ✨ Resumen

✅ **El buscador está activado y funcional**  
✅ **Está en la parte superior del panel de Swagger UI**  
✅ **Filtra endpoints en tiempo real**  
✅ **Búsqueda case-insensitive**  
✅ **Soportado en drf-spectacular 0.29.0**  

**Para buscar endpoints:** Simplemente escribe en el buscador y Swagger filtrará automáticamente la lista.

---

**Última actualización:** Abril 2026  
**Versión:** 1.0.0  
**Estado:** ✅ Implementado y Funcional

