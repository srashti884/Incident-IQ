"""
IncidentIQ - Recurring Patterns & Fingerprint Routes
"""
from fastapi import APIRouter
from backend.analytics.fingerprint import get_recurring_patterns_analytics, cluster_ad_hoc_incidents
from backend.database.connection import execute_query

router = APIRouter(prefix="/api/patterns", tags=["patterns"])

@router.get("")
def api_list_patterns():
    return {
        "patterns": get_recurring_patterns_analytics()
    }

@router.get("/ad-hoc-clusters")
def api_ad_hoc_clusters(threshold: float = 0.65):
    return {
        "clusters": cluster_ad_hoc_incidents(threshold=threshold)
    }

@router.get("/{pattern_id}/incidents")
def api_pattern_incidents(pattern_id: str):
    sql = """
    SELECT incident_id, title, application, service, severity, status, created_at, resolution_time_minutes, sla_breached
    FROM incidents
    WHERE pattern_id = ?
    ORDER BY created_at DESC;
    """
    rows = execute_query(sql, (pattern_id,))
    return {
        "pattern_id": pattern_id,
        "count": len(rows),
        "incidents": rows
    }
