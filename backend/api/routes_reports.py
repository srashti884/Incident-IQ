"""
IncidentIQ - Reporting API Routes (PDF, Excel, CSV)
"""
from fastapi import APIRouter, Response, HTTPException, Body
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from backend.reporting.pdf_generator import generate_query_result_pdf, generate_general_report_pdf
from backend.reporting.excel_generator import generate_excel_report
from backend.reporting.csv_generator import generate_csv_from_dicts
from backend.database.connection import execute_query

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.post("/query-pdf")
def api_download_query_pdf(query_result: Dict[str, Any] = Body(...)):
    """
    Mandatory Feature: Generates a ReportLab PDF matching the exact current Natural Language query result.
    """
    try:
        pdf_bytes = generate_query_result_pdf(query_result)
        filename = f"IncidentIQ_Query_Result_{query_result.get('view_type', 'report')}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@router.post("/general-pdf")
def api_download_general_pdf(scope: Optional[Dict[str, Any]] = Body(None)):
    """
    Generates a full periodic executive incident audit report PDF via ReportLab.
    """
    try:
        pdf_bytes = generate_general_report_pdf(scope or {})
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="IncidentIQ_Executive_Incident_Report.pdf"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"General PDF report generation failed: {str(e)}")

@router.get("/excel")
def api_download_excel(app: Optional[str] = None):
    try:
        excel_bytes = generate_excel_report(filter_app=app)
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": 'attachment; filename="IncidentIQ_Incident_Analytics.xlsx"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel generation failed: {str(e)}")

class CsvExportRequest(BaseModel):
    records: Optional[List[Dict[str, Any]]] = None
    application: Optional[str] = None

@router.post("/csv")
def api_download_csv(req: CsvExportRequest):
    try:
        if req.records and len(req.records) > 0:
            csv_text = generate_csv_from_dicts(req.records)
        else:
            where_str = " WHERE application = ?" if req.application else ""
            params = (req.application,) if req.application else ()
            rows = execute_query(f"SELECT * FROM incidents{where_str} ORDER BY created_at DESC LIMIT 1000;", params)
            csv_text = generate_csv_from_dicts(rows)
            
        return Response(
            content=csv_text,
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="IncidentIQ_Export.csv"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV generation failed: {str(e)}")
