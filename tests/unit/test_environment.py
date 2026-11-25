"""
Pruebas de verificación del entorno base y configuración de Django.
"""

import pytest
from django.conf import settings


@pytest.mark.django_db
def test_django_settings_loaded():
    """Verifica que los settings principales de Django se carguen correctamente."""
    assert settings.SECRET_KEY is not None
    assert "apps.core.apps.CoreConfig" in settings.INSTALLED_APPS
    assert "django_plotly_dash.apps.DjangoPlotlyDashConfig" in settings.INSTALLED_APPS


def test_base_directory_exists():
    """Verifica que los directorios del proyecto existan."""
    assert (settings.BASE_DIR / "apps").exists()
    assert (settings.BASE_DIR / "templates").exists()
    assert (settings.BASE_DIR / "static").exists()
    assert (settings.BASE_DIR / "logs").exists()
