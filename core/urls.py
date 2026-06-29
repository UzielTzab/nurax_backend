from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from utils.auth_views import CustomTokenObtainPairView, CustomTokenRefreshView, LogoutView
from apps.accounts.views import OnboardingWizardView, StoreEmployeesView
from apps.carts.views import pusher_auth

urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),
    
    # API v1 - Arquitectura Final
    path('api/v1/stores/<uuid:store_id>/employees/', StoreEmployeesView.as_view(), name='store-employees-exact'),
    path('api/v1/onboarding/wizard/', OnboardingWizardView.as_view(), name='onboarding-wizard'),
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/accounts/', include('apps.accounts.urls')),
    path('api/v1/products/', include('apps.products.urls')),
    path('api/v1/expenses/', include('apps.expenses.urls')),
    path('api/v1/sales/', include('apps.sales.urls')),
    path('api/v1/carts/', include('apps.carts.urls')),
    path('api/v1/product-intelligence/', include('apps.product_intelligence.urls')),
    path('api/pusher/auth/', pusher_auth),
    
    # Authentication - 🔒 HttpOnly Cookies
    path('api/auth/login/',   CustomTokenObtainPairView.as_view(),  name='token_obtain'),
    path('api/auth/refresh/', CustomTokenRefreshView.as_view(),      name='token_refresh'),
    path('api/auth/logout/',  LogoutView.as_view(),                  name='logout'),
    
    # Documentation
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
]

# Servir archivos de media en desarrollo (en producción Cloudinary los sirve)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
