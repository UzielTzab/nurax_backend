# Bug Fix: JWT Authentication con Cambio de Email

## Problema

Cuando un usuario cambió su nombre de usuario y correo electrónico de su cuenta (siendo cliente dueño), recibió un error `403 Forbidden` al intentar crear un producto:

```json
{
  "detail": "No tienes acceso a esta tienda."
}
```

## Causa Raíz

El sistema utilizaba el **email como identificador en los tokens JWT** (`USERNAME_FIELD = 'email'` en el modelo User). Esto causaba que:

1. **Tokens inválidos después del cambio de email**: Si el usuario tenía un token JWT activo con su email anterior, ese token se volvía inválido cuando cambió el email en la base de datos.

2. **Pérdida de asociación con tienda**: La autenticación fallaba, por lo que `self.request.user` no retornaba correctamente el usuario, causando que la validación de permisos en `StoreMembership` falle.

3. **Error incorrecto**: En lugar de obtener un error de autenticación (`401 Unauthorized`), obtenía un error de permisos (`403 Forbidden`).

## Solución Implementada

Se cambió el sistema JWT para usar el **UUID del usuario como identificador** en lugar del email. Esto permite que el usuario pueda cambiar su email sin invalidar tokens.

### Cambios:

1. **`utils/authentication.py`**: Personalizado `get_user()` para:
   - Primero buscar por `user_id` (identificador nuevo basado en UUID)
   - Fallback a buscar por `email` (para compatibilidad hacia atrás con tokens antiguos)

2. **`utils/auth_views.py`**: 
   - Creado `CustomTokenObtainPairSerializer` que incluye `user_id` en el token
   - Creado `CustomRefreshToken` que también usa `user_id`
   - Ambos reemplazan el `sub` (subject) con el UUID en lugar del email

### Comportamiento:

- **Tokens nuevos**: Contienen `user_id` (UUID) como identificador principal
- **Tokens antiguos**: Siguen funcionando mediante fallback a email (compatible hacia atrás)
- **Cambios de email**: Ya no invalidan tokens futuros

## Pasos para Resolver el Problema Actual

Si el usuario está experimentando este error **ahora**, necesita hacer lo siguiente:

### Opción 1: Limpiar la Sesión (Recomendado)

1. **Cierra la sesión completamente** en tu navegador:
   - Ve a cualquier página (ej: home)
   - Abre DevTools (F12)
   - Ve a la pestaña "Application"
   - Limpia todas las cookies de tu dominio
   - O simplemente usa "Logout" si hay un botón

2. **Inicia sesión de nuevo**:
   - Usa tu **email actual** (el nuevo que estableciste)
   - Usa tu contraseña
   - Obtendrás un nuevo token JWT basado en `user_id`

3. **Intenta crear un producto nuevamente**:
   - Debería funcionar sin errores

### Opción 2: Debug (Verificar Estado Actual)

Si aún tienes problemas, puedes verificar qué usuario está autenticado:

```bash
# En el navegador, abre DevTools (F12) y ejecuta en la consola:

# 1. Obtener el usuario actual autenticado
fetch('http://localhost:8000/api/v1/accounts/users/me/', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  },
  credentials: 'include'  // Incluir cookies
})
.then(r => r.json())
.then(data => console.log('Usuario actual:', data))

# 2. Ver las cookies activas
document.cookie  // Mostrará todas las cookies

# 3. Verificar las tiendas asociadas al usuario
fetch('http://localhost:8000/api/v1/accounts/stores/', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  },
  credentials: 'include'
})
.then(r => r.json())
.then(data => console.log('Tiendas:', data))
```

## Validación

Para confirmar que el fix funciona:

1. Haz login normalmente
2. Intenta crear un producto
3. Debería funcionar sin errores de permiso

## Notas Técnicas

- El modelo User sigue teniendo `USERNAME_FIELD = 'email'` (necesario para Django)
- El cambio solo afecta a JWT, no a autenticación de Django
- El fallback a email significa que tokens antiguos aún funcionan
- Se recomienda que los usuarios refresque sus tokens (logout/login) después de este update

## Para Desarrolladores

### Estructura del Token JWT

**Tokens nuevos (después del fix)**:
```json
{
  "token_type": "access",
  "exp": 1234567890,
  "iat": 1234567800,
  "jti": "...",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",  // ← NUEVO
  "sub": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",     // ← UUID en lugar de email
  "username": "usuario_actual",
  "email": "usuario@ejemplo.com"
}
```

**Tokens antiguos (compatibilidad)**:
```json
{
  "token_type": "access",
  "exp": 1234567890,
  "iat": 1234567800,
  "jti": "...",
  "sub": "usuario@ejemplo_anterior.com",  // ← Email (fallback)
  "username": "usuario_anterior"
}
```

### Testing

```python
# En tests, para verificar el fix:
from rest_framework.test import APIClient
from apps.accounts.models import User, Store, StoreMembership

client = APIClient()

# 1. Login con email
response = client.post('/api/auth/login/', {
    'email': 'user@example.com',
    'password': 'password123'
})
assert response.status_code == 200

# 2. Obtener usuario actual
response = client.get('/api/v1/accounts/users/me/')
assert response.status_code == 200
user_data = response.json()
assert 'id' in user_data

# 3. Crear producto
response = client.post('/api/v1/products/products/', {
    'name': 'Test Product',
    'store': store_id,
    'base_cost': 10,
    'sale_price': 20
})
assert response.status_code == 201
```
