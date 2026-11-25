from django.apps import AppConfig
from django.conf import settings


class DashboardsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.dashboards"
    verbose_name = "Dashboards y Visualizaciones Analíticas"

    def ready(self):
        # Compatibilidad Flask 3.x / Dash: inyectar secret_key en PseudoFlask
        # Esto previene el KeyError: 'SECRET_KEY' que ocurre cuando Dash intenta
        # obtener getattr(self.server, 'secret_key') en el servidor simulado de django-plotly-dash.
        try:
            from django_plotly_dash.dash_wrapper import PseudoFlask
            PseudoFlask.secret_key = settings.SECRET_KEY
        except ImportError:
            pass

        # Cargar los componentes y aplicaciones de Dash al iniciar Django
        try:
            import apps.dashboards.dash_apps.kpi_overview  # noqa: F401
        except ImportError:
            pass
