"""
IncidentIQ - Enterprise PDF Reporting Engine (ReportLab)
Generates high-fidelity, paginated, executive-grade PDF reports locally:
1. Direct Natural Language Query Result PDF (exact active query, KPIs, chart, table)
2. General Enterprise Analytical Report (comprehensive operational audit)
100% local, zero external APIs, zero internet required.
"""
import io
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group
from reportlab.graphics.charts.barcharts import VerticalBarChart

# Corporate Theme Colors
C_PRIMARY = colors.HexColor("#0F172A")    # Deep Navy
C_SECONDARY = colors.HexColor("#2563EB")  # Enterprise Blue
C_ACCENT = colors.HexColor("#0284C7")     # Sky Blue
C_BG_LIGHT = colors.HexColor("#F8FAFC")   # Light Slate
C_BORDER = colors.HexColor("#E2E8F0")     # Subtle Border
C_TEXT_DARK = colors.HexColor("#1E293B")  # Dark Text
C_TEXT_MUTED = colors.HexColor("#64748B") # Muted Text
C_CRITICAL = colors.HexColor("#E11D48")   # Rose/Red
C_WARNING = colors.HexColor("#D97706")    # Amber
C_SUCCESS = colors.HexColor("#16A34A")    # Emerald

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to compute and render total page numbers cleanly in footer.
    """
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(C_TEXT_MUTED)

        # Header
        self.drawString(54, letter[1] - 36, "INCIDENTIQ  |  Operational Incident Analytics & Reporting")
        self.drawRightString(letter[0] - 54, letter[1] - 36, "LOCAL ENTERPRISE INTELLIGENCE")
        self.setStrokeColor(C_BORDER)
        self.setLineWidth(0.5)
        self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Footer
        self.line(54, 45, letter[0] - 54, 45)
        self.drawString(54, 32, "Confidential - For Internal Corporate IT Operations Only")
        self.drawRightString(letter[0] - 54, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def get_styles():
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name="DocTitle",
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=C_PRIMARY,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name="DocSubtitle",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=C_TEXT_MUTED,
        spaceAfter=15
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=C_PRIMARY,
        spaceBefore=12,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name="QueryCallout",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=C_SECONDARY
    ))
    styles.add(ParagraphStyle(
        name="NormalText",
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=C_TEXT_DARK
    ))
    styles.add(ParagraphStyle(
        name="MutedText",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=C_TEXT_MUTED
    ))
    styles.add(ParagraphStyle(
        name="TableHeader",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white
    ))
    styles.add(ParagraphStyle(
        name="TableCell",
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=C_TEXT_DARK
    ))
    styles.add(ParagraphStyle(
        name="TableCellBold",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=C_TEXT_DARK
    ))
    return styles


def generate_query_result_pdf(query_result: Dict[str, Any]) -> bytes:
    """
    Generates a dedicated PDF for the exact currently displayed Natural Language query result.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    styles = get_styles()
    story = []

    # Title & Metadata
    story.append(Paragraph("Incident Analytics Query Report", styles["DocTitle"]))
    gen_time = datetime.now().strftime("%B %d, %Y - %H:%M:%S")
    story.append(Paragraph(f"Generated via Local Warehouse Engine  |  Report Timestamp: {gen_time}", styles["DocSubtitle"]))

    # Original Query Callout Box
    query_text = query_result.get("query", "Incident Query")
    query_box_data = [
        [
            Paragraph("<b>Original User Query:</b>", styles["NormalText"]),
            Paragraph(f"\"{query_text}\"", styles["QueryCallout"])
        ]
    ]
    query_box = Table(query_box_data, colWidths=[120, 384])
    query_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(query_box)
    story.append(Spacer(1, 10))

    # Query Understanding & Execution Metadata
    qu = query_result.get("query_understanding", {})
    entities = qu.get("entities", {})
    
    ent_strs = []
    if entities.get("application"):
        ent_strs.append(f"<b>Application:</b> {entities['application']}")
    if entities.get("service"):
        ent_strs.append(f"<b>Service:</b> {entities['service']}")
    if entities.get("severity"):
        ent_strs.append(f"<b>Severity:</b> {entities['severity']}")
    if entities.get("status"):
        val = entities['status']
        ent_strs.append(f"<b>Status:</b> {', '.join(val) if isinstance(val, list) else val}")
    if not ent_strs:
        ent_strs.append("None (Unconstrained)")

    meta_table_data = [
        [
            Paragraph("<b>Intent:</b>", styles["NormalText"]),
            Paragraph(str(qu.get("intent", "ANALYTICS")), styles["NormalText"]),
            Paragraph("<b>Execution Time:</b>", styles["NormalText"]),
            Paragraph(f"{qu.get('execution_time_ms', 0)} ms", styles["NormalText"])
        ],
        [
            Paragraph("<b>Entities:</b>", styles["NormalText"]),
            Paragraph(" | ".join(ent_strs), styles["NormalText"]),
            Paragraph("<b>Time Range:</b>", styles["NormalText"]),
            Paragraph(str(entities.get("time_range", "All Available History")), styles["NormalText"])
        ],
        [
            Paragraph("<b>Data Source:</b>", styles["NormalText"]),
            Paragraph("Local SQLite Incident Lakehouse", styles["NormalText"]),
            Paragraph("<b>Applied Filters:</b>", styles["NormalText"]),
            Paragraph("; ".join(query_result.get("applied_filters", ["None"])), styles["NormalText"])
        ]
    ]
    meta_table = Table(meta_table_data, colWidths=[90, 162, 90, 162])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # Analytical Summary & KPIs
    story.append(Paragraph("Executive Summary & Key Metrics", styles["SectionHeader"]))
    summary_text = query_result.get("summary", "Query completed successfully.")
    story.append(Paragraph(f"<b>Analytical Finding:</b> {summary_text}", styles["NormalText"]))
    story.append(Spacer(1, 8))

    # KPI Cards Row
    kpis = query_result.get("kpis", {})
    if kpis:
        kpi_items = list(kpis.items())[:4]
        card_cells = []
        for k, v in kpi_items:
            k_clean = k.replace("_", " ").title()
            cell_text = f"<b>{k_clean}</b><br/><font size='14' color='#0F172A'><b>{v:,}</b></font>" if isinstance(v, (int, float)) else f"<b>{k_clean}</b><br/><font size='12' color='#0F172A'><b>{v}</b></font>"
            card_cells.append(Paragraph(cell_text, styles["NormalText"]))
        
        # Pad up to 4 cells
        while len(card_cells) < 4:
            card_cells.append(Paragraph("", styles["NormalText"]))

        kpi_table = Table([card_cells], colWidths=[126, 126, 126, 126])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), C_BG_LIGHT),
            ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 14))

    # Render Visual Chart Flowable if chart_data exists
    chart_data = query_result.get("chart_data", [])
    if chart_data and len(chart_data) > 0:
        story.append(Paragraph("Analytical Distribution", styles["SectionHeader"]))
        
        # Build Vector Bar Chart via ReportLab Graphics
        drawing = Drawing(504, 130)
        drawing.add(Rect(0, 0, 504, 130, fillColor=C_BG_LIGHT, strokeColor=C_BORDER, strokeWidth=0.5))
        
        # Pick top 6 items for clean rendering
        top_items = chart_data[:6]
        x_key = query_result.get("chart_config", {}).get("x_key", "category")
        y_key = query_result.get("chart_config", {}).get("y_key", "count")
        
        bc = VerticalBarChart()
        bc.x = 40
        bc.y = 25
        bc.height = 85
        bc.width = 440
        
        data_series = []
        cat_names = []
        for item in top_items:
            val = item.get(y_key, 0)
            data_series.append(val if isinstance(val, (int, float)) else 0)
            raw_label = str(item.get(x_key, ""))
            cat_names.append(raw_label[:12] + ("." if len(raw_label) > 12 else ""))
            
        bc.data = [data_series]
        bc.categoryAxis.categoryNames = cat_names
        bc.categoryAxis.labels.fontSize = 7
        bc.categoryAxis.labels.fillColor = C_TEXT_DARK
        bc.valueAxis.valueMin = 0
        bc.valueAxis.labels.fontSize = 7
        bc.bars[0].fillColor = C_SECONDARY
        
        drawing.add(bc)
        story.append(drawing)
        story.append(Spacer(1, 14))

    # Results Table
    table_data = query_result.get("table_data", [])
    if table_data:
        story.append(Paragraph(f"Detailed Incident Records ({len(table_data)} rows)", styles["SectionHeader"]))

        # Limit to top 25 rows in PDF for optimal pagination and clarity
        display_rows = table_data[:25]
        view_type = query_result.get("view_type", "incident_list")

        if view_type == "grouped_analytics":
            # Dimension vs Metric Value
            t_rows = [[
                Paragraph("<b>Dimension</b>", styles["TableHeader"]),
                Paragraph("<b>Metric Value</b>", styles["TableHeader"]),
                Paragraph("<b>Total Volume</b>", styles["TableHeader"])
            ]]
            for r in display_rows:
                t_rows.append([
                    Paragraph(str(r.get("dimension", "")), styles["TableCellBold"]),
                    Paragraph(str(r.get("metric_value", "")), styles["TableCell"]),
                    Paragraph(str(r.get("incident_count", "")), styles["TableCell"])
                ])
            col_widths = [240, 132, 132]

        elif view_type == "patterns":
            t_rows = [[
                Paragraph("<b>Pattern ID</b>", styles["TableHeader"]),
                Paragraph("<b>Fingerprint</b>", styles["TableHeader"]),
                Paragraph("<b>Occurrences</b>", styles["TableHeader"]),
                Paragraph("<b>Trend</b>", styles["TableHeader"]),
                Paragraph("<b>Avg Resolution</b>", styles["TableHeader"])
            ]]
            for r in display_rows:
                t_rows.append([
                    Paragraph(str(r.get("pattern_id", "")), styles["TableCellBold"]),
                    Paragraph(str(r.get("fingerprint", "")), styles["TableCell"]),
                    Paragraph(str(r.get("occurrences", "")), styles["TableCell"]),
                    Paragraph(str(r.get("trend", "")), styles["TableCell"]),
                    Paragraph(f"{r.get('avg_resolution_minutes', '')} min", styles["TableCell"])
                ])
            col_widths = [65, 219, 70, 70, 80]

        elif view_type == "root_cause":
            t_rows = [[
                Paragraph("<b>Root Cause Category</b>", styles["TableHeader"]),
                Paragraph("<b>Primary Root Cause Summary</b>", styles["TableHeader"]),
                Paragraph("<b>Incidents</b>", styles["TableHeader"]),
                Paragraph("<b>Avg MTTR</b>", styles["TableHeader"])
            ]]
            for r in display_rows:
                t_rows.append([
                    Paragraph(str(r.get("root_cause_category", "")), styles["TableCellBold"]),
                    Paragraph(str(r.get("root_cause_summary", "")), styles["TableCell"]),
                    Paragraph(str(r.get("incident_count", "")), styles["TableCell"]),
                    Paragraph(f"{r.get('avg_resolution_time', '')} min", styles["TableCell"])
                ])
            col_widths = [120, 244, 70, 70]

        else:
            # Default incident list table
            t_rows = [[
                Paragraph("<b>ID</b>", styles["TableHeader"]),
                Paragraph("<b>Title</b>", styles["TableHeader"]),
                Paragraph("<b>Application</b>", styles["TableHeader"]),
                Paragraph("<b>Severity</b>", styles["TableHeader"]),
                Paragraph("<b>Status</b>", styles["TableHeader"]),
                Paragraph("<b>Created At</b>", styles["TableHeader"])
            ]]
            for r in display_rows:
                sev_str = str(r.get("severity", ""))
                sev_color = "#E11D48" if sev_str == "Critical" else ("#D97706" if sev_str == "High" else "#1E293B")
                t_rows.append([
                    Paragraph(str(r.get("incident_id", "")), styles["TableCellBold"]),
                    Paragraph(str(r.get("title", ""))[:45] + ("..." if len(str(r.get("title", ""))) > 45 else ""), styles["TableCell"]),
                    Paragraph(str(r.get("application", "")), styles["TableCell"]),
                    Paragraph(f"<font color='{sev_color}'><b>{sev_str}</b></font>", styles["TableCell"]),
                    Paragraph(str(r.get("status", "")), styles["TableCell"]),
                    Paragraph(str(r.get("created_at", ""))[:16], styles["TableCell"])
                ])
            col_widths = [55, 175, 124, 50, 45, 55]

        pdf_table = Table(t_rows, colWidths=col_widths, repeatRows=1)
        pdf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, C_BG_LIGHT]),
            ('BOX', (0, 0), (-1, -1), 0.5, C_BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ]))
        story.append(pdf_table)

        if len(table_data) > 25:
            story.append(Spacer(1, 4))
            story.append(Paragraph(f"<i>Showing top 25 of {len(table_data)} total matching records. Full export available via CSV.</i>", styles["MutedText"]))

    # Build the PDF using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()


