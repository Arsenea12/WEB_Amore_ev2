"""
URL configuration for mysite project.
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("", include("amore.urls")),
    path("admin/", admin.site.urls),
    path("__debug__/", include("debug_toolbar.urls")),

    path("accounts/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),

    # API RESTful (Unidad 3)
    path("api/", include("amore.api_urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("api-auth/", include("rest_framework.urls")),  # vista navegable de DRF (login/logout en el browser)
]
