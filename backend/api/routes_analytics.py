"""
IncidentIQ - Analytics API Routes
"""
from fastapi import APIRouter
from backend.analytics.dashboard import get_dashboard_data
from backend.analytics.what_changed import compute_what_changed
from backend.analytics.impact_matrix import get_impact_vs_severity_matrix
from backend.database.connection import get_warehouse_stats

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/dashboard")
def api_dashboard():
    return get_dashboard_data()

@router.get("/what-changed")
def api_what_changed():
    return compute_what_changed()

@router.get("/impact-matrix")
def api_impact_matrix(limit: int = 150):
    return get_impact_vs_severity_matrix(limit=limit)

@router.get("/system-status")
def api_system_status():
    return get_warehouse_stats()
