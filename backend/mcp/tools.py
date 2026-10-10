"""
IncidentIQ - Local MCP Data Access Layer (Tool Registry)
Implements lightweight, decoupled local MCP-style tools operating strictly
on local SQLite warehouse data without any external dependencies.
"""
from typing import Dict, Any, List, Optional
from backend.database.connection import execute_query

def get_incident_schema() -> Dict[str, Any]:
    """
    Returns the analytical schema, column types, and descriptions of the local warehouse.
    """
    columns_sql = "PRAGMA table_info(incidents);"
    cols = execute_query(columns_sql)
    
    schema_definition = {
        table_name: execute_query(f"PRAGMA table_info({table_name});")
        for table_name in ["incidents", "applications", "services", "recurring_patterns"]
    }
    return {
        "tool": "get_incident_schema",
        "description": "Provides table definitions, columns, primary keys and types for IncidentIQ SQLite warehouse.",
        "tables": schema_definition
    }

def search_incidents(
    query: Optional[str] = None,
    application: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    sla_breached: Optional[int] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Searches and filters incident records locally.
    """
    where_parts = []
    params = []

    if query:
        where_parts.append("(title LIKE ? OR description LIKE ? OR incident_id LIKE ?)")
        param_val = f"%{query}%"
        params.extend([param_val, param_val, param_val])
    if application:
        where_parts.append("application = ?")
        params.append(application)
    if severity:
        where_parts.append("severity = ?")
        params.append(severity)
    if status:
        where_parts.append("status = ?")
        params.append(status)
    if sla_breached is not None:
        where_parts.append("sla_breached = ?")
        params.append(int(sla_breached))

    where_str = (" WHERE " + " AND ".join(where_parts)) if where_parts else ""

    # Count total
    count_sql = f"SELECT COUNT(*) as total FROM incidents{where_str};"
    total_rows = execute_query(count_sql, tuple(params))
    total_count = total_rows[0]["total"] if total_rows else 0

    # Paged query
    paged_sql = f"""
    SELECT incident_id, title, application, service, severity, priority, status,
           created_at, resolved_at, resolution_time_minutes, sla_breached, root_cause_category, impact_score
    FROM incidents
    {where_str}
    ORDER BY created_at DESC
    LIMIT ? OFFSET ?;
    """
    paged_params = list(params) + [limit, offset]
    results = execute_query(paged_sql, tuple(paged_params))

    return {
        "tool": "search_incidents",
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "results": results
    }

def get_incident_metrics(time_range: Optional[str] = None, application: Optional[str] = None) -> Dict[str, Any]:
    """
    Calculates summary metrics: total volume, critical ratio, SLA breaches, and MTTR.
    """
    where_parts = []
    params = []

    if application:
        where_parts.append("application = ?")
        params.append(application)
    
    where_str = (" WHERE " + " AND ".join(where_parts)) if where_parts else ""

    sql = f"""
    SELECT 
        COUNT(*) as total_incidents,
        SUM(CASE WHEN severity = 'Critical' THEN 1 ELSE 0 END) as critical_count,
        SUM(CASE WHEN sla_breached = 1 THEN 1 ELSE 0 END) as sla_breaches,
        ROUND(AVG(resolution_time_minutes), 1) as avg_resolution_time,
        ROUND(AVG(impact_score), 1) as avg_impact_score
    FROM incidents
    {where_str};
    """
    rows = execute_query(sql, tuple(params))
    return {
        "tool": "get_incident_metrics",
        "scope": {"application": application, "time_range": time_range},
        "metrics": rows[0] if rows else {}
    }

def get_application_metrics() -> Dict[str, Any]:
    """
    Returns breakdown metrics grouped by application tier and volume.
    """
    sql = """
    SELECT 
        a.app_id,
        a.name as application,
        a.tier,
        a.criticality,
        COUNT(i.incident_id) as incident_count,
        SUM(CASE WHEN i.severity = 'Critical' THEN 1 ELSE 0 END) as critical_count,
        SUM(CASE WHEN i.sla_breached = 1 THEN 1 ELSE 0 END) as sla_breaches,
        ROUND(AVG(i.resolution_time_minutes), 1) as avg_resolution_time
    FROM applications a
    LEFT JOIN incidents i ON a.name = i.application
    GROUP BY a.app_id, a.name, a.tier, a.criticality
    ORDER BY incident_count DESC;
    """
    rows = execute_query(sql)
    return {
        "tool": "get_application_metrics",
        "total_applications": len(rows),
        "applications": rows
    }

def get_trend_metrics(interval: str = "daily", days: int = 30) -> Dict[str, Any]:
    """
    Returns time-series incident trends.
    """
    sql = """
    SELECT 
        SUBSTR(created_at, 1, 10) as date_interval,
        COUNT(*) as incident_count,
        SUM(CASE WHEN severity = 'Critical' THEN 1 ELSE 0 END) as critical_count,
        SUM(CASE WHEN sla_breached = 1 THEN 1 ELSE 0 END) as sla_breaches
    FROM incidents
    GROUP BY date_interval
    ORDER BY date_interval DESC
    LIMIT ?;
    """
    rows = execute_query(sql, (days,))
    rows.reverse()
    return {
        "tool": "get_trend_metrics",
        "interval": interval,
        "points": rows
    }

def get_recurring_patterns() -> Dict[str, Any]:
    """
    Retrieves recurring pattern profiles and fingerprints.
    """
    sql = """
    SELECT * FROM recurring_patterns ORDER BY occurrences DESC;
    """
    rows = execute_query(sql)
    return {
        "tool": "get_recurring_patterns",
        "patterns_count": len(rows),
        "patterns": rows
    }

def get_root_cause_context(application: Optional[str] = None) -> Dict[str, Any]:
    """
    Aggregates root-cause categories and specific incident summaries.
    """
    where_clause = "WHERE application = ?" if application else ""
    params = (application,) if application else ()

    sql = f"""
    SELECT 
        root_cause_category,
        root_cause_summary,
        COUNT(*) as count,
        ROUND(AVG(resolution_time_minutes), 1) as avg_resolution
    FROM incidents
    {where_clause}
    GROUP BY root_cause_category, root_cause_summary
    ORDER BY count DESC
    LIMIT 15;
    """
    rows = execute_query(sql, params)
    return {
        "tool": "get_root_cause_context",
        "application_filter": application,
        "root_causes": rows
    }
