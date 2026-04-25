from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from utils.auth_views import CustomTokenObtainPairView, CustomTokenRefreshView, LogoutView
from apps.accounts.views import OnboardingWizardView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API v1 - ARCHITECTURE_V2 (apps in apps/ folder)
    path('api/v1/accounts/', include('apps.accounts.urls')),
    path('api/v1/products/', include('apps.products.urls')),
    path('api/v1/sales/', include('apps.sales.urls')),
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/expenses/', include('apps.expenses.urls')),
    path('api/v1/carts/', include('apps.carts.urls')),
    path('api/v1/onboarding/wizard/', OnboardingWizardView.as_view(), name='onboarding-wizard'),
    
    # Authentication - 🔒 HttpOnly Cookies
    path('api/auth/login/',   CustomTokenObtainPairView.as_view(),  name='token_obtain'),
    path('api/auth/logout/',  LogoutView.as_view(),                  name='logout'),
    path('api/auth/refresh/', CustomTokenRefreshView.as_view(),      name='token_refresh'),
    
    # Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Servir archivos de media en desarrollo (en producción Cloudinary los sirve)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
