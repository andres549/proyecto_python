"""
Pruebas de integración de las rutas y vistas web principales de Django.
"""

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_landing_view(client):
    """Verifica que la pantalla principal responda exitosamente."""
    url = reverse("core:landing")
    response = client.get(url)
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Portal Principal" in content
    assert "Iniciar Sesión" in content
    assert "APScheduler" in content


@pytest.mark.django_db
def test_dashboard_view(client):
    """Verifica que el dashboard general responda con código HTTP 200."""
    url = reverse("core:dashboard")
    response = client.get(url)
    assert response.status_code == 200
    assert "APScheduler" in response.content.decode("utf-8")


@pytest.mark.django_db
def test_documents_view(client):
    """Verifica que el gestor de documentos cargue correctamente."""
    url = reverse("documents:list")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_automations_view(client):
    """Verifica que el centro de control de automatizaciones responda con código HTTP 200."""
    url = reverse("automations:control_panel")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_analytics_view(client):
    """Verifica que la vista contenedora de Dash responda exitosamente."""
    url = reverse("dashboards:analytics")
    response = client.get(url)
    assert response.status_code == 200
