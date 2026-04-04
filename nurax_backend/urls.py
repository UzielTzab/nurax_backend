from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API v1 - ARCHITECTURE_V2
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/products/', include('products.urls')),
    path('api/v1/sales/', include('sales.urls')),
    path('api/v1/inventory/', include('inventory.urls')),
    path('api/v1/expenses/', include('expenses.urls')),
    path('api/v1/carts/', include('carts.urls')),
    
    # Authentication
    path('api/auth/login/',   TokenObtainPairView.as_view(),  name='token_obtain'),
    path('api/auth/refresh/', TokenRefreshView.as_view(),     name='token_refresh'),
    
    # Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Legacy API endpoints - DEPRECATED
    path('api/', include('api.urls')),
]
