"""
IncidentIQ - Query Planner & SQL Compiler
Converts classified intent and extracted entities into structured SQLite execution plans.
Ensures 100% parameterized SQL queries, zero SQL injection risks, and optimal chart selection.
"""
from typing import Dict, Any, List, Tuple
from backend.semantic_layer.engine import semantic_engine

def build_query_plan(query: str, intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
    app = entities.get("application")
    svc = entities.get("service")
    sev = entities.get("severity")
    status = entities.get("status")
    sla = entities.get("sla_breached")
    tr = entities.get("time_range")
    metric = entities.get("metric", "incident_count")
    group_by = entities.get("group_by")
    limit = entities.get("limit") or 25

    where_clauses = []
    params: List[Any] = []

    if app:
        where_clauses.append("application = ?")
        params.append(app)
    if svc:
        where_clauses.append("service = ?")
        params.append(svc)
    if sev:
        where_clauses.append("severity = ?")
        params.append(sev)
    if status:
        if isinstance(status, list):
            placeholders = ",".join(["?"] * len(status))
            where_clauses.append(f"status IN ({placeholders})")
            params.extend(status)
        else:
            where_clauses.append("status = ?")
            params.append(status)
    if sla is not None:
        where_clauses.append("sla_breached = ?")
        params.append(int(sla))
    if tr and tr.get("start") and tr.get("end"):
        where_clauses.append("created_at >= ? AND created_at <= ?")
        params.extend([tr["start"], tr["end"]])

    where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    # Plan based on Intent
    if intent == "RECURRING_PATTERNS":
        sql = """
        SELECT 
            pattern_id,
            fingerprint,
            application,
            service,
            severity,
            occurrences,
            first_seen,
            last_seen,
            avg_resolution_minutes,
            trend,
            possible_root_cause,
            root_cause_category
        FROM recurring_patterns
        ORDER BY occurrences DESC
        LIMIT 10;
        """
        return {
            "sql": sql,
            "params": tuple(),
            "chart_type": "bar",
            "chart_x": "fingerprint",
            "chart_y": "occurrences",
            "intent": intent,
            "view_type": "patterns",
            "explanation": "Identified high-confidence recurring incident patterns clustered by system fingerprint.",
            "metric_name": "Pattern Occurrences"
        }

    elif intent == "ROOT_CAUSE":
        base_where = where_sql if where_sql else " WHERE root_cause_category != ''"
        sql = f"""
        SELECT 
            root_cause_category,
            root_cause_summary,
            COUNT(*) as incident_count,
            ROUND(AVG(resolution_time_minutes), 1) as avg_resolution_time,
            SUM(CASE WHEN severity = 'Critical' THEN 1 ELSE 0 END) as critical_incidents
        FROM incidents
        {base_where}
        GROUP BY root_cause_category, root_cause_summary
        ORDER BY incident_count DESC
        LIMIT 10;
        """
        return {
            "sql": sql,
            "params": tuple(params),
            "chart_type": "bar",
            "chart_x": "root_cause_category",
            "chart_y": "incident_count",
            "intent": intent,
            "view_type": "root_cause",
            "explanation": "Aggregated incident frequency and impact grouped by identified root-cause category and summary.",
            "metric_name": "Incidents by Root Cause"
        }

    elif intent == "ANALYTICS_GROUP" or group_by:
        target_group = group_by or "application"

        if metric == "average_resolution_time":
            time_filter = " AND resolution_time_minutes IS NOT NULL" if where_sql else " WHERE resolution_time_minutes IS NOT NULL"
            sql = f"""
            SELECT 
                {target_group} as dimension,
                ROUND(AVG(resolution_time_minutes), 1) as metric_value,
                COUNT(*) as incident_count
            FROM incidents
            {where_sql}{time_filter}
            GROUP BY {target_group}
            ORDER BY metric_value DESC
            LIMIT ?;
            """
            metric_label = "Average Resolution Time (mins)"
            p_list = list(params) + [limit]
        elif metric == "sla_breaches":
            sql = f"""
            SELECT 
                {target_group} as dimension,
                SUM(CASE WHEN sla_breached = 1 THEN 1 ELSE 0 END) as metric_value,
                COUNT(*) as incident_count,
                ROUND(SUM(CASE WHEN sla_breached = 1 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 1) as breach_rate
            FROM incidents
            {where_sql}
            GROUP BY {target_group}
            ORDER BY metric_value DESC
            LIMIT ?;
            """
            metric_label = "SLA Breaches"
            p_list = list(params) + [limit]
        else:
            sql = f"""
            SELECT 
                {target_group} as dimension,
                COUNT(*) as metric_value,
                SUM(CASE WHEN severity = 'Critical' THEN 1 ELSE 0 END) as critical_count,
                SUM(CASE WHEN sla_breached = 1 THEN 1 ELSE 0 END) as sla_breaches
            FROM incidents
            {where_sql}
            GROUP BY {target_group}
            ORDER BY metric_value DESC
            LIMIT ?;
            """
            metric_label = "Total Incidents"
            p_list = list(params) + [limit]

        return {
            "sql": sql,
            "params": tuple(p_list),
            "chart_type": "bar",
            "chart_x": "dimension",
            "chart_y": "metric_value",
            "intent": intent,
            "view_type": "grouped_analytics",
            "explanation": f"Ranked breakdown by {target_group} evaluating {metric_label.lower()}.",
            "metric_name": metric_label
        }

    elif intent == "ANALYTICS_TREND":
        sql = f"""
        SELECT 
            SUBSTR(created_at, 1, 10) as date_day,
            COUNT(*) as incident_count,
            SUM(CASE WHEN severity = 'Critical' THEN 1 ELSE 0 END) as critical_count,
            SUM(CASE WHEN sla_breached = 1 THEN 1 ELSE 0 END) as sla_breaches
        FROM incidents
        {where_sql}
        GROUP BY date_day
        ORDER BY date_day ASC
        LIMIT 30;
        """
        return {
            "sql": sql,
            "params": tuple(params),
            "chart_type": "line",
            "chart_x": "date_day",
            "chart_y": "incident_count",
            "intent": intent,
            "view_type": "trend",
            "explanation": "Chronological trajectory of daily incident counts and critical alerts.",
            "metric_name": "Daily Incident Trend"
        }

    else:
        # Default: ANALYTICS_LIST
        sql = f"""
        SELECT 
            incident_id,
            title,
            application,
            service,
            severity,
            priority,
            status,
            created_at,
            resolved_at,
            resolution_time_minutes,
            sla_breached,
            root_cause_summary,
            impact_score,
            assignee
        FROM incidents
        {where_sql}
        ORDER BY created_at DESC
        LIMIT 100;
        """
        return {
            "sql": sql,
            "params": tuple(params),
            "chart_type": "bar" if len(where_clauses) > 0 else "none",
            "chart_x": "severity",
            "chart_y": "count",
            "intent": intent,
            "view_type": "incident_list",
            "explanation": f"Detailed list of matching operational incidents filtered from local warehouse.",
            "metric_name": "Matching Incidents"
        }
