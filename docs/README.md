# Índice de Documentación - Nurax Backend

Bienvenido a la documentación del backend de Nurax. Este directorio contiene toda la información que necesitas para entender, desarrollar y mantener el proyecto.

---

## 📚 Archivos de Documentación

### 1. **[AGENT.md](AGENT.md)** - Guía Técnica Principal
   - 📌 **Empieza aquí** si es tu primera vez
   - Descripción completa del proyecto
   - Stack tecnológico
   - Estructura de directorios
   - Componentes principales
   - Patrones clave y convenciones
   - **Duración lectura:** 30-40 minutos
   - **Para quién:** Developers nuevos, IAs, Copilot

### 2. **[DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)** - Estructura de BD
   - Diagrama ERD (Entity Relationship)
   - Descripción detallada de cada tabla
   - Tipos de datos y constraints
   - Relaciones entre entidades
   - Ejemplos de queries
   - **Duración lectura:** 20-30 minutos
   - **Para quién:** Backend devs, DBAs, Data analysts

### 3. **[API_ENDPOINTS.md](API_ENDPOINTS.md)** - Endpoints y Rutas
   - Listado completo de endpoints
   - Métodos HTTP, request/response
   - Ejemplos con cURL
   - Códigos de estado y errores
   - Paginación y filtrado
   - **Duración lectura:** 15-25 minutos
   - **Para quién:** Frontend devs, API consumers, Testers

### 4. **[DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)** - Guía de Desarrollo
   - Setup inicial
   - Desarrollo local vs Docker
   - Crear nuevas features (step-by-step)
   - Migraciones de BD
   - Testing
   - Debugging
   - Buenas prácticas
   - Troubleshooting
   - **Duración lectura:** 40-60 minutos (referencia)
   - **Para quién:** Backend developers, QA

### 5. **[MIGRATION_ORDER_FIX.md](MIGRATION_ORDER_FIX.md)** - Error de Migraciones
   - ❌ Problema: `InconsistentMigrationHistory` en producción
   - ✅ Solución implementada
   - Causa y prevención
   - Verificación post-fix
   - **Duración lectura:** 5-10 minutos
   - **Para quién:** DevOps, Backend developers, Render deploy troubleshooting

### 6. **[BACKEND_IMPLEMENT_HTTPONLY_COOKIES.md](BACKEND_IMPLEMENT_HTTPONLY_COOKIES.md)** - Seguridad: HttpOnly Cookies
   - 🔒 Migración a HttpOnly cookies (XSS protection)
   - Implementación completa en Django
   - Cambios en `settings.py`, `authentication.py`, `accounts/views.py`
   - Configuración CORS y seguridad
   - Testing y validación
   - **Duración lectura:** 20-30 minutos
   - **Para quién:** Backend developers, Security engineers
   - **Status:** ⏳ Próxima implementación

### 7. **[DEPLOYMENT_TROUBLESHOOTING.md](DEPLOYMENT_TROUBLESHOOTING.md)** - Incidentes de Deploy en Producción
   - 🐛 Caso 1: `ModuleNotFoundError` tras reestructuración (`nurax_backend` → `core`)
   - 🔐 Caso 2: Login falla en producción por cookies cross-site (`SameSite=Strict`)
   - 🔁 Caso 3: Frontend sin proxy real (Netlify rewrites para `/api/*`)
   - Checklist Render + Netlify para validar CORS/CSRF/cookies
   - Variables de entorno recomendadas para evitar regresiones
   - **Duración lectura:** 10-15 minutos
   - **Para quién:** DevOps, Backend developers, incident response

### 8. **[SWAGGER_TAGS_ORGANIZATION.md](SWAGGER_TAGS_ORGANIZATION.md)** - Documentación API en Swagger
   - 📚 Organización de endpoints por tags (categorías)
   - Listado completo de tags implementados
   - Endpoints agrupados por módulo (Productos, Ventas, Usuarios, etc.)
   - Estructura visual de navegación en Swagger/OpenAPI
   - **Duración lectura:** 10-15 minutos
   - **Para quién:** API consumers, Frontend developers, QA, Documentación

### 9. **[SWAGGER_IMPLEMENTATION_SUMMARY.md](SWAGGER_IMPLEMENTATION_SUMMARY.md)** - Implementación Técnica de Tags
   - 🔧 Cambios técnicos realizados en cada ViewSet
   - Uso de `@extend_schema_view` y `@extend_schema` de drf-spectacular
   - Archivo por archivo de las modificaciones
   - Ejemplos de antes/después
   - Beneficios y próximas mejoras opcionales
   - **Duración lectura:** 15-20 minutos
   - **Para quién:** Backend developers, Architecture review

