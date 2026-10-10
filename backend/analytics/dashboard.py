"""
IncidentIQ - Dashboard Analytics Engine
Aggregates real-time KPIs and chart metrics from local SQLite warehouse.
100% database-backed, zero dummy values.
"""
from typing import Dict, Any, List
from backend.database.connection import execute_query

def get_dashboard_data() -> Dict[str, Any]:
    # 1. Primary KPIs
    kpi_sql = """
    SELECT 
        COUNT(*) as total_incidents,
        SUM(CASE WHEN status IN ('Open', 'In Progress') THEN 1 ELSE 0 END) as open_incidents,
        SUM(CASE WHEN severity = 'Critical' THEN 1 ELSE 0 END) as critical_incidents,
        SUM(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) as resolved_incidents,
        SUM(CASE WHEN sla_breached = 1 THEN 1 ELSE 0 END) as sla_breaches,
        ROUND(AVG(resolution_time_minutes), 1) as avg_resolution_time,
        ROUND(SUM(CASE WHEN sla_breached = 1 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 1) as sla_breach_rate
    FROM incidents;
    """
    kpi_rows = execute_query(kpi_sql)
    kpi = kpi_rows[0] if kpi_rows else {}

    # 2. Incidents by Severity
    sev_sql = """
    SELECT severity, COUNT(*) as count
    FROM incidents
    GROUP BY severity
    ORDER BY 
        CASE severity 
            WHEN 'Critical' THEN 1 
            WHEN 'High' THEN 2 
            WHEN 'Medium' THEN 3 
            WHEN 'Low' THEN 4 
            ELSE 5 
        END;
    """
    sev_data = execute_query(sev_sql)

    # 3. Incidents by Application
    app_sql = """
    SELECT application, COUNT(*) as incident_count,
           SUM(CASE WHEN severity = 'Critical' THEN 1 ELSE 0 END) as critical_count,
           SUM(CASE WHEN sla_breached = 1 THEN 1 ELSE 0 END) as sla_breaches
    FROM incidents
    GROUP BY application
    ORDER BY incident_count DESC;
    """
    app_data = execute_query(app_sql)

    # 4. Incidents by Status
    status_sql = """
    SELECT status, COUNT(*) as count
    FROM incidents
    GROUP BY status
    ORDER BY count DESC;
    """
    status_data = execute_query(status_sql)

    # 5. Incident Trend Over Time (Last 30 Days)
    trend_sql = """
    SELECT 
        SUBSTR(created_at, 1, 10) as date_day,
        COUNT(*) as total,
        SUM(CASE WHEN severity = 'Critical' THEN 1 ELSE 0 END) as critical,
        SUM(CASE WHEN sla_breached = 1 THEN 1 ELSE 0 END) as sla_breaches
    FROM incidents
    WHERE created_at >= date('2026-09-22', '-30 days')
    GROUP BY date_day
    ORDER BY date_day ASC;
    """
    trend_data = execute_query(trend_sql)

    # 6. SLA Breaches Trend (Weekly)
    sla_trend_sql = """
    SELECT 
        SUBSTR(created_at, 1, 10) as date_day,
        SUM(CASE WHEN sla_breached = 1 THEN 1 ELSE 0 END) as breaches,
        ROUND(AVG(resolution_time_minutes), 1) as avg_resolution
    FROM incidents
    WHERE created_at >= date('2026-09-22', '-30 days')
    GROUP BY date_day
    ORDER BY date_day ASC;
    """
    sla_trend_data = execute_query(sla_trend_sql)

    return {
        "kpis": {
            "total_incidents": kpi.get("total_incidents", 0),
            "open_incidents": kpi.get("open_incidents", 0),
            "critical_incidents": kpi.get("critical_incidents", 0),
            "resolved_incidents": kpi.get("resolved_incidents", 0),
            "sla_breaches": kpi.get("sla_breaches", 0),
            "avg_resolution_time": kpi.get("avg_resolution_time", 0),
            "sla_breach_rate": kpi.get("sla_breach_rate", 0)
        },
        "incidents_by_severity": sev_data,
        "incidents_by_application": app_data,
        "incidents_by_status": status_data,
        "trend_over_time": trend_data,
        "sla_trend": sla_trend_data
    }
