---
name: backend-httponly-cookies-implementation
description: >
  Instrucciones paso-a-paso para implementar autenticación segura con HttpOnly cookies en Django Backend
---

# 🔐 Implementación Backend: HttpOnly Cookies en Django

> **Requisito:** El Frontend ya está refactorizado (6 Abril 2026)  
> **Estado:** 📋 LISTO PARA IMPLEMENTAR EN BACKEND  
> **Duración Estimada:** 2-3 horas

---

## 📋 Pre-requisitos

**El frontend ya hace:**
- ✅ Incluye `credentials: 'include'` en fetch
- ✅ NO manipula tokens manualmente
- ✅ Espera que backend maneje HttpOnly cookies
- ✅ NO accede a localStorage para auth tokens

**Tu backend debe:**
- ❌ Actualmente: Envía tokens en JSON + frontend guarda en localStorage
- ✅ Objetivo: Enviar tokens en HttpOnly cookies automáticamente

---

## ✅ Plan Implementación

### Fase 1: Crear Utils de Cookies
```python
# nurax_backend/utils/auth_utils.py (CREAR NUEVO)
```

### Fase 2: Actualizar Authentication Backend
```python
# nurax_backend/config/authentication.py (CREAR NUEVO)
```

### Fase 3: Configurar Django Settings
```python
# nurax_backend/settings.py (ACTUALIZAR)
```

### Fase 4: Actualizar Auth Endpoints
```python
# accounts/views.py (REFACTORIZAR login, refresh, logout)
```

### Fase 5: Testing
```bash
curl + DevTools verification
```

---

## 🛠️ IMPLEMENTACIÓN PASO-A-PASO

### PASO 1️⃣: Crear `nurax_backend/utils/auth_utils.py`

```python
"""
Utilidades de autenticación con HttpOnly Cookies (Seguro contra XSS)
"""

from datetime import timedelta
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings


def create_auth_response_with_cookies(user):
    """
    Crea tokens JWT y los retorna en HttpOnly cookies seguras.
    
    ✅ SEGURO:
    - HttpOnly: No accesible desde JavaScript (previene XSS)
    - Secure: Solo se envía por HTTPS en producción
    - SameSite=Strict: Previene CSRF
    
    Parámetros:
        user: Usuario autenticado (User model instance)
    
    Retorna:
        HttpResponse con cookies HTTP-only + JSON de usuario
    """
    
    # Generar tokens JWT
    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)
    
    # Preparar respuesta
    response_data = {
        'success': True,
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'name': getattr(user, 'name', ''),
            'role': getattr(user, 'role', 'cliente'),
        }
    }
    
    response = JsonResponse(response_data)
    
    # ✅ SET-COOKIE: access_token (corta duración)
    response.set_cookie(
        key='access_token',
        value=access,
        max_age=15 * 60,  # 15 minutos
        httponly=True,  # ← NO accesible desde JS
        secure=settings.SECURE_SSL_REDIRECT,  # True en producción
        samesite='Strict',  # Previene CSRF
        path='/api',  # Solo en endpoints /api
        domain=None,  # Dominio actual
    )
    
    # ✅ SET-COOKIE: refresh_token (larga duración)
    response.set_cookie(
        key='refresh_token',
        value=str(refresh),
        max_age=30 * 24 * 60 * 60,  # 30 días
        httponly=True,  # ← NO accesible desde JS
        secure=settings.SECURE_SSL_REDIRECT,
        samesite='Strict',
        path='/api/auth',  # Más restrictivo
        domain=None,
    )
    
    return response


def create_logout_response():
    """
    Crea respuesta que expira las cookies (logout).
    
    Establece Max-Age=0 para que navegador las elimine.
    """
    response = JsonResponse({'success': True, 'message': 'Logout successful'})
    
    # Expirar cookies (Max-Age=0)
    response.set_cookie(
        key='access_token',
        value='',
        max_age=0,
        httponly=True,
        secure=settings.SECURE_SSL_REDIRECT,
        samesite='Strict',
        path='/api',
    )
    
    response.set_cookie(
        key='refresh_token',
        value='',
        max_age=0,
        httponly=True,
        secure=settings.SECURE_SSL_REDIRECT,
        samesite='Strict',
        path='/api/auth',
    )
    
    return response


def create_refresh_response_with_cookies(user):
    """
    Genera nuevo access_token y lo retorna en HttpOnly cookie.
    (Se llama cuando token expira)
    """
    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)
    
    response = JsonResponse({
        'success': True,
        'message': 'Token refreshed successfully'
    })
    
    response.set_cookie(
        key='access_token',
        value=access,
        max_age=15 * 60,
        httponly=True,
        secure=settings.SECURE_SSL_REDIRECT,
        samesite='Strict',
        path='/api',
    )
    
    return response
```

