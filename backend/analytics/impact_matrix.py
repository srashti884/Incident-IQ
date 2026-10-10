"""
IncidentIQ - Impact vs Severity Matrix Analytics
Calculates and plots Operational Impact Score vs Severity Level.
"""
from typing import Dict, Any, List
from backend.database.connection import execute_query

SEV_MAP = {
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Critical": 4
}

def get_impact_vs_severity_matrix(limit: int = 150) -> Dict[str, Any]:
    sql = f"""
    SELECT 
        incident_id,
        title,
        application,
        service,
        severity,
        impact_score,
        sla_breached,
        resolution_time_minutes,
        created_at
    FROM incidents
    ORDER BY created_at DESC
    LIMIT {limit};
    """
    rows = execute_query(sql)

    points = []
    for r in rows:
        points.append({
            "incident_id": r["incident_id"],
            "title": r["title"][:60] + ("..." if len(r["title"]) > 60 else ""),
            "application": r["application"],
            "service": r["service"],
            "severity": r["severity"],
            "severity_level": SEV_MAP.get(r["severity"], 2),
            "impact_score": r["impact_score"],
            "sla_breached": r["sla_breached"],
            "resolution_time": r["resolution_time_minutes"] or 0
        })

    formula_explanation = (
        "Calculated Impact Score (1-100) is derived deterministically from: "
        "Base Severity Weight (40%) + SLA Breach Penalty (20%) + "
        "Application Infrastructure Tier (20%) + Resolution Duration Weight (20%)."
    )

    return {
        "points": points,
        "formula": formula_explanation,
        "severity_labels": ["Low", "Medium", "High", "Critical"],
        "total_analyzed": len(points)
    }
