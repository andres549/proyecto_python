"""
Registro de modelos de automatización en el panel administrativo de Django.
"""

from django.contrib import admin
from apps.automations.models import AutomationJob, ExecutionLog


@admin.register(AutomationJob)
class AutomationJobAdmin(admin.ModelAdmin):
    list_display = ("name", "job_type", "cron_expression", "is_active", "last_run", "next_run")
    list_filter = ("job_type", "is_active")
    search_fields = ("name",)


@admin.register(ExecutionLog)
class ExecutionLogAdmin(admin.ModelAdmin):
    list_display = (
        "job_name",
        "triggered_by",
        "status",
        "start_time",
        "duration_seconds",
        "records_processed",
    )
    list_filter = ("status", "triggered_by", "start_time")
    search_fields = ("job_name", "output_message", "error_trace")
    readonly_fields = ("start_time", "end_time", "duration_seconds")
