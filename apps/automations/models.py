"""
Modelos de datos para el seguimiento, registro y orquestación de automatizaciones.
"""

from django.db import models
from django.utils import timezone


class AutomationJob(models.Model):
    """
    Representa una tarea programada o recurrente registrada en el sistema.
    """
    JOB_TYPES = [
        ("ETL_AUDIT", "Auditoría y Validación ETL"),
        ("HOURLY_SYNC", "Sincronización Periódica de Métricas"),
        ("DAILY_REPORT", "Generación de Reporte Diario Consolidado"),
        ("DATA_CLEANUP", "Limpieza de Archivos Temporales"),
    ]

    name = models.CharField(max_length=150, unique=True, verbose_name="Nombre de la Tarea")
    job_type = models.CharField(max_length=50, choices=JOB_TYPES, verbose_name="Tipo de Tarea")
    cron_expression = models.CharField(
        max_length=50,
        verbose_name="Expresión Cron / Intervalo",
        help_text="Ejemplo: '*/15 * * * *' para cada 15 minutos o '0 8 * * *' para diario a las 8am.",
    )
    is_active = models.BooleanField(default=True, verbose_name="¿Activa?")
    last_run = models.DateTimeField(null=True, blank=True, verbose_name="Última Ejecución")
    next_run = models.DateTimeField(null=True, blank=True, verbose_name="Próxima Ejecución")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Tarea Programada"
        verbose_name_plural = "Tareas Programadas"
        ordering = ["name"]

    def __str__(self) -> str:
        status = "ACTIVA" if self.is_active else "INACTIVA"
        return f"{self.name} [{status}] ({self.cron_expression})"


class ExecutionLog(models.Model):
    """
    Registro histórico de cada corrida de automatización, duraciones, estado y errores.
    """
    STATUS_CHOICES = [
        ("RUNNING", "En Ejecución"),
        ("SUCCESS", "Completada Exitosamente"),
        ("FAILED", "Fallida"),
    ]

    TRIGGER_CHOICES = [
        ("SCHEDULER", "Programador APScheduler"),
        ("MANUAL", "Ejecución Manual por Usuario"),
        ("FILE_UPLOAD", "Evento de Carga de Archivo"),
    ]

    job = models.ForeignKey(
        AutomationJob,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs",
        verbose_name="Tarea Asociada",
    )
    job_name = models.CharField(max_length=150, verbose_name="Nombre del Proceso")
    triggered_by = models.CharField(max_length=20, choices=TRIGGER_CHOICES, default="SCHEDULER", verbose_name="Disparado Por")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="RUNNING", verbose_name="Estado")
    start_time = models.DateTimeField(default=timezone.now, verbose_name="Inicio")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Fin")
    duration_seconds = models.FloatField(default=0.0, verbose_name="Duración (segundos)")
    records_processed = models.PositiveIntegerField(default=0, verbose_name="Registros Procesados")
    output_message = models.TextField(blank=True, default="", verbose_name="Resultado / Salida")
    error_trace = models.TextField(blank=True, default="", verbose_name="Traza de Error")

    class Meta:
        verbose_name = "Historial de Ejecución"
        verbose_name_plural = "Historial de Ejecuciones"
        ordering = ["-start_time"]

    def __str__(self) -> str:
        return f"[{self.start_time.strftime('%Y-%m-%d %H:%M:%S')}] {self.job_name} - {self.status}"