### 10. **[SWAGGER_VISUAL_PREVIEW.md](SWAGGER_VISUAL_PREVIEW.md)** - Vista Previa Visual de Swagger
   - 🖥️ Cómo se ve la interfaz de Swagger con los tags
   - Estructura organizacional visual
   - Ejemplo de interacción usuario
   - Estadísticas de endpoints
   - Cómo acceder en desarrollo y producción
   - Próximas mejoras opcionales
   - **Duración lectura:** 10 minutos
   - **Para quién:** API consumers, Frontend developers, QA

### 11. **[SWAGGER_TAGS_CHECKLIST.md](SWAGGER_TAGS_CHECKLIST.md)** - Checklist de Verificación
   - ✅ Lista completa de items a validar
   - Verificación de código (imports, decoradores)
   - Verificación en desarrollo (sintaxis, servidor)
   - Verificación visual en Swagger (tags, endpoints)
   - Pruebas de interacción
   - Validación de cambios en Git
   - **Duración lectura:** 15 minutos (para ejecutar)
   - **Para quién:** QA, Backend developers, DevOps

### 12. **[SWAGGER_IMPLEMENTATION_COMPLETE.md](SWAGGER_IMPLEMENTATION_COMPLETE.md)** - Resumen Ejecutivo
   - 🎯 Visión general de todo lo implementado
   - Números y estadísticas de la implementación
   - Beneficios inmediatos
   - Cambios principales (antes/después)
   - Lista de archivos modificados
   - Instrucciones de verificación
   - **Duración lectura:** 5-10 minutos
   - **Para quién:** Product manager, Team leads, Stakeholders

### 13. **[SWAGGER_QUICK_REFERENCE.md](SWAGGER_QUICK_REFERENCE.md)** - Referencia Rápida
   - 🏷️ Vista rápida de todos los 21 tags
   - Tabla con cantidad de endpoints
   - Atajos y tips profesionales
   - Flujo típico de usuario
   - URLs directas
   - Notas de seguridad
   - **Duración lectura:** 3-5 minutos
   - **Para quién:** API consumers, Frontend developers, Testing

### 14. **[SWAGGER_SEARCH_GUIDE.md](SWAGGER_SEARCH_GUIDE.md)** - Guía del Buscador en Swagger
   - 🔍 Cómo usar el buscador de endpoints
   - Ubicación exacta del buscador en Swagger UI
   - Ejemplos de búsquedas (por nombre, método, ruta)
   - Tips profesionales para búsquedas eficientes
   - Troubleshooting si no ves el buscador
   - Configuración técnica de drf-spectacular
   - Atajos de teclado
   - **Duración lectura:** 5-10 minutos
   - **Para quién:** API consumers, Frontend developers, QA, Testers

---

## 🎯 Guía Rápida por Rol

### **🆕 Nuevo Developer en el Proyecto**