---

### PASO 2️⃣: Crear `nurax_backend/config/authentication.py`

```python
"""
Backend de autenticación JWT desde HttpOnly cookies
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed as JWTAuthenticationFailed
import jwt
from django.conf import settings

User = get_user_model()


class CookieJWTAuthentication(BaseAuthentication):
    """
    Autentica usando JWT desde HttpOnly cookies (seguro contra XSS).
    
    Orden de intento:
    1. Cookie 'access_token' (preferido - seguro)
    2. Header 'Authorization: Bearer ...' (fallback para testing/mobile)
    """
    
    def authenticate(self, request):
        """Extrae y valida token de cookies o headers"""
        
        # Intento 1: Obtener token de HttpOnly cookie (preferido)
        auth_token = request.COOKIES.get('access_token')
        
        # Intento 2: Fallback a Authorization header (para testing)
        if not auth_token:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                auth_token = auth_header[7:]  # Remover 'Bearer '
        
        if not auth_token:
            return None  # No autenticado
        
        try:
            # Decodificar JWT
            payload = jwt.decode(
                auth_token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            # Obtener usuario
            user_id = payload.get('user_id')
            if not user_id:
                raise AuthenticationFailed('Token inválido: user_id no encontrado')
            
            user = User.objects.get(id=user_id)
            return (user, auth_token)
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expirado')
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f'Token inválido: {str(e)}')
        except User.DoesNotExist:
            raise AuthenticationFailed('Usuario no encontrado')


class CookieJWTRefreshAuthentication(BaseAuthentication):
    """
    Autentica usando refresh_token de HttpOnly cookies.
    (Se usa solo en endpoint /auth/refresh/)
    """
    
    def authenticate(self, request):
        """Extrae refresh_token de cookie"""
        
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return None
        
        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            user_id = payload.get('user_id')
            if not user_id:
                raise AuthenticationFailed('Refresh token inválido')
            
            user = User.objects.get(id=user_id)
            return (user, refresh_token)
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Refresh token expirado')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Refresh token inválido')
        except User.DoesNotExist:
            raise AuthenticationFailed('Usuario no encontrado')
```

---

### PASO 3️⃣: Actualizar `nurax_backend/settings.py`

```python
# settings.py

# ✅ AGREGAR ESTAS LÍNEAS:

# ─────────────────────────────────────────────────────────────
# 🔐 SEGURIDAD: HttpOnly Cookies Configuration
# ─────────────────────────────────────────────────────────────

# CSRF Protection
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True  # Solo HTTPS en producción
CSRF_COOKIE_SAMESITE = 'Strict'

# Session Cookies (si SE usa sessions)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'Strict'

# ─────────────────────────────────────────────────────────────
# REST Framework - Autenticación
# ─────────────────────────────────────────────────────────────

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'config.authentication.CookieJWTAuthentication',
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',  # Comentar
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# ─────────────────────────────────────────────────────────────
# HTTPS & Security Headers
# ─────────────────────────────────────────────────────────────

# En producción (settings.prod.py o environment variable):
SECURE_SSL_REDIRECT = True  # Redirige HTTP → HTTPS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'",),  # NO inline scripts
    'style-src': ("'self'", "'unsafe-inline'"),  # CSS puede ser inline
    'img-src': ("'self'", "data:", "https:"),
    'font-src': ("'self'",),
}

# ─────────────────────────────────────────────────────────────
# CORS - Solo dominio permitido
# ─────────────────────────────────────────────────────────────

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Dev frontend
    "https://nurax.com",
    "https://www.nurax.com",
]

# IMPORTANTE: Habilitar credentials
CORS_ALLOW_CREDENTIALS = True
```

