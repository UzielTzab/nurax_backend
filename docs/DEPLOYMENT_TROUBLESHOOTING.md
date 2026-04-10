# 🐛 Deployment Troubleshooting - Nurax Backend

## Caso 1: ModuleNotFoundError después de Project Restructuring

### 📋 Problema

Después de reestructurar el proyecto Django de:
```
nurax_backend/
├── accounts/
├── products/
...
└── nurax_backend/  (config)
```

A:
```
nurax_backend/
├── apps/
│   ├── accounts/
│   ├── products/
│   └── ...
├── core/  (config)
└── ...
```

El deployment en **Render** fallaba con:
```
ModuleNotFoundError: No module named 'nurax_backend'
==> Running 'gunicorn nurax_backend.wsgi:application'
```

### 🔍 Raíz Causa

1. **init_db.py** seguía referenciando `nurax_backend.settings` → ✅ Fijo
2. **manage.py** seguía referenciando `nurax_backend.settings` → ✅ Fijo
3. **Render Dashboard** tenía comando hardcodeado: `gunicorn nurax_backend.wsgi:application` → ❌ **PROBLEMA REAL**

El dashboard de Render **ignora** `Procfile` cuando hay un comando configurado manualmente. Tiene **prioridad máxima**.

### ✅ Solución Implementada

#### Paso 1: Actualizar código (DONE)
```python
# init_db.py
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")  # ✅

from apps.products.models import Category  # ✅
from apps.accounts.models import User, Store  # ✅
```

```python
# manage.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  # ✅
```

#### Paso 2: Crear Procfile (como respaldo)
```procfile
web: gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
```

#### Paso 3: Actualizar Dashboard Render (CRÍTICO)
**Dashboard → Settings → Start Command**
```
❌ CAMBIAR DE:  gunicorn nurax_backend.wsgi:application
✅ CAMBIAR A:   gunicorn core.wsgi:application
```

**Click "Save" → Click "Redeploy"** → ✅ Deploy sucessful

### 📊 Orden de Configuración en Render

| Prioridad | Fuente | Notas |
|-----------|--------|-------|
| 🔴 **1 (Máxima)** | Dashboard manual | Si existe, ignora todo lo demás |
| 🟡 **2** | Procfile | Se usa solo si dashboard está vacío |
| 🟢 **3** | render.yaml | No es leído por Render standard |

### 📝 Lecciones Aprendidas

1. **Procfile es respaldo**: Mantenerlo por si migras a Heroku/Railway/DigitalOcean
2. **Dashboard tiene prioridad**: Siempre verificar que el comando sea correcto en el dashboard
3. **Documenta cambios estructurales**: Cuando cambies módulos (nurax_backend → core), actualiza:
   - `init_db.py` 
   - `manage.py`
   - `core/settings.py` (ROOT_URLCONF, WSGI_APPLICATION)
   - `core/urls.py` (imports)
   - **Dashboard de Render** (muy importante!)

### 🚀 Cómo Evitar en el Futuro

Cuando restructures Django a nueva arquitectura:
1. ✅ Actualiza todos los imports en código
2. ✅ Actualiza DJANGO_SETTINGS_MODULE en scripts
3. ✅ Crea/actualiza Procfile
4. ✅ **Verifica Dashboard de Render** - cambiar comando si es necesario
5. ✅ Documenta los cambios en este archivo

### 📦 Archivos Afectados en este Deploy

| Archivo | Cambio | Estado |
|---------|--------|--------|
| `init_db.py` | DJANGO_SETTINGS_MODULE: nurax_backend → core | ✅ Actualizado |
| `init_db.py` | imports: products → apps.products | ✅ Actualizado |
| `init_db.py` | imports: accounts → apps.accounts | ✅ Actualizado |
| `manage.py` | DJANGO_SETTINGS_MODULE: nurax_backend → core | ✅ Actualizado |
| `core/settings.py` | ROOT_URLCONF: nurax_backend → core | ✅ Actualizado |
| `core/settings.py` | WSGI_APPLICATION: nurax_backend → core | ✅ Actualizado |
| `core/settings.py` | INSTALLED_APPS: accounts → apps.accounts | ✅ Actualizado |
| `core/urls.py` | imports y paths: accounts → apps.accounts | ✅ Actualizado |
| `Procfile` | web: gunicorn core.wsgi:application | ✅ Creado |
| **Render Dashboard** | Start Command | ✅ Actualizado manualmente |

---

## Cambio de Referencia

**Commit:** 9d1c437af386d809e6c1a95fee53f4f6481a5eff  
**Rama:** main  
**Fecha:** April 9, 2026  
**Status:** ✅ RESUELTO Y EN PRODUCCIÓN

---

## Si tienes problemas similares

1. Verifica que `Procfile` exista y sea correcto
2. **Verificar Dashboard de Render** - es donde Render realmente busca el comando
3. Si cambias la estructura del proyecto, actualiza todos los references de módulos
4. Hacer test en local primero: `gunicorn core.wsgi:application`
