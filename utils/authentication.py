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
from django.contrib.auth import get_user_model

User = get_user_model()


class CookieJWTAuthentication(JWTAuthentication):
    """
    Autenticación JWT que lee el token desde una HttpOnly cookie.
    
    Ventajas sobre localStorage (OWASP compliant):
    - ✅ Token NO accesible a JavaScript (protección XSS)
    - ✅ Browser envía automáticamente en cada request
    - ✅ Secure flag: solo via HTTPS en producción
    - ✅ SameSite=Strict: CSRF protection
    
    Usa UUID del usuario como 'sub' en el token, no email.
    Esto permite que el usuario pueda cambiar su email sin invalidar tokens.
    
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
            # Obtener el usuario del token usando UUID en lugar de email
            user = self.get_user(validated_token)
            return (user, validated_token)
        except InvalidToken as exc:
            raise AuthenticationFailed(f'Token inválido o expirado: {exc}') from exc
        except TokenError as exc:
            raise AuthenticationFailed(f'Error procesando token: {exc}') from exc
        except Exception as exc:
            raise AuthenticationFailed(f'Error de autenticación: {exc}') from exc
    
    def get_user(self, validated_token):
        """
        Obtiene el usuario del token usando UUID o email (backward compatible).
        
        Override del método de JWTAuthentication para:
        1. Primero intenta buscar por 'user_id' (nuevos tokens)
        2. Si no existe, busca por 'sub' que es el USERNAME_FIELD (email) (tokens antiguos)
        
        Esto permite compatibilidad con tokens generados antes y después del cambio.
        """
        # Intentar obtener por user_id (nuevos tokens)
        user_id = validated_token.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                if not user.is_active:
                    raise InvalidToken('Usuario inactivo')
                return user
            except User.DoesNotExist:
                raise InvalidToken('Usuario no encontrado')
        
        # Fallback: buscar por 'sub' (EMAIL) para tokens antiguos
        # Esto mantiene compatibilidad con tokens generados antes del cambio
        username = validated_token.get('sub')  # Típicamente es el email
        if not username:
            raise InvalidToken('Token no contiene identificador')
        
        try:
            # Buscar por USERNAME_FIELD (email)
            user = User.objects.get(email=username)
            if not user.is_active:
                raise InvalidToken('Usuario inactivo')
            return user
        except User.DoesNotExist:
            # Si el email anterior ya no existe, informar claramente
            raise InvalidToken(
                'Usuario con ese email no encontrado. '
                'Por favor inicie sesión nuevamente para obtener un token actualizado.'
            )