---

### PASO 4️⃣: Actualizar `accounts/views.py` (Auth Endpoints)

```python
# accounts/views.py

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from utils.auth_utils import (
    create_auth_response_with_cookies,
    create_logout_response,
    create_refresh_response_with_cookies
)
from config.authentication import CookieJWTRefreshAuthentication
from .serializers import UserSerializer


class AuthViewSet(viewsets.ViewSet):
    """
    Endpoints de autenticación con HttpOnly cookies
    
    ✅ SEGURO: Todos los tokens en HttpOnly cookies
    """
    
    permission_classes = [AllowAny]
    
    # ───────────────────────────────────────────────────────────
    # 1️⃣ LOGIN - Retorna tokens en HttpOnly cookies
    # ───────────────────────────────────────────────────────────
    
    @action(detail=False, methods=['POST'], permission_classes=[AllowAny])
    def login(self, request):
        """
        POST /auth/login/
        
        Body: { "email": "user@example.com", "password": "..." }
        
        Retorna: HttpOnly cookies + JSON user data
        """
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email y password requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Autenticar usando email (ajustar según tu User model)
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(email=email)
            
            # Verificar contraseña
            if not user.check_password(password):
                return Response(
                    {'error': 'Credenciales inválidas'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # ✅ Retorna respuesta con HttpOnly cookies
            return create_auth_response_with_cookies(user)
            
        except User.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    # ───────────────────────────────────────────────────────────
    # 2️⃣ REFRESH - Genera nuevo access_token
    # ───────────────────────────────────────────────────────────
    
    @action(detail=False, methods=['POST'], permission_classes=[AllowAny])
    def refresh(self, request):
        """
        POST /auth/refresh/
        
        Cookie: refresh_token=...
        
        Retorna: Nuevo access_token en HttpOnly cookie
        """
        # Usar authentication especial para refresh_token
        auth = CookieJWTRefreshAuthentication()
        
        try:
            auth_tuple = auth.authenticate(request)
            if not auth_tuple:
                return Response(
                    {'error': 'Refresh token no encontrado'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            user, _ = auth_tuple
            
            # ✅ Generar nuevo access_token en cookie
            return create_refresh_response_with_cookies(user)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    # ───────────────────────────────────────────────────────────
    # 3️⃣ LOGOUT - Expira las cookies
    # ───────────────────────────────────────────────────────────
    
    @action(detail=False, methods=['POST', 'GET'])
    def logout(self, request):
        """
        POST /auth/logout/
        
        Expira cookies HttpOnly
        """
        return create_logout_response()
    
    # ───────────────────────────────────────────────────────────
    # 4️⃣ VERIFY - Verifica token actual
    # ───────────────────────────────────────────────────────────
    
    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def verify(self, request):
        """
        POST /auth/verify/
        
        Requiere: access_token en cookie
        
        Retorna: Confirmación de que token es válido
        """
        return Response({
            'success': True,
            'message': 'Token válido',
            'user_id': request.user.id
        })


# ───────────────────────────────────────────────────────────
# URLs - Registrar viewset
# ───────────────────────────────────────────────────────────

# accounts/urls.py
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet

router = DefaultRouter()
router.register('auth', AuthViewSet, basename='auth')

urlpatterns = router.urls
```

---

## 🧪 TESTING & VERIFICACIÓN

### Test 1: Verificar Login con Cookies

```bash
# 1. Login
curl -i -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }' \
  -c cookies.txt

# Debe retornar:
# HTTP/1.1 200 OK
# Set-Cookie: access_token=eyJ...; HttpOnly; Secure; SameSite=Strict; Path=/api
# Set-Cookie: refresh_token=eyJ...; HttpOnly; Secure; SameSite=Strict; Path=/api/auth
# { "success": true, "user": {...} }
```

