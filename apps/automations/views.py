"""
Vistas para el centro de control de automatizaciones y monitoreo de APScheduler.
"""

from pathlib import Path
from django.views.generic import View, TemplateView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.http import FileResponse, Http404

from apps.automations.models import ExecutionLog
from apps.automations.scheduler import get_registered_jobs_info
from apps.automations.tasks import (
    task_audit_pending_documents,
    task_generate_daily_consolidated_report,
)


class AutomationControlView(TemplateView):
    """
    Panel central de control:
    - Estado de las tareas programadas activas.
    - Acciones de disparo manual inmediato.
    - Historial detallado de ejecuciones, duraciones y trazas.
    - Archivos de reportes generados listos para descarga.
    """
    template_name = "automations/control_panel.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["scheduled_jobs"] = get_registered_jobs_info()
        context["execution_logs"] = ExecutionLog.objects.all()[:30]

        # Listar reportes generados en el directorio media/reports/
        reports_dir = settings.MEDIA_ROOT / "reports"
        reports_list = []
        if reports_dir.exists():
            for p in sorted(reports_dir.glob("*.xlsx"), key=lambda f: f.stat().st_mtime, reverse=True):
                reports_list.append({
                    "name": p.name,
                    "size_bytes": p.stat().st_size,
                    "modified": p.stat().st_mtime,
                    "url": f"{settings.MEDIA_URL}reports/{p.name}",
                })
        context["generated_reports"] = reports_list[:10]
        return context


class TriggerJobManualView(View):
    """
    Dispara una tarea en segundo plano bajo demanda manual del usuario.
    """
    def post(self, request, job_type: str):
        if job_type == "audit":
            success, msg, count = task_audit_pending_documents(trigger="MANUAL")
            if success:
                messages.success(request, f"Tarea ejecutada manualmente: {msg}")
            else:
                messages.error(request, f"Fallo al ejecutar tarea: {msg}")

        elif job_type == "report":
            success, msg, count = task_generate_daily_consolidated_report(trigger="MANUAL")
            if success:
                messages.success(request, f"Reporte generado exitosamente: {msg}")
            else:
                messages.error(request, f"Error al generar reporte: {msg}")
        else:
            messages.warning(request, f"Tipo de tarea desconocido: '{job_type}'")

        return redirect("automations:control_panel")
