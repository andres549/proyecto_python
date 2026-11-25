"""
Enrutamiento principal de la aplicación.

Conecta:
- Panel administrativo de Django (/admin/).
- Rutas internas del motor reactivo Dash (/django_plotly_dash/).
- Módulos funcionales de la aplicación:
  * /            -> apps.core (Dashboard principal)
  * /auth/       -> apps.authentication (Login/Logout)
  * /documents/  -> apps.documents (Gestor de archivos y ETL)
  * /automations/-> apps.automations (Centro de control APScheduler)
  * /dashboards/ -> apps.dashboards (Vistas analíticas Plotly Dash)
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Panel de administración de Django
    path("admin/", admin.site.urls),

    # Rutas internas requeridas por django-plotly-dash para servir componentes y callbacks
    path("django_plotly_dash/", include("django_plotly_dash.urls")),

    # Módulos de la arquitectura modular
    path("", include("apps.core.urls")),
    path("auth/", include("apps.authentication.urls")),
    path("documents/", include("apps.documents.urls")),
    path("automations/", include("apps.automations.urls")),
    path("dashboards/", include("apps.dashboards.urls")),
]

# Servir archivos multimedia en modo de desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
