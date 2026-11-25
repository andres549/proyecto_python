"""
Pruebas de integración del flujo ETL y las tareas de automatización con APScheduler.
"""

import pytest
import io
import pandas as pd
from django.core.files.base import ContentFile
from apps.documents.models import UploadedDocument, CommercialRecord
from apps.documents.services import process_document_etl
from apps.automations.models import ExecutionLog
from apps.automations.tasks import (
    task_audit_pending_documents,
    task_generate_daily_consolidated_report,
)


@pytest.mark.django_db
def test_full_etl_lifecycle():
    """Valida la carga, validación e inserción de datos en la base de datos relacional."""
    df_sample = pd.DataFrame({
        "codigo_factura": ["FAC-TEST-001", "FAC-TEST-002"],
        "cliente": ["Corporación Test", "Servicios Integrados"],
        "region": ["Centro", "Occidente"],
        "categoria_producto": ["Consultoría", "Hardware"],
        "cantidad": [4, 2],
        "precio_unitario": [250.0, 500.0],
        "fecha_transaccion": ["2026-02-01", "2026-02-02"],
        "estado": ["Pagada", "Pendiente"],
    })

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_sample.to_excel(writer, index=False)

    doc = UploadedDocument(
        filename="test_dataset.xlsx",
        file_type="XLSX",
        file_size_bytes=len(buffer.getvalue()),
        status="PENDING",
    )
    doc.file.save("test_dataset.xlsx", ContentFile(buffer.getvalue()))
    doc.save()

    # Ejecutar ETL
    success, msg = process_document_etl(doc)

    assert success is True
    doc.refresh_from_db()
    assert doc.status == "COMPLETED"
    assert doc.row_count == 2

    # Verificar que los registros existan en la tabla CommercialRecord
    records = CommercialRecord.objects.filter(document=doc)
    assert records.count() == 2
    assert records.first().total_amount == 1000.0


@pytest.mark.django_db
def test_automation_tasks():
    """Valida que las tareas programadas se ejecuten y generen registros de auditoría."""
    success, msg, count = task_audit_pending_documents(trigger="MANUAL")
    assert success is True

    # Verificar log de auditoría
    last_log = ExecutionLog.objects.first()
    assert last_log is not None
    assert last_log.status == "SUCCESS"

    # Probar generación de reporte diario
    success_rep, msg_rep, count_rep = task_generate_daily_consolidated_report(trigger="MANUAL")
    assert success_rep is True
