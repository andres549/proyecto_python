"""
Tareas automatizadas ejecutadas por APScheduler o disparadas manualmente.
"""

from typing import Tuple
from pathlib import Path
import time
import pandas as pd
from django.utils import timezone
from django.conf import settings
import logging

from apps.documents.models import UploadedDocument, CommercialRecord
from apps.documents.services import process_document_etl
from apps.automations.models import ExecutionLog, AutomationJob
from services.excel_processor import generate_styled_excel_report

logger = logging.getLogger("automations")


def task_audit_pending_documents(trigger: str = "SCHEDULER") -> Tuple[bool, str, int]:
    """
    Tarea 1: Busca documentos en estado 'PENDING' y ejecuta el pipeline ETL.
    """
    start_time = timezone.now()
    t0 = time.time()
    job_name = "Auditoría y Validación ETL"

    log_entry = ExecutionLog.objects.create(
        job_name=job_name,
        triggered_by=trigger,
        status="RUNNING",
        start_time=start_time,
    )

    try:
        pending_docs = UploadedDocument.objects.filter(status="PENDING")
        total_processed_records = 0

        if not pending_docs.exists():
            duration = round(time.time() - t0, 3)
            msg = "No se encontraron documentos pendientes para auditar."
            log_entry.status = "SUCCESS"
            log_entry.end_time = timezone.now()
            log_entry.duration_seconds = duration
            log_entry.output_message = msg
            log_entry.save()
            logger.info("%s: %s", job_name, msg)
            return True, msg, 0

        for doc in pending_docs:
            success, result_msg = process_document_etl(doc)
            if success:
                total_processed_records += doc.row_count

        duration = round(time.time() - t0, 3)
        msg = f"Se procesaron {pending_docs.count()} documento(s) con un total de {total_processed_records} registros."
        log_entry.status = "SUCCESS"
        log_entry.end_time = timezone.now()
        log_entry.duration_seconds = duration
        log_entry.records_processed = total_processed_records
        log_entry.output_message = msg
        log_entry.save()

        logger.info("%s completado exitosamente: %s", job_name, msg)
        return True, msg, total_processed_records

    except Exception as exc:
        duration = round(time.time() - t0, 3)
        err_msg = f"Error en ejecución de {job_name}: {str(exc)}"
        log_entry.status = "FAILED"
        log_entry.end_time = timezone.now()
        log_entry.duration_seconds = duration
        log_entry.error_trace = err_msg
        log_entry.save()
        logger.exception(err_msg)
        return False, err_msg, 0


def task_generate_daily_consolidated_report(trigger: str = "SCHEDULER") -> Tuple[bool, str, int]:
    """
    Tarea 2: Genera un reporte Excel estilizado con todos los registros comerciales actuales.
    """
    start_time = timezone.now()
    t0 = time.time()
    job_name = "Generación de Reporte Diario Consolidado"

    log_entry = ExecutionLog.objects.create(
        job_name=job_name,
        triggered_by=trigger,
        status="RUNNING",
        start_time=start_time,
    )

    try:
        records_qs = CommercialRecord.objects.all().values(
            "invoice_code",
            "client_name",
            "region",
            "product_category",
            "quantity",
            "unit_price",
            "total_amount",
            "tax_amount",
            "transaction_date",
            "status",
        )

        df = pd.DataFrame(list(records_qs))
        count = len(df)

        timestamp_str = timezone.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"reporte_consolidado_{timestamp_str}.xlsx"
        report_path = settings.MEDIA_ROOT / "reports" / report_filename

        if not df.empty:
            generate_styled_excel_report(df, report_path, title=f"Reporte Consolidado al {timezone.now().strftime('%d/%m/%Y %H:%M')}")
            msg = f"Reporte generado con {count} registros en: media/reports/{report_filename}"
        else:
            # Crear un dataframe básico vacío con las columnas para generar la plantilla
            empty_df = pd.DataFrame(
                columns=[
                    "invoice_code", "client_name", "region", "product_category",
                    "quantity", "unit_price", "total_amount", "tax_amount", "transaction_date", "status"
                ]
            )
            generate_styled_excel_report(empty_df, report_path, title="Reporte Consolidado (Sin Datos)")
            msg = f"Reporte vacío generado en: media/reports/{report_filename}"

        duration = round(time.time() - t0, 3)
        log_entry.status = "SUCCESS"
        log_entry.end_time = timezone.now()
        log_entry.duration_seconds = duration
        log_entry.records_processed = count
        log_entry.output_message = msg
        log_entry.save()

        logger.info("%s: %s", job_name, msg)
        return True, msg, count

    except Exception as exc:
        duration = round(time.time() - t0, 3)
        err_msg = f"Fallo al generar reporte consolidado: {str(exc)}"
        log_entry.status = "FAILED"
        log_entry.end_time = timezone.now()
        log_entry.duration_seconds = duration
        log_entry.error_trace = err_msg
        log_entry.save()
        logger.exception(err_msg)
        return False, err_msg, 0
