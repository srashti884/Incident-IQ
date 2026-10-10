"""
IncidentIQ - Incident Explorer & Story Drill-down Routes
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from backend.mcp.tools import search_incidents
from backend.analytics.incident_story import get_incident_story
from backend.database.connection import execute_query

router = APIRouter(prefix="/api/incidents", tags=["incidents"])

@router.get("")
def api_list_incidents(
    q: Optional[str] = Query(None, description="Free text search term"),
    application: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sla_breached: Optional[int] = Query(None),
    limit: int = Query(25, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    return search_incidents(
        query=q,
        application=application,
        severity=severity,
        status=status,
        sla_breached=sla_breached,
        limit=limit,
        offset=offset
    )

@router.get("/filters")
def api_get_filter_options():
    apps = execute_query("SELECT DISTINCT name FROM applications ORDER BY name;")
    sevs = ["Critical", "High", "Medium", "Low"]
    statuses = ["Open", "In Progress", "Resolved", "Closed"]
    return {
        "applications": [a["name"] for a in apps],
        "severities": sevs,
        "statuses": statuses
    }

@router.get("/{incident_id}/story")
def api_get_incident_story(incident_id: str):
    story = get_incident_story(incident_id)
    if not story:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return story