### Test 2: Usar Token en Request

```bash
# 2. Request autenticado (cookies guardadas en -c cookies.txt)
curl -i -X GET http://localhost:8000/api/v1/accounts/users/me/ \
  -b cookies.txt

# Debe retornar:
# HTTP/1.1 200 OK
# { "id": 1, "email": "test@example.com", ... }
```

### Test 3: Token Refresh

```bash
# 3. Esperar a que token expire (15 min en dev), o modificar settings temporalmente

# Cuando frontend reciba 401, ejecuta:
curl -i -X POST http://localhost:8000/api/auth/refresh/ \
  -b cookies.txt

# Debe retornar:
# HTTP/1.1 200 OK
# Set-Cookie: access_token=eyJ...(NEW);
```

### Test 4: Logout

```bash
# 4. Logout
curl -i -X POST http://localhost:8000/api/auth/logout/ \
  -b cookies.txt

# Debe retornar:
# HTTP/1.1 200 OK
# Set-Cookie: access_token=; Max-Age=0;
# Set-Cookie: refresh_token=; Max-Age=0;
```

### Test 5: XSS Protection Verification

```javascript
// En DevTools → Console

// ✅ Verificar que localStorage NO tiene tokens
console.log(localStorage.getItem('access_token'))  // null
console.log(localStorage.getItem('refresh_token')) // null

// ✅ Verificar que cookies HttpOnly NO aparecen en document.cookie
console.log(document.cookie)  // Vacío (HttpOnly cookies no aparecen)

// ✅ Pero el navegador SÍ las envía automáticamente en requests
// (Esto se verifica en Network tab del DevTools)
```

---

## ✅ Checklist Implementación

- [ ] Creado `utils/auth_utils.py` con funciones de cookies
- [ ] Creado `config/authentication.py` con backends JWT
- [ ] Actualizado `settings.py` con CSRF, SESSION, CORS config  
- [ ] Refactorizado `accounts/views.py` - login, refresh, logout
- [ ] Testing manual: Login retorna Set-Cookie headers
- [ ] Testing: Request usa cookies automáticamente
- [ ] Testing: Token refresh funciona
- [ ] Testing: Logout expira cookies
- [ ] Testing: XSS injection no roba tokens
- [ ] DevTools: Verificar HttpOnly flag en cookies
- [ ] Deployment: HTTPS configurado en producción
- [ ] Documentation: Actualizar README con new auth flow

---

## 🚀 Deployment

### Producción (HTTPS)

```python
# environment: production

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True

# En settings.py o .env:
DEBUG = False
ALLOWED_HOSTS = ['nurax.com', 'www.nurax.com']
```

### Testing/Development (HTTP allowed)

```python
# environment: development

SECURE_SSL_REDIRECT = False  # ← Allow HTTP in dev
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# En settings.py:
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

---

## 📞 Troubleshooting

### Problema: 401 Unauthorized en requests

```python
# Causa: Cookie no se envía

# Solución:
# 1. Verificar CORS_ALLOW_CREDENTIALS = True
# 2. Verificar credentials: 'include' en frontend
# 3. Verificar dominio de cookie

# Debug:
print(request.COOKIES)  # Debe contener 'access_token'
```

### Problema: CORS Error

```python
# Causa: CORS_ALLOWED_ORIGINS no incluye frontend

# Solución:
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Dev frontend
    "https://nurax.com",      # Producción
]

CORS_ALLOW_CREDENTIALS = True  # ← CRÍTICA para cookies
```

### Problema: Cookies no persisten

```python
# Causa: SameSite=Strict demasiado restrictivo

# Verificar:
# - SameSite=Strict requiere same-site requests
# - Si frontend y backend en dominios diferentes, usar SameSite=Lax

response.set_cookie(..., samesite='Lax')  # Más permisivo
```

---

## 📚 Referencia OWASP

- [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [OWASP Authentication](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

---

**Siguiente:** Una vez implementado backend, correr pruebas end-to-end completas.