def generate_general_report_pdf(report_scope: Dict[str, Any] = None) -> bytes:
    """
    Generates a comprehensive executive periodic incident audit report.
    """
    from backend.analytics.dashboard import get_dashboard_data
    from backend.analytics.what_changed import compute_what_changed

    dash_data = get_dashboard_data()
    changed_data = compute_what_changed()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    styles = get_styles()
    story = []

    # Title & Metadata
    story.append(Paragraph("Enterprise Operational Incident Audit Report", styles["DocTitle"]))
    gen_time = datetime.now().strftime("%B %d, %Y - %H:%M:%S")
    story.append(Paragraph(f"IncidentIQ Local Analytical Intelligence  |  Audit Timestamp: {gen_time}", styles["DocSubtitle"]))

    # KPI Summary Section
    story.append(Paragraph("Key Performance Indicators (Current Portfolio)", styles["SectionHeader"]))
    k = dash_data.get("kpis", {})
    kpi_cards = [
        Paragraph(f"<b>Total Volume</b><br/><font size='14'><b>{k.get('total_incidents', 0):,}</b></font>", styles["NormalText"]),
        Paragraph(f"<b>Open Tickets</b><br/><font size='14' color='#D97706'><b>{k.get('open_incidents', 0):,}</b></font>", styles["NormalText"]),
        Paragraph(f"<b>Critical (P1)</b><br/><font size='14' color='#E11D48'><b>{k.get('critical_incidents', 0):,}</b></font>", styles["NormalText"]),
        Paragraph(f"<b>SLA Breaches</b><br/><font size='14'><b>{k.get('sla_breaches', 0):,} ({k.get('sla_breach_rate', 0)}%)</b></font>", styles["NormalText"]),
    ]
    kpi_table = Table([kpi_cards], colWidths=[126, 126, 126, 126])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    # What Changed Highlights
    story.append(Paragraph("Operational Velocity: What Changed Since Yesterday?", styles["SectionHeader"]))
    insights = changed_data.get("insights", [])
    bullet_data = [[Paragraph(f"• {ins}", styles["NormalText"])] for ins in insights]
    bullet_table = Table(bullet_data, colWidths=[504])
    bullet_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(bullet_table)
    story.append(Spacer(1, 14))

    # Application Breakdown Table
    story.append(Paragraph("Portfolio Health by Application Tier", styles["SectionHeader"]))
    app_data = dash_data.get("incidents_by_application", [])
    app_rows = [[
        Paragraph("<b>Application</b>", styles["TableHeader"]),
        Paragraph("<b>Total Incidents</b>", styles["TableHeader"]),
        Paragraph("<b>Critical P1</b>", styles["TableHeader"]),
        Paragraph("<b>SLA Breaches</b>", styles["TableHeader"])
    ]]
    for r in app_data:
        app_rows.append([
            Paragraph(str(r.get("application", "")), styles["TableCellBold"]),
            Paragraph(str(r.get("incident_count", "")), styles["TableCell"]),
            Paragraph(str(r.get("critical_count", "")), styles["TableCell"]),
            Paragraph(str(r.get("sla_breaches", "")), styles["TableCell"])
        ])
    app_table = Table(app_rows, colWidths=[204, 100, 100, 100], repeatRows=1)
    app_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, C_BG_LIGHT]),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
    ]))
    story.append(app_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()
