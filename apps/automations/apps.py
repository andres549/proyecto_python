from django.apps import AppConfig


class AutomationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.automations"
    verbose_name = "Automatización y Tareas Programadas"

    def ready(self):
        # Iniciar el planificador de tareas APScheduler cuando Django esté listo
        from apps.automations.scheduler import start_scheduler
        start_scheduler()
