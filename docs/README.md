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
- [API_ENDPOINTS.md](API_ENDPOINTS.md) - Todos los endpoints disponibles
- [AGENT.md](AGENT.md) - Sección "Domain Context" para conceptos de negocio
- El diagrama ERD en [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) para entender datos

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
→ Lee [API_ENDPOINTS.md](API_ENDPOINTS.md)

### **"¿Cómo me autentico?"**
→ Ve a [API_ENDPOINTS.md](API_ENDPOINTS.md) - Sección "Autenticación"

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
