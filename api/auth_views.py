"""
Vistas de Autenticación personalizada para HttpOnly Cookies.

Proporciona un endpoint de login que retorna el JWT en una HttpOnly cookie
en lugar de en el response body (OWASP Security Best Practice).
"""

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer que personaliza la respuesta del login."""
    
    @classmethod
    def get_token(cls, user):
        """Obtiene el token para el usuario."""
        token = super().get_token(user)
        # Aquí puedes agregar claims personalizados si lo necesitas:
        # token['name'] = user.name
        # token['email'] = user.email
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista de login personalizada que retorna JWT en HttpOnly cookie.
    
    Endpoint: POST /api/auth/login/
    Request: {"email": "user@example.com", "password": "password"}
    Response: 
        {
            "message": "Login exitoso",
            "user": {
                "id": 1,
                "email": "user@example.com",
                "username": "username",
                "name": "User Name",
                "role": "owner"
            }
        }
        + Set-Cookie: access_token=JWT_VALUE; HttpOnly; Secure; SameSite=Strict
        + Set-Cookie: refresh_token=REFRESH_JWT; HttpOnly; Secure; SameSite=Strict
    
    Security:
    - Token almacenado en HttpOnly cookie (no accesible a JavaScript)
    - Secure flag en producción (HTTPS only)
    - SameSite=Strict para CSRF protection
    """
    
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        """Override post para retornar tokens en cookies."""
        # 1. Validar credenciales con el serializer standard
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response(
                {'error': 'Credenciales inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # 2. Obtener tokens del serializer
        tokens = serializer.validated_data
        access_token = tokens.get('access')
        refresh_token = tokens.get('refresh')
        
        # 3. Obtener datos del usuario para incluir en respuesta
        user = serializer.user
        response_data = {
            'message': 'Login exitoso',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'name': user.name or f"{user.first_name} {user.last_name}".strip(),
                'role': user.role,
                'avatar_url': user.avatar_url,
            }
        }
        
        # 4. Crear response
        response = Response(response_data, status=status.HTTP_200_OK)
        
        # 5. Establecer cookies HttpOnly
        # Access token (corta duración - 8 horas)
        response.set_cookie(
            key='access_token',
            value=access_token,
            max_age=8 * 60 * 60,  # 8 horas (debe coincidir con ACCESS_TOKEN_LIFETIME en settings)
            httponly=True,         # 🛡️ No accesible a JavaScript
            secure=not settings.DEBUG,  # ✅ True en producción (HTTPS)
            samesite='Strict',     # 🛡️ CSRF protection
            path='/'
        )
        
        # Refresh token (larga duración - 30 días)
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            max_age=30 * 24 * 60 * 60,  # 30 días
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Strict',
            path='/'
        )
        
        return response


class CustomTokenRefreshView(TokenRefreshView):
    """
    Vista de refresh personalizada que lee y retorna refresh token desde cookies.
    
    Endpoint: POST /api/auth/refresh/
    Cookies (auto-enviada): refresh_token=REFRESH_JWT
    Response: {"message": "Token refreshed"} + nuevo access_token cookie
    
    Security:
    - Lee refresh_token de cookie automáticamente
    - Retorna nuevo access_token en cookie
    """
    
    def post(self, request, *args, **kwargs):
        """Override post para leer refresh_token de cookie."""
        # 1. Obtener refresh_token de la cookie
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response(
                {'error': 'refresh_token no encontrado en cookies'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # 2. Crear request.data con el refresh token
        request.data._mutable = True  # Si es immutable, hacerlo mutable
        request.data['refresh'] = refresh_token
        
        # 3. Validar con serializer standard
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as exc:
            return Response(
                {'error': 'Token de refresco inválido o expirado'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # 4. Obtener nuevo access token
        new_access_token = serializer.validated_data.get('access')
        
        # 5. Crear response y setear nueva cookie
        response = Response(
            {'message': 'Token refrescado exitosamente'},
            status=status.HTTP_200_OK
        )
        
        response.set_cookie(
            key='access_token',
            value=new_access_token,
            max_age=8 * 60 * 60,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Strict',
            path='/'
        )
        
        return response


class LogoutView(TokenObtainPairView):
    """
    Vista de logout que limpia las cookies.
    
    Endpoint: POST /api/auth/logout/
    Response: {"message": "Sesión cerrada"}
    Set-Cookie: access_token=; Max-Age=0; HttpOnly
    Set-Cookie: refresh_token=; Max-Age=0; HttpOnly
    """
    
    def post(self, request, *args, **kwargs):
        """Limpia cookies y cierra sesión."""
        response = Response(
            {'message': 'Sesión cerrada correctamente'},
            status=status.HTTP_200_OK
        )
        
        # Eliminar cookies (delete_cookie es simple en Django)
        response.delete_cookie('access_token', path='/')
        response.delete_cookie('refresh_token', path='/')
        
        return response

