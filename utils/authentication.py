"""
Autenticación con HttpOnly Cookies para NURAX.

Proporciona CookieJWTAuthentication que lee tokens JWT desde HttpOnly cookies
en lugar de headers Authorization, protegiendo contra ataques XSS.

OWASP Security Best Practice: Tokens en HttpOnly cookies, no accesibles a JavaScript.
"""

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class CookieJWTAuthentication(JWTAuthentication):
    """
    Autenticación JWT que lee el token desde una HttpOnly cookie.
    
    Ventajas sobre localStorage (OWASP compliant):
    - ✅ Token NO accesible a JavaScript (protección XSS)
    - ✅ Browser envía automáticamente en cada request
    - ✅ Secure flag: solo via HTTPS en producción
    - ✅ SameSite=Strict: CSRF protection
    
    Usage en settings.py:
    ```
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'utils.authentication.CookieJWTAuthentication',
        ),
    }
    ```
    """
    
    def authenticate(self, request):
        """
        Lee el JWT desde la cookie 'access_token' en lugar del header Authorization.
        
        Retorna:
            (user, token) si la autenticación es exitosa
            None si no hay cookie (permite AnonymousUser)
            AuthenticationFailed si la cookie está corrupta
        """
        # 1. Intentar obtener el token de la cookie
        token = request.COOKIES.get('access_token')
        
        # Si no hay cookie, retornar None para permitir AnonymousUser
        if not token:
            return None
        
        # 2. Intentar validar el token
        try:
            # Usar el validador de JWTAuthentication del simplejwt
            validated_token = self.get_validated_token(token)
            # Obtener el usuario del token
            user = self.get_user(validated_token)
            return (user, validated_token)
        except InvalidToken as exc:
            raise AuthenticationFailed(f'Token inválido o expirado: {exc}') from exc
        except TokenError as exc:
            raise AuthenticationFailed(f'Error procesando token: {exc}') from exc
        except Exception as exc:
            raise AuthenticationFailed(f'Error de autenticación: {exc}') from exc
