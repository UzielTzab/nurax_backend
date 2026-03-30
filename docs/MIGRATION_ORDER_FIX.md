# Troubleshooting: InconsistentMigrationHistory Error

## Problema
```
django.db.migrations.exceptions.InconsistentMigrationHistory: 
Migration admin.0001_initial is applied before its dependency accounts.0001_initial 
on database 'default'.
```

## Causa
Este error ocurre cuando en la BD de producción, las migraciones se ejecutaron en un **orden incorrecto**:
- Django's `admin.0001_initial` se aplicó primero
- Pero depende del modelo `User` de `accounts.0001_initial`
- Que fue aplicada **después**

### Por qué pasó (en Render)
En el proceso de deploy con `docker-compose` + Render:
1. Las migraciones se ejecutaron en un orden no determinístico
2. `admin` (built-in de Django) se ejecutó antes que `accounts` (app personalizada)
3. Esto creó una inconsistencia

## Solución

### ✅ Solución Implementada (v0.2.0)
Se creó una migración de **reparación** en `accounts/migrations/0002_fix_admin_dependency.py`:

```python
class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
        ('admin', '0001_initial'),  # ← Force correct order
    ]
    operations = []  # No schema changes needed
```

### Cómo funciona
- Esta migración vacía **establece explícitamente** que:
  - `admin.0001_initial` debe ejecutarse **antes**
  - De `accounts.0001_initial` (que ya está aplicada)
- Django entiende las dependencias y corrige el historial
- Durante el siguiente deploy, migrará sin errores

## Para Render (Deploy Fix)

### Build Script
En `render.yaml` o configuración de build:

```bash
./manage.py migrate --database=default
```

Django ejecutará:
1. `admin.0001_initial` (ya está, se salta)
2. `accounts.0001_initial` (ya está, se salta)
3. `accounts.0002_fix_admin_dependency` ← Nueva, establece orden
4. Resto de migraciones normalmente

### Alternativa: Forzar Fresh Database
Si la BD está muy corrupta, en Render:
1. Ir a Dashboard → Database
2. Reset Database (⚠️ Destruye todos los datos)
3. Re-deploy
4. Las migraciones se aplicarán en orden correcto

## Prevención Futura

### 1. INSTALLED_APPS Order (Production-Ready)
```python
# settings.py
INSTALLED_APPS = [
    # ← Django's built-in apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # ← Third party (DESPUÉS)
    'rest_framework',
    # ...
    
    # ← Custom apps (DESPUÉS)
    'accounts.apps.AccountsConfig',  # ← IMPORTANTE: antes que admin deps
    'products.apps.ProductsConfig',
    # ...
]
```

### 2. AUTH_USER_MODEL (Required for Custom User)
```python
# settings.py - CRITICAL for production
AUTH_USER_MODEL = 'accounts.User'
```

### 3. Build Script Best Practice
```bash
# manage.py runserver equivalent for production
python manage.py collectstatic --noinput
python manage.py migrate --verbosity=2  # More logging untuk debug
```

## Verificación Post-Fix

Después del deploy, verificar:
```bash
# SSH into Render container
python manage.py showmigrations
# Debería mostrar ✓ marca al lado de todas las migraciones,
# incluyendo admin.0001_initial ANTES de accounts.0001_initial
```

## Referencias
- Django Docs: [Data Migrations](https://docs.djangoproject.com/en/6.0/topics/migrations/#data-migrations)
- Django Docs: [Custom User Model](https://docs.djangoproject.com/en/6.0/topics/auth/customizing/#substituting-a-custom-user-model)
- Common Issue: Custom User Model + Built-in Admin Conflictsp
