"""
Orquestador de tareas en segundo plano con APScheduler.
"""

from typing import List, Dict, Any, Optional
import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger("automations")

# Instancia global del programador
_scheduler: Optional[BackgroundScheduler] = None


def get_scheduler() -> BackgroundScheduler:
    """Retorna la instancia activa del scheduler o crea una nueva."""
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler(
            daemon=True,
            timezone="America/Bogota",
            job_defaults={
                "coalesce": True,            # Combinar ejecuciones acumuladas si hubo retraso
                "max_instances": 1,           # Impedir ejecuciones paralelas de la misma tarea
                "misfire_grace_time": 60,     # Margen de 60 segundos si el servidor estuvo ocupado
            },
        )
    return _scheduler


def start_scheduler() -> None:
    """
    Inicializa el planificador de tareas controlando el recargador de Django para evitar duplicaciones.
    """
    # En desarrollo con 'runserver', solo inicializar en el proceso secundario (RUN_MAIN == 'true')
    # Si no estamos en runserver con reload (por ejemplo test o producción), se inicia directamente
    is_reloader_child = os.environ.get("RUN_MAIN") == "true"
    is_development_server = "runserver" in os.sys.argv

    if is_development_server and not is_reloader_child:
        logger.debug("Omitiendo inicio del scheduler en el proceso watcher de Django.")
        return

    scheduler = get_scheduler()

    if scheduler.running:
        logger.info("APScheduler ya se encuentra en ejecución.")
        return

    from apps.automations.tasks import (
        task_audit_pending_documents,
        task_generate_daily_consolidated_report,
    )

    # Registro de Tarea 1: Verificación de documentos pendientes cada 1 minuto
    scheduler.add_job(
        func=task_audit_pending_documents,
        trigger=IntervalTrigger(minutes=1),
        id="job_audit_pending_documents",
        name="Auditoría Continua de Documentos",
        replace_existing=True,
    )

    # Registro de Tarea 2: Reporte consolidado cada día a las 23:00 (o cada 6 horas)
    scheduler.add_job(
        func=task_generate_daily_consolidated_report,
        trigger=CronTrigger(hour="23", minute="0"),
        id="job_daily_consolidated_report",
        name="Reporte Diario Consolidado",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("APScheduler iniciado exitosamente con %d tareas registradas.", len(scheduler.get_jobs()))


def get_registered_jobs_info() -> List[Dict[str, Any]]:
    """Devuelve metadatos de las tareas registradas actualmente en el scheduler."""
    scheduler = get_scheduler()
    info = []
    for job in scheduler.get_jobs():
        info.append(
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job.next_run_time else "En pausa",
                "trigger": str(job.trigger),
            }
        )
    return info
