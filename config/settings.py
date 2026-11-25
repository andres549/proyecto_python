"""
Configuración principal de Django para la plataforma empresarial.

Este archivo centraliza todos los parámetros del sistema:
- Carga de variables de entorno con python-dotenv.
- Configuración de seguridad (Secret Key, Debug, Allowed Hosts).
- Registro de aplicaciones del proyecto y de terceros (DjangoPlotlyDash).
- Configuración del motor de plantillas y archivos estáticos/media.
- Integración con base de datos (SQLite / PostgreSQL).
- Sistema de Logging estructurado y rotativo.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Ruta raíz del proyecto (directorio que contiene manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno desde el archivo .env
load_dotenv(BASE_DIR / ".env")

# ==============================================================================
# SEGURIDAD
# ==============================================================================

# Clave secreta criptográfica (leída desde .env con valor por defecto seguro para dev)
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-enterprise-automation-key-change-in-production-2026",
)

# Modo Debug (False en producción)
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() in ("true", "1", "yes")

# Hosts permitidos
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]").split(",")
    if host.strip()
]

# Permitir incrustar Dash mediante iframe en el mismo origen (requisito de django-plotly-dash)
X_FRAME_OPTIONS = "SAMEORIGIN"

# ==============================================================================
# APLICACIONES INSTALADAS
# ==============================================================================

INSTALLED_APPS = [
    # Aplicaciones nativas de Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Soporte para Dashboards interactivos sin JavaScript manual
    "django_plotly_dash.apps.DjangoPlotlyDashConfig",
    "dpd_components",

    # Aplicaciones modulares del proyecto
    "apps.core.apps.CoreConfig",
    "apps.authentication.apps.AuthenticationConfig",
    "apps.documents.apps.DocumentsConfig",
    "apps.automations.apps.AutomationsConfig",
    "apps.dashboards.apps.DashboardsConfig",
]

# ==============================================================================
# MIDDLEWARE
# ==============================================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # Middlewares requeridos por django-plotly-dash para inyectar recursos y redirecciones
    "django_plotly_dash.middleware.BaseMiddleware",
    "django_plotly_dash.middleware.ExternalRedirectionMiddleware",
]

ROOT_URLCONF = "config.urls"

# ==============================================================================
# PLANTILLAS (TEMPLATES)
# ==============================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ==============================================================================
# BASE DE DATOS
# ==============================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ==============================================================================
# VALIDACIÓN DE CONTRASEÑAS
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ==============================================================================
# INTERNACIONALIZACIÓN Y HORARIOS
# ==============================================================================

LANGUAGE_CODE = "es-es"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

# ==============================================================================
# ARCHIVOS ESTÁTICOS Y SUBIDAS (MEDIA)
# ==============================================================================

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Buscadores de archivos estáticos requeridos para servir componentes Dash
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "django_plotly_dash.finders.DashAssetFinder",
    "django_plotly_dash.finders.DashComponentFinder",
    "django_plotly_dash.finders.DashAppDirectoryFinder",
]

# Configuración de carga y almacenamiento de medios
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Redirecciones de autenticación
LOGIN_URL = "authentication:login"
LOGIN_REDIRECT_URL = "core:dashboard"
LOGOUT_REDIRECT_URL = "authentication:login"

# ==============================================================================
# CONFIGURACIÓN DE PLOTLY DASH
# ==============================================================================

PLOTLY_COMPONENTS = [
    "dash",
    "dash_bootstrap_components",
    "dpd_components",
]

PLOTLY_DASH = {
    "ws_route": "dpd/ws/channel",
    "insert_demo_migrations": False,
    "http_poke_enabled": True,
    "view_decorator": None,
    "cache_arguments": False,
}

# ==============================================================================
# LOGGING ESTRUCTURADO Y ROTATIVO
# ==============================================================================

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] [{levelname}] [{name}:{lineno}] - {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "[{levelname}] - {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "app_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOGS_DIR / "app.log"),
            "maxBytes": 5 * 1024 * 1024,  # 5 MB por archivo
            "backupCount": 5,             # Mantener 5 copias de respaldo
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOGS_DIR / "errors.log"),
            "level": "ERROR",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        "automation_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOGS_DIR / "automation.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
            "encoding": "utf-8",
        },
    },
    "root": {
        "handlers": ["console", "app_file", "error_file"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console", "app_file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "automations": {
            "handlers": ["console", "automation_file", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "documents": {
            "handlers": ["console", "app_file", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
