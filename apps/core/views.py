"""
Vistas para la Pantalla Principal (Landing explicativa) y Dashboard del sistema.
"""

from typing import Any, Dict
from django.views.generic import TemplateView
from apps.documents.models import UploadedDocument, CommercialRecord
from apps.automations.models import ExecutionLog
from apps.automations.scheduler import get_registered_jobs_info


class LandingPageView(TemplateView):
    """
    Pantalla principal de bienvenida que expone:
    - Explicación de la arquitectura y funcionamiento del programa.
    - Flujo ETL, automatización APScheduler y analítica reactiva Dash.
    - Acceso directo y opciones para Iniciar Sesión.
    """
    template_name = "core/landing.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["total_documents"] = UploadedDocument.objects.count()
        context["completed_documents"] = UploadedDocument.objects.filter(status="COMPLETED").count()
        context["total_records"] = CommercialRecord.objects.count()
        context["scheduled_jobs"] = get_registered_jobs_info()
        return context


class DashboardView(TemplateView):
    """
    Vista principal que consolida el estado global de la plataforma:
    - Indicadores totales (documentos, registros, tareas).
    - Últimos registros procesados.
    - Historial reciente de automatizaciones.
    """
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["total_documents"] = UploadedDocument.objects.count()
        context["completed_documents"] = UploadedDocument.objects.filter(status="COMPLETED").count()
        context["total_records"] = CommercialRecord.objects.count()
        context["scheduled_jobs"] = get_registered_jobs_info()
        context["recent_logs"] = ExecutionLog.objects.all()[:8]
        context["recent_documents"] = UploadedDocument.objects.all()[:5]
        return context
