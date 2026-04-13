"""
Custom authentication views with HttpOnly cookie support.
Implements JWT authentication using secure HttpOnly cookies (OWASP best practice).
"""
from datetime import timedelta
from django.http import JsonResponse
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom login endpoint that returns JWT tokens in HttpOnly cookies.
    
    POST /api/auth/login/
    Body: { "email": "user@example.com", "password": "password" }
    
    Response: SET-COOKIE headers with access_token and refresh_token (HttpOnly, Secure, SameSite=Strict)
    """
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            tokens = response.data
            access_token = tokens['access']
            refresh_token = tokens['refresh']
            
            # Set HttpOnly cookies with secure flags
            response.set_cookie(
                'access_token',
                access_token,
                max_age=int(timedelta(hours=8).total_seconds()),  # 8 hours
                httponly=True,
                secure=settings.SESSION_COOKIE_SECURE,
                samesite=settings.SESSION_COOKIE_SAMESITE,
                path='/',
            )
            response.set_cookie(
                'refresh_token',
                refresh_token,
                max_age=int(timedelta(days=7).total_seconds()),  # 7 days
                httponly=True,
                secure=settings.SESSION_COOKIE_SECURE,
                samesite=settings.SESSION_COOKIE_SAMESITE,
                path='/',
            )
            
            # Remove tokens from response body (they're in cookies now)
            response.data = {'detail': 'Login successful'}
            response.status_code = 200
        
        return response


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom refresh endpoint that reads and sets tokens in HttpOnly cookies.
    
    POST /api/auth/refresh/
    Cookies: refresh_token (sent automatically by browser)
    
    Response: New access_token in SET-COOKIE header
    """
    
    def post(self, request, *args, **kwargs):
        # Read refresh token from cookie
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response(
                {'detail': 'No refresh token in cookies'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Put it in request.data for parent class
        request.data._mutable = True
        request.data['refresh'] = refresh_token
        
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            new_access_token = response.data.get('access')
            
            # Set new access token in cookie
            response.set_cookie(
                'access_token',
                new_access_token,
                max_age=int(timedelta(hours=8).total_seconds()),
                httponly=True,
                secure=settings.SESSION_COOKIE_SECURE,
                samesite=settings.SESSION_COOKIE_SAMESITE,
                path='/',
            )
            
            # Remove token from response body
            response.data = {'detail': 'Token refreshed'}
        
        return response


class LogoutView(APIView):
    """
    Custom logout endpoint that deletes HttpOnly cookies.
    
    POST /api/auth/logout/
    Cookies: access_token, refresh_token (cleared automatically)
    
    Response: Cookies deleted with Max-Age=0
    """
    
    def post(self, request, *args, **kwargs):
        response = Response(
            {'detail': 'Logout successful'},
            status=status.HTTP_200_OK
        )
        
        # Delete cookies by setting Max-Age=0
        response.delete_cookie(
            'access_token',
            samesite=settings.SESSION_COOKIE_SAMESITE,
            secure=settings.SESSION_COOKIE_SECURE,
            path='/',
        )
        response.delete_cookie(
            'refresh_token',
            samesite=settings.SESSION_COOKIE_SAMESITE,
            secure=settings.SESSION_COOKIE_SECURE,
            path='/',
        )
        
        return response