1. Leer [AGENT.md](AGENT.md) - Contexto general (30 min)
2. Leer [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Setup e instalación (20 min)
3. [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Entender BD (20 min)
4. Hacer un pequeño cambio para practicar (ej: crear un endpoint simple)

**Tiempo total:** ~1-1.5 horas

---

### **👨‍💻 Backend Developer**

**Lectura recomendada:**
- [AGENT.md](AGENT.md) - Contexto y patrones
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Procedimientos
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Dimensiones de BD

**Cuando necesites agregar feature:**
1. Ir a sección "Crear Nuevas Features" en [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)
2. Consultar [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) si necesitas entender relaciones
3. Usar [API_ENDPOINTS.md](API_ENDPOINTS.md) como referencia

---

### **🎨 Frontend Developer**

**Solo necesitas:**
- [SWAGGER_TAGS_ORGANIZATION.md](SWAGGER_TAGS_ORGANIZATION.md) - Endpoints organizados por categoría (mejor que leer lista plana)
- [API_ENDPOINTS.md](API_ENDPOINTS.md) - Todos los endpoints disponibles
- [AGENT.md](AGENT.md) - Sección "Domain Context" para conceptos de negocio
- El diagrama ERD en [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) para entender datos

**También disponible:**
- `http://localhost:8000/api/docs/` - UI interactiva de Swagger/OpenAPI para probar endpoints

**No necesitas:** DEVELOPMENT_GUIDE.md (a menos que quieras contribuir al backend)

---

### **🤖 IA / Copilot**

**Siempre revisar:**
- [AGENT.md](AGENT.md) - Contexto completo del proyecto
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Estructura de modelos
- [API_ENDPOINTS.md](API_ENDPOINTS.md) - Qué endpoints existen

Esto cubre el 80% de lo que necesitas saber.

---

### **🧪 QA / Tester**

**Leer:**
1. [AGENT.md](AGENT.md) - Sección "Domain Context"
2. [API_ENDPOINTS.md](API_ENDPOINTS.md) - Todos los endpoints para testear
3. [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Sección "Testing"

---

### **📊 Data Analyst**

**Leer:**
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Tablas, campos, tipos
- [AGENT.md](AGENT.md) - Sección "Domain Context"

**Útil para queries SQL en PostgreSQL**

---

## 🗺️ Mapeo Visual

```
┌─────────────────────────────────────────────────────────┐
│                   NURAX BACKEND                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  📜 AGENT.md - Contexto General                 │   │
│  │  • Project Overview                             │   │
│  │  • Architecture                                 │   │
│  │  • Key Patterns                                 │   │
│  └──────────────────────────────────────────────────┘   │
│                       ▼                                  │
│  ┌──────────────┬──────────────┬──────────────────┐     │
│  │              │              │                  │     │
│  │   📊 DB      │   🔌 API     │   🛠️ Dev        │     │
│  │   SCHEMA     │   ENDPOINTS  │   GUIDE          │     │
│  │              │              │                  │     │
│  │ • 13 tablas  │ • 50+ rutas  │ • Setup          │     │
│  │ • Relaciones │ • HTTPs      │ • Features       │     │
│  │ • Queries    │ • Autenticación│ • Testing      │     │
│  │              │              │ • Debugging      │     │
│  └──────────────┴──────────────┴──────────────────┘     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📅 Flujos de Trabajo

### **Cuando necesitas agregar una Feature**

```
1. AGENT.md
   └─ Revisar patrones existentes
2. DATABASE_SCHEMA.md
   └─ ¿Necesito nuevo modelo? Entender relaciones
3. DEVELOPMENT_GUIDE.md
   └─ Seguir checklist "Crear Nuevas Features"
4. Implementar (models → serializers → views → urls)
5. API_ENDPOINTS.md
   └─ Documentar nuevo endpoint
```

---

### **Cuando necesitas entender la BD**

```
1. DATABASE_SCHEMA.md (diagrama ERD)
   └─ Ver relaciones visuales
2. DATABASE_SCHEMA.md (tablas detalladas)
   └─ Leer descripción de cada tabla
3. DATABASE_SCHEMA.md (ejemplos SQL)
   └─ Ver ejemplos de queries
```

---

### **Cuando necesitas usar la API**

```
1. API_ENDPOINTS.md
   └─ Encontrar endpoint que necesitas
2. Copiar ejemplo (cURL, Python, JavaScript)
3. Si necesitas entender datos:
   └─ Revisar DATABASE_SCHEMA.md
```

---

### **Cuando necesitas debuggear algo**

```
1. AGENT.md
   └─ Revisar patrones aplicables
2. DEVELOPMENT_GUIDE.md
   └─ Ir a "Debugging" o "Troubleshooting"
3. Django Shell / Logs / PostgreSQL
   └─ Encontrar problema
```

---

## 🔑 Conceptos Clave

| Concepto | Ubicación | Descripción breve |
|----------|-----------|-------------------|
| **Multi-tenant** | AGENT.md | Cada usuario aislado, datos separados |
| **JWT Auth** | AGENT.md | Autenticación por token (email + password) |
| **HttpOnly Cookies** | BACKEND_IMPLEMENT_HTTPONLY_COOKIES.md | Tokens seguros, no accesibles a JavaScript |
| **XSS Protection** | BACKEND_IMPLEMENT_HTTPONLY_COOKIES.md | Mitigación de ataques XSS |
| **ViewSet** | AGENT.md | Combina CRUD en una clase DRF |
| **Serializer** | AGENT.md | Convierte modelos ↔ JSON |
| **Migración** | DEVELOPMENT_GUIDE.md | Cambios de BD versionados |
| **Related names** | AGENT.md | Acceso inverso a relaciones ForeignKey |
| **Snapshot** | DATABASE_SCHEMA.md | Guardar datos históricos (SaleItem.product_name) |
| **CashShift** | AGENT.md | Turno de caja, auditoría de dinero |

---

## 🚀 Quick Links

### **Setup & Ejecución**

```bash
# Con Docker (recomendado)
docker-compose up --build

# Shell
docker exec -it nurax_api bash

# Migraciones
docker exec nurax_api python manage.py migrate

# Tests
docker exec nurax_api python manage.py test

# Docs en navegador
http://localhost:8000/api/docs/
```

### **URLs Importantes**

| URL | Descripción |
|-----|-------------|
| `http://localhost:8000/` | API root |
| `http://localhost:8000/admin` | Django admin |
| `http://localhost:8000/api/docs/` | Swagger UI (documentación interactiva) |
| `http://localhost:8000/api/schema/` | OpenAPI schema (JSON) |

---

## ❓ Preguntas Frecuentes

### **"¿Por dónde empiezo?"**
→ Lee [AGENT.md](AGENT.md) primero

### **"¿Cómo creo un nuevo endpoint?"**
→ Ve a [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Sección "Crear Nuevas Features"

### **"¿Cómo se relacionan los modelos?"**
→ Ve a [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Diagrama ERD

### **"¿Cuáles son los endpoints disponibles?"**
→ Lee [SWAGGER_TAGS_ORGANIZATION.md](SWAGGER_TAGS_ORGANIZATION.md) para ver endpoints organizados por categoría
→ O abre `http://localhost:8000/api/docs/` para UI interactiva de Swagger

### **"¿Cómo se organiza la documentación de API en Swagger?"**
→ Ve a [SWAGGER_TAGS_ORGANIZATION.md](SWAGGER_TAGS_ORGANIZATION.md) - Organización por tags
→ Ve a [SWAGGER_IMPLEMENTATION_SUMMARY.md](SWAGGER_IMPLEMENTATION_SUMMARY.md) - Detalles técnicos de implementación

### **"¿Cómo me autentico?"**
→ Ve a [API_ENDPOINTS.md](API_ENDPOINTS.md) - Sección "Autenticación"

### **"¿Cómo busco endpoints rápidamente en Swagger?"**
→ Ve a [SWAGGER_SEARCH_GUIDE.md](SWAGGER_SEARCH_GUIDE.md) - Guía completa del buscador
→ **Ubicación:** Caja de búsqueda en la parte superior de `http://localhost:8000/api/docs/`
→ **Ejemplos:** Busca "usuarios", "get", "/v1/sales", etc.

### **"¿Cómo está asegurada la autenticación?"**
→ Ve a [BACKEND_IMPLEMENT_HTTPONLY_COOKIES.md](BACKEND_IMPLEMENT_HTTPONLY_COOKIES.md) - Implementación de HttpOnly cookies
### **"¿Cómo hago una migración?"**
→ Ve a [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Sección "Migraciones de BD"

### **"Hay un bug, ¿cómo debuggeo?"**
→ Ve a [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Sección "Debugging"

### **"¿Cuál es la estructura de carpetas?"**
→ Ve a [AGENT.md](AGENT.md) - Sección "Estructura del Repositorio"

---

## 📞 Soporte

Si encuentras problemas:

1. **Verificar Troubleshooting**: [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md#troubleshooting)
2. **Ver Documentación relevante** según el tema
3. **Buscar en código**: Usar editor search (Ctrl+F)
4. **Revisar logs**: `docker logs -f nurax_api`
5. **Git blame**: Ver qué cambios causaron el problema

---

## 📝 Changelog

| Fecha | Cambio | Archivo |
|-------|--------|---------|
| Marzo 2026 | Documentación inicial completa | AGENT.md, DATABASE_SCHEMA.md, API_ENDPOINTS.md, DEVELOPMENT_GUIDE.md |

---

## 🎓 Niveles de Difficulty

Algunos archivos tienen diferentes niveles:

- 🟢 **Principiante**: Leer en orden
- 🟡 **Intermedio**: Saltar a secciones específicas
- 🔴 **Avanzado**: Profundizar en detalles

**[AGENT.md](AGENT.md)**: 🟢 → 🟡  
**[DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)**: 🟡 → 🔴  
**[API_ENDPOINTS.md](API_ENDPOINTS.md)**: 🟢 (referencia más que lectura)  
**[DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)**: 🟡 → 🔴

---

**Última actualización:** Marzo 2026  
**Versión Backend:** 1.0.0  
**Status:** Documentación Completa ✅
