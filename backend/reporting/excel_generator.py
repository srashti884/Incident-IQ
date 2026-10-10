"""
IncidentIQ - Enterprise Excel Export Engine (OpenPyXL)
Generates multi-sheet styled Excel workbooks locally:
- Executive Summary Sheet
- Detailed Incidents Sheet
- Application Tier Analysis Sheet
- Recurring Patterns Sheet
"""
import io
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from typing import Dict, Any, List
from backend.database.connection import execute_query

def generate_excel_report(filter_app: str = None) -> bytes:
    wb = openpyxl.Workbook()
    # Sheet 1: Incidents
    ws_inc = wb.active
    ws_inc.title = "Incident Records"

    # Sheet 2: Application Summary
    ws_app = wb.create_sheet(title="Application Summary")

    # Sheet 3: Recurring Patterns
    ws_pat = wb.create_sheet(title="Recurring Patterns")

    # Styling definitions
    header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    bold_font = Font(name="Calibri", size=10, bold=True)
    regular_font = Font(name="Calibri", size=10)
    thin_border = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )

    # 1. Fill Incidents Sheet
    where_str = " WHERE application = ?" if filter_app else ""
    params = (filter_app,) if filter_app else ()
    inc_sql = f"""
    SELECT incident_id, title, application, service, severity, priority, status,
           created_at, resolved_at, resolution_time_minutes, sla_breached, root_cause_category, impact_score
    FROM incidents
    {where_str}
    ORDER BY created_at DESC;
    """
    incidents = execute_query(inc_sql, params)

    headers = [
        "Incident ID", "Title", "Application", "Service", "Severity", "Priority",
        "Status", "Created At", "Resolved At", "Resolution (Min)", "SLA Breached",
        "Root Cause Category", "Impact Score"
    ]
    ws_inc.append(headers)

    for col_num in range(1, len(headers) + 1):
        cell = ws_inc.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for inc in incidents:
        ws_inc.append([
            inc["incident_id"],
            inc["title"],
            inc["application"],
            inc["service"],
            inc["severity"],
            inc["priority"],
            inc["status"],
            inc["created_at"],
            inc["resolved_at"] or "N/A",
            inc["resolution_time_minutes"] or 0,
            "YES" if inc["sla_breached"] == 1 else "NO",
            inc["root_cause_category"],
            inc["impact_score"]
        ])

    for row in ws_inc.iter_rows(min_row=2, max_row=len(incidents) + 1, min_col=1, max_col=len(headers)):
        for cell in row:
            cell.font = regular_font
            cell.border = thin_border

    # Auto-fit columns
    for col in ws_inc.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_inc.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 50)

    # 2. Fill Application Summary
    app_headers = ["Application", "Total Incidents", "Critical Incidents", "SLA Breaches", "MTTR (Min)"]
    ws_app.append(app_headers)
    for col_num in range(1, len(app_headers) + 1):
        cell = ws_app.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font

    app_sql = """
    SELECT application, COUNT(*) as count,
           SUM(CASE WHEN severity = 'Critical' THEN 1 ELSE 0 END) as critical,
           SUM(CASE WHEN sla_breached = 1 THEN 1 ELSE 0 END) as breaches,
           ROUND(AVG(resolution_time_minutes), 1) as mttr
    FROM incidents
    GROUP BY application
    ORDER BY count DESC;
    """
    for r in execute_query(app_sql):
        ws_app.append([r["application"], r["count"], r["critical"], r["breaches"], r["mttr"] or 0])

    for row in ws_app.iter_rows(min_row=2, max_col=len(app_headers)):
        for cell in row:
            cell.font = regular_font
            cell.border = thin_border

    for col in ws_app.columns:
        col_letter = get_column_letter(col[0].column)
        ws_app.column_dimensions[col_letter].width = 25

    # 3. Fill Patterns
    pat_headers = ["Pattern ID", "Fingerprint", "Application", "Service", "Occurrences", "Trend", "Possible Root Cause"]
    ws_pat.append(pat_headers)
    for col_num in range(1, len(pat_headers) + 1):
        cell = ws_pat.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font

    for r in execute_query("SELECT * FROM recurring_patterns ORDER BY occurrences DESC;"):
        ws_pat.append([
            r["pattern_id"], r["fingerprint"], r["application"], r["service"],
            r["occurrences"], r["trend"], r["possible_root_cause"]
        ])

    for row in ws_pat.iter_rows(min_row=2, max_col=len(pat_headers)):
        for cell in row:
            cell.font = regular_font
            cell.border = thin_border

    for col in ws_pat.columns:
        col_letter = get_column_letter(col[0].column)
        ws_pat.column_dimensions[col_letter].width = 30

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
